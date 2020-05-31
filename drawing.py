import math
import gpu
from gpu_extras.batch import batch_for_shader
from bpy.types import WindowManager
from bpy_extras.view3d_utils import location_3d_to_region_2d
import bmesh
from mathutils import Vector
import blf
from collections import defaultdict

from . import props
from . import solver


def equals(value, ref):
    return ref - solver.EPSILON < value and value < ref + solver.EPSILON


def draw_text(font_id, x, y, label, color):
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, label)
    return blf.dimensions(font_id, label)


class BatchDrawing:
    def __init__(self, verts, obj):
        # object on which I draw
        self.obj = obj
        # points index -> co
        self.points = {v.index:v.co for v in verts}
        # edge (point0, point1) -> [(label, color), ...]
        self.edges_label = defaultdict(list)
        # vertex (point) -> [(label, color), ...]
        self.vertices_label = defaultdict(list)

    def add_edge_label(self, edge, label, color):
        """Add a label on edge
        - edge : tuple of (point0_3d, point1_3d) making the edge
        - label : label of the edge
        - color : color of the label"""
        # Sort vertices index min - max
        p0, p1 = edge
        p0, p1 = min(p0, p1), max(p0, p1)
        self.edges_label[(p0, p1)].append((label, color))

    def add_point_label(self, point, label, color):
        """Add a label on point
        - point : 3d point
        - label : label of the edge
        - color : color of the label"""
        self.vertices_label[point].append((label, color))

    def _world_point(self, point_3d):
        """Transform a 3D point from the mesh to a 3D point of the world
        by multiplying with the matrix world
        point_3d: 3D point of the object's mesh"""
        return self.obj.matrix_world @ point_3d

    def draw(self, context):
        region = context.region
        rv3d = context.space_data.region_3d
        o = context.edit_object

        font_id = 0
        blf.size(font_id, FONT_SIZE, 72)

        # First edges
        for (p0, p1), datas in self.edges_label.items():
            p0_3d, p1_3d = self._world_point(self.points[p0]), self._world_point(self.points[p1])
            # This edge in 2d
            p0_2d = location_3d_to_region_2d(region, rv3d, p0_3d)
            p1_2d = location_3d_to_region_2d(region, rv3d, p1_3d)
            if p0_2d is None or p1_2d is None:
                # not in view
                # TODO should I do something when one of the points is in view ?
                continue
            # Vector in 3d and 2d
            v_3d = p1_3d - p0_3d
            v_2d = p1_2d - p0_2d

            # normal vector to v_3d pointing to outside of the object already
            # normalized multiply to 1/10 of v_3d length so it hopefully stays in view
            vn_3d = _normal_vector(o, p0_3d, p1_3d) * v_3d.length / 10

            # Projected point on normal vector from p0_3d
            p0_n_2d = location_3d_to_region_2d(region, rv3d, p0_3d + vn_3d)
            if p0_n_2d is None:
                # Not in view
                continue

            # Now the point on (p0_2d - p0_n_2d) vector so (p0_n0_2d - p0_2d).length == EDGE_CONSTRAINT_SPACING
            p0_n0_2d = p0_2d.lerp(p0_n_2d, EDGE_CONSTRAINT_SPACING / (p0_n_2d - p0_2d).length)

            # Keep p0_n0_2d - p1_n0_2d parallel to p0_2d - p1_2d
            p1_n0_2d = p0_n0_2d + v_2d

            # Middle of this displaced edge
            p_n0_middle = p0_n0_2d.lerp(p1_n0_2d, 0.5)

            # The whole label width
            whole_label = "-".join([d[0] for d in datas])
            width_whole_label, height_whole_label = blf.dimensions(font_id, whole_label)

            x = p_n0_middle[0] - width_whole_label / 2
            y = p_n0_middle[1] - height_whole_label / 2

            # Now draw each label
            # TODO if same color, batch draw_text ?
            for i, (label, color) in enumerate(datas):
                if i > 0:
                    # draw a "-" between label
                    w,h = draw_text(font_id, x, y, "-", COLOR_OK)
                    x += w
                # Draw the label
                w,h = draw_text(font_id, x, y, label, color)
                x += w

        # And now vertices
        for p, datas in self.vertices_label.items():
            point_3d = self.points[p]
            world_point_3d = self._world_point(point_3d)
            world_point_2d = location_3d_to_region_2d(region, rv3d, world_point_3d)

            if world_point_2d is None:
                # Not in view
                continue

            x = world_point_2d[0] + 1.5 * VERTEX_BOX_MARGIN
            y = world_point_2d[1] - VERTEX_BOX_MARGIN

            # Now draw each label
            # TODO if same color, batch draw_text ?
            for i, (label, color) in enumerate(datas):
                if i > 0:
                    # draw a "-" between label
                    w,h = draw_text(font_id, x, y, "-", COLOR_OK)
                    x += w
                # Draw the label
                w,h = draw_text(font_id, x, y, label, color)
                x += w


def draw_constraints_definition(context):
    if not WindowManager.mesh_constraints_draw_constraints_definition:
        # No drawing for me
        return
    if context.space_data.region_quadviews:
        # OMG quad view, not supported for now
        return
    o = context.edit_object
    if o is None:
        # Nothing in edit mode
        return
    if "MeshConstraintGenerator" not in o:
        # no constraints here
        return
    if context.region is None:
        # no region ? maybe in render ?
        return
    if context.space_data.region_3d is None:
        # no region_3d ? maybe in render or in non 3d view ?
        return

    bm = bmesh.from_edit_mesh(o.data)
    mc = props.MeshConstraints(o.MeshConstraintGenerator)
    batch = BatchDrawing(bm.verts, o)

    for c in mc:
        if not c.view:
            # Do not display if not in view
            continue
        c_kind = props.ConstraintsKind(c.kind)
        if c_kind == props.ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES:
            p0_3d, p1_3d = bm.verts[c.point0].co, bm.verts[c.point1].co
            label = _format_distance(context, c.distance)
            color = _select_color(c, equals((p1_3d - p0_3d).length, c.distance))
            batch.add_edge_label((c.point0, c.point1), label, color)
        elif c_kind == props.ConstraintsKind.FIX_X_COORD:
            point = bm.verts[c.point].co
            color = _select_color(c, equals(point.x, c.x))
            batch.add_point_label(c.point, "X", color)
        elif c_kind == props.ConstraintsKind.FIX_Y_COORD:
            point = bm.verts[c.point].co
            color = _select_color(c, equals(point.y, c.y))
            batch.add_point_label(c.point, "Y", color)
        elif c_kind == props.ConstraintsKind.FIX_Z_COORD:
            point = bm.verts[c.point].co
            color = _select_color(c, equals(point.z, c.z))
            batch.add_point_label(c.point, "Z", color)
        elif c_kind == props.ConstraintsKind.FIX_XY_COORD:
            point = bm.verts[c.point].co
            color = _select_color(c, equals(point.x, c.x) and equals(point.y, c.y))
            batch.add_point_label(c.point, "XY", color)
        elif c_kind == props.ConstraintsKind.FIX_XZ_COORD:
            point = bm.verts[c.point].co
            color = _select_color(c, equals(point.x, c.x) and equals(point.z, c.z))
            batch.add_point_label(c.point, "XZ", color)
        elif c_kind == props.ConstraintsKind.FIX_YZ_COORD:
            point = bm.verts[c.point].co
            color = _select_color(c, equals(point.y, c.y) and equals(point.z, c.z))
            batch.add_point_label(c.point, "YZ", color)
        elif c_kind == props.ConstraintsKind.FIX_XYZ_COORD:
            point = bm.verts[c.point].co
            color = _select_color(c, equals(point.x, c.x) and equals(point.y, c.y) and equals(point.z, c.z))
            batch.add_point_label(c.point, "XYZ", color)
        elif c_kind == props.ConstraintsKind.PARALLEL:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            point2 = bm.verts[c.point2].co
            point3 = bm.verts[c.point3].co
            # parallel if cross product == 0
            v0_3d, v1_3d = point1 - point0, point3 - point2
            cross = v0_3d.cross(v1_3d)
            color = _select_color(c, equals(cross.x, 0) and equals(cross.y, 0) and equals(cross.z, 0))
            batch.add_edge_label((c.point0, c.point1), "//", color)
            batch.add_edge_label((c.point2, c.point3), "//", color)
        elif c_kind == props.ConstraintsKind.PERPENDICULAR:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            point2 = bm.verts[c.point2].co
            point3 = bm.verts[c.point3].co
            # perpendicular if dot == 0
            v0_3d, v1_3d = point1 - point0, point3 - point2
            d = v0_3d.dot(v1_3d)
            color = _select_color(c, equals(d, 0))
            batch.add_edge_label((c.point0, c.point1), "L", color)
            batch.add_edge_label((c.point2, c.point3), "L", color)
        elif c_kind == props.ConstraintsKind.ON_X:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            color = _select_color(
                c, equals(point0.y, point1.y) and equals(point0.z, point1.z)
            )
            batch.add_edge_label((c.point0, c.point1), "X", color)
        elif c_kind == props.ConstraintsKind.ON_Y:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            color = _select_color(
                c, equals(point0.x, point1.x) and equals(point0.z, point1.z)
            )
            batch.add_edge_label((c.point0, c.point1), "Y", color)
        elif c_kind == props.ConstraintsKind.ON_Z:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            color = _select_color(
                c, equals(point0.x, point1.x) and equals(point0.y, point1.y)
            )
            batch.add_edge_label((c.point0, c.point1), "Z", color)
        elif c_kind == props.ConstraintsKind.SAME_DISTANCE:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            point2 = bm.verts[c.point2].co
            point3 = bm.verts[c.point3].co
            v0_3d, v1_3d = point1 - point0, point3 - point2
            color = _select_color(c, equals(v0_3d.length, v1_3d.length))
            batch.add_edge_label((c.point0, c.point1), "/", color)
            batch.add_edge_label((c.point2, c.point3), "/", color)
        elif c_kind == props.ConstraintsKind.ANGLE:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            point2 = bm.verts[c.point2].co
            point3 = bm.verts[c.point3].co
            # dot product of v0 and v1 / (v0.length * v1.length) = cos(angle in radian)
            v0_3d, v1_3d = point1 - point0, point3 - point2
            cos_rad = v0_3d.dot(v1_3d) / (v0_3d.length * v1_3d.length)
            color = _select_color(c, equals(cos_rad, math.cos(math.pi * c.angle / 180)))
            batch.add_edge_label((c.point0, c.point1), f"{c.angle}°", color)
            batch.add_edge_label((c.point2, c.point3), f"{c.angle}°", color)
        else:
            # Don't want to raise an error here but it deserves it
            pass

    batch.draw(context)


def _select_color(constraint, constraint_ok):
    # Color change
    if constraint.show_details:
        # show detail
        return COLOR_SHOW_DETAIL
    if constraint.in_error:
        # is in solver error
        return COLOR_SOLVER_NOK
    if constraint_ok:
        # Constraint is OK
        return COLOR_OK
    # Constraint is not OK
    return COLOR_CONSTRAINT_NOK


def _normal_vector(o, p0_3d, p1_3d):
    """Return the normal vector (pointing outside) to an object
    and a pair of vertices"""
    # The vector between middle point of v1-v2 and object center location
    # is the normal vector I'm looking for
    vn = p0_3d.lerp(p1_3d, 0.5) - o.matrix_world.translation
    # normalize so I can to length computation on it
    vn.normalize()
    return vn


def _from_hex_rgb(r, g, b):
    return list(map(lambda x: x / 0xFF, (r, g, b, 0xFF)))


def _format_distance(context, distance):
    unit_system = context.scene.unit_settings.system
    if unit_system == "METRIC":
        r = round(distance, 2)
        if r >= 1.0:
            return f"{distance:.2f} m"
        elif r >= 0.1:
            return f"{distance * 100:.1f} cm"
        elif r >= 0.01:
            return f"{distance * 100:.2f} cm"
        else:
            return f"{distance * 1000:.2f} mm"
    elif unit_system == "IMPERIAL":
        feet = distance * 3.2808399
        if round(feet, 2) >= 1.0:
            return f"{feet:.2f} ft"
        else:
            inches = distance * 39.3700787
            return f"{inches:.2f} in"
    else:
        return f"{distance}"


# TODO move all of this in preferences of the addon

VERTEX_BOX_MARGIN = 4
# Spacing between edge and constraint drawing in px
EDGE_CONSTRAINT_SPACING = 10

COLOR_TEAL_400 = _from_hex_rgb(0x4F, 0xD1, 0xC5)
COLOR_RED_600 = _from_hex_rgb(0xE5, 0x3E, 0x3E)
COLOR_PINK_600 = _from_hex_rgb(0xD5, 0x3F, 0x8C)
COLOR_GREEN_400 = _from_hex_rgb(0x68, 0xD3, 0x91)
COLOR_ORANGE_400 = _from_hex_rgb(0xF6, 0xAD, 0x55)

COLOR_OK = COLOR_TEAL_400
COLOR_SOLVER_NOK = COLOR_RED_600
COLOR_CONSTRAINT_NOK = COLOR_PINK_600
COLOR_SHOW_DETAIL = COLOR_ORANGE_400

FONT_SIZE = 15
