import gpu
from gpu_extras.batch import batch_for_shader
from bpy.types import WindowManager
from bpy_extras.view3d_utils import location_3d_to_region_2d
import bmesh
from mathutils import Vector
import blf

from . import props
from . import solver


def equals(value, ref):
    return ref - solver.EPSILON < value and value < ref + solver.EPSILON


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

    for c in mc:
        if not c.view:
            # Do not display if not in view
            continue
        c_kind = props.ConstraintsKind(c.kind)
        if c_kind == props.ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            _distance_between_2_vertices(context, point0, point1, c)
        elif c_kind == props.ConstraintsKind.FIX_X_COORD:
            point = bm.verts[c.point].co
            _fix_x_coord(context, point, c)
        elif c_kind == props.ConstraintsKind.FIX_Y_COORD:
            point = bm.verts[c.point].co
            _fix_y_coord(context, point, c)
        elif c_kind == props.ConstraintsKind.FIX_Z_COORD:
            point = bm.verts[c.point].co
            _fix_z_coord(context, point, c)
        elif c_kind == props.ConstraintsKind.FIX_XY_COORD:
            point = bm.verts[c.point].co
            _fix_xy_coord(context, point, c)
        elif c_kind == props.ConstraintsKind.FIX_XZ_COORD:
            point = bm.verts[c.point].co
            _fix_xz_coord(context, point, c)
        elif c_kind == props.ConstraintsKind.FIX_YZ_COORD:
            point = bm.verts[c.point].co
            _fix_yz_coord(context, point, c)
        elif c_kind == props.ConstraintsKind.FIX_XYZ_COORD:
            point = bm.verts[c.point].co
            _fix_xyz_coord(context, point, c)
        elif c_kind == props.ConstraintsKind.PARALLEL:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            point2 = bm.verts[c.point2].co
            point3 = bm.verts[c.point3].co
            _parallel(context, point0, point1, point2, point3, c)
        elif c_kind == props.ConstraintsKind.PERPENDICULAR:
            point0 = bm.verts[c.point0].co
            point1 = bm.verts[c.point1].co
            point2 = bm.verts[c.point2].co
            point3 = bm.verts[c.point3].co
            _perpendicular(context, point0, point1, point2, point3, c)
        else:
            # Don't want to raise an error here but it deserves it
            pass

    # draw_red_bounds(context)


def draw_red_bounds(context):
    region = context.region
    rv3d = context.space_data.region_3d

    w = region.width
    h = region.height

    margin = 10
    x_min = margin
    x_max = w - margin
    y_min = margin
    y_max = h - margin
    if context.preferences.system.use_region_overlap:
        area = context.area
        for r in area.regions:
            if r.type == "TOOLS":
                x_min += r.width
            elif r.type == "UI":
                x_max -= r.width
    vertices = [
        (x_min, y_min),
        (x_min, y_max),
        (x_max, y_max),
        (x_max, y_min),
    ]
    indices = ((0, 1), (1, 2), (2, 3), (3, 0))
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": vertices}, indices=indices)

    shader.bind()
    shader.uniform_float("color", COLOR_OK)
    batch.draw(shader)


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


def _distance_between_2_vertices(context, p0_3d, p1_3d, constraint):
    """Draw the constraint DISTANCE_BETWEEN_2_VERTICES"""
    region = context.region
    rv3d = context.space_data.region_3d
    o = context.edit_object

    p0_2d = location_3d_to_region_2d(region, rv3d, p0_3d)
    p1_2d = location_3d_to_region_2d(region, rv3d, p1_3d)
    if p0_2d is None or p1_2d is None:
        # not in view
        # TODO should I do something when one of the points is in view ?
        return

    v_3d = p1_3d - p0_3d
    v_2d = p1_2d - p0_2d
    # normal vector to v_3d pointing to outside of the object
    # already normalized multiply to 1/10 of v_3d length so it hopefully
    # stays in view
    vn_3d = _normal_vector(o, p0_3d, p1_3d) * v_3d.length / 10

    # Projected point on normal vector from p0_3d
    p0_n_2d = location_3d_to_region_2d(region, rv3d, p0_3d + vn_3d)
    if p0_n_2d is None:
        # Not in view
        return
    # Now the point on (p0_2d - p0_n_2d) vector so (p0_n0_2d - p0_2d).length == EDGE_CONSTRAINT_SPACING
    p0_n0_2d = p0_2d.lerp(p0_n_2d, EDGE_CONSTRAINT_SPACING / (p0_n_2d - p0_2d).length)
    # Same story with EDGE_CONSTRAINT_SPACING * 1.3
    p0_n1_2d = p0_2d.lerp(
        p0_n_2d, EDGE_CONSTRAINT_SPACING * 1.3 / (p0_n_2d - p0_2d).length
    )

    # Keep p0_n0_2d - p1_n0_2d parallel to p0_2d - p1_2d
    p1_n0_2d = p0_n0_2d + v_2d
    # Same
    p1_n1_2d = p0_n1_2d + v_2d

    # Color change
    color = _select_color(constraint, equals(v_3d.length, constraint.distance))

    # Now text drawing
    txt = _format_distance(context, constraint.distance)
    font_id = 0
    width, height = blf.dimensions(font_id, txt)
    p_n0_middle = p0_n0_2d.lerp(p1_n0_2d, 0.5)
    blf.position(font_id, p_n0_middle[0] - width / 2, p_n0_middle[1] - height / 2, 0)
    blf.size(font_id, FONT_SIZE, 72)
    blf.color(font_id, *color)
    blf.draw(font_id, txt)

    # Draw the lines
    # TODO cut the line on the text box
    vertices = [p0_2d, p1_2d, p0_n0_2d, p1_n0_2d, p0_n1_2d, p1_n1_2d]
    indices = ((0, 4), (1, 5), (2, 3))
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": vertices}, indices=indices)

    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def _parallel(context, p0_3d, p1_3d, p2_3d, p3_3d, constraint):
    """Draw the constraint PARALLEL"""
    region = context.region
    rv3d = context.space_data.region_3d
    o = context.edit_object

    # Color change if OK, cross product should be 0
    v0_3d = p1_3d - p0_3d
    v1_3d = p3_3d - p2_3d
    c = v0_3d.cross(v1_3d)
    color = _select_color(constraint, equals(c.x, 0) and equals(c.y, 0) and equals(c.z, 0))

    def _single_parallel(p0_3d, p1_3d):
        p0_2d = location_3d_to_region_2d(region, rv3d, p0_3d)
        p1_2d = location_3d_to_region_2d(region, rv3d, p1_3d)
        if p0_2d is None or p1_2d is None:
            # not in view
            # TODO should I do something when one of the points is in view ?
            return

        v_3d = p1_3d - p0_3d
        v_2d = p1_2d - p0_2d
        # normal vector to v_3d pointing to outside of the object
        # already normalized multiply to 1/10 of v_3d length so it hopefully
        # stays in view
        vn_3d = _normal_vector(o, p0_3d, p1_3d) * v_3d.length / 10

        # Projected point on normal vector from p0_3d
        p0_n_2d = location_3d_to_region_2d(region, rv3d, p0_3d + vn_3d)
        if p0_n_2d is None:
            # Not in view
            return
        # Now the point on (p0_2d - p0_n_2d) vector so (p0_n0_2d - p0_2d).length == EDGE_CONSTRAINT_SPACING
        p0_n0_2d = p0_2d.lerp(
            p0_n_2d, EDGE_CONSTRAINT_SPACING / (p0_n_2d - p0_2d).length
        )

        # Keep p0_n0_2d - p1_n0_2d parallel to p0_2d - p1_2d
        p1_n0_2d = p0_n0_2d + v_2d

        # Now text drawing
        txt = "//"
        font_id = 0
        width, height = blf.dimensions(font_id, txt)
        p_n0_middle = p0_n0_2d.lerp(p1_n0_2d, 0.5)
        blf.position(
            font_id, p_n0_middle[0] - width / 2, p_n0_middle[1] - height / 2, 0
        )
        blf.size(font_id, FONT_SIZE, 72)
        blf.color(font_id, *color)
        blf.draw(font_id, txt)

    _single_parallel(p0_3d, p1_3d)
    _single_parallel(p2_3d, p3_3d)


def _perpendicular(context, p0_3d, p1_3d, p2_3d, p3_3d, constraint):
    """Draw the constraint PERPENDICULAR"""
    region = context.region
    rv3d = context.space_data.region_3d
    o = context.edit_object

    # Color change if OK, dot product should be 0
    v0_3d = p1_3d - p0_3d
    v1_3d = p3_3d - p2_3d
    d = v0_3d.dot(v1_3d)
    color = _select_color(constraint, equals(d, 0))

    def _single_perpendicular(p0_3d, p1_3d):
        p0_2d = location_3d_to_region_2d(region, rv3d, p0_3d)
        p1_2d = location_3d_to_region_2d(region, rv3d, p1_3d)
        if p0_2d is None or p1_2d is None:
            # not in view
            # TODO should I do something when one of the points is in view ?
            return

        v_3d = p1_3d - p0_3d
        v_2d = p1_2d - p0_2d
        # normal vector to v_3d pointing to outside of the object
        # already normalized multiply to 1/10 of v_3d length so it hopefully
        # stays in view
        vn_3d = _normal_vector(o, p0_3d, p1_3d) * v_3d.length / 10

        # Projected point on normal vector from p0_3d
        p0_n_2d = location_3d_to_region_2d(region, rv3d, p0_3d + vn_3d)
        if p0_n_2d is None:
            # Not in view
            return
        # Now the point on (p0_2d - p0_n_2d) vector so (p0_n0_2d - p0_2d).length == EDGE_CONSTRAINT_SPACING
        p0_n0_2d = p0_2d.lerp(
            p0_n_2d, EDGE_CONSTRAINT_SPACING / (p0_n_2d - p0_2d).length
        )

        # Keep p0_n0_2d - p1_n0_2d parallel to p0_2d - p1_2d
        p1_n0_2d = p0_n0_2d + v_2d

        # Now text drawing
        txt = "_|_"
        font_id = 0
        width, height = blf.dimensions(font_id, txt)
        p_n0_middle = p0_n0_2d.lerp(p1_n0_2d, 0.5)
        blf.position(
            font_id, p_n0_middle[0] - width / 2, p_n0_middle[1] - height / 2, 0
        )
        blf.size(font_id, FONT_SIZE, 72)
        blf.color(font_id, *color)
        blf.draw(font_id, txt)

    _single_perpendicular(p0_3d, p1_3d)
    _single_perpendicular(p2_3d, p3_3d)


def _fix_x_coord(context, point_3d, constraint):
    color = _select_color(constraint, equals(point_3d.x, constraint.x))
    _fix_coord(context, point_3d, "x", color)


def _fix_y_coord(context, point_3d, constraint):
    color = _select_color(constraint, equals(point_3d.y, constraint.y))
    _fix_coord(context, point_3d, "y", color)


def _fix_z_coord(context, point_3d, constraint):
    color = _select_color(constraint, equals(point_3d.z, constraint.z))
    _fix_coord(context, point_3d, "z", color)


def _fix_xy_coord(context, point_3d, constraint):
    color = _select_color(
        constraint,
        equals(point_3d.x, constraint.x) and equals(point_3d.y, constraint.y),
    )
    _fix_coord(context, point_3d, "xy", color)


def _fix_xz_coord(context, point_3d, constraint):
    color = _select_color(
        constraint,
        equals(point_3d.x, constraint.x) and equals(point_3d.z, constraint.z),
    )
    _fix_coord(context, point_3d, "xz", color)


def _fix_yz_coord(context, point_3d, constraint):
    color = _select_color(
        constraint,
        equals(point_3d.y, constraint.y) and equals(point_3d.z, constraint.z),
    )
    _fix_coord(context, point_3d, "yz", color)


def _fix_xyz_coord(context, point_3d, constraint):
    color = _select_color(
        constraint,
        equals(point_3d.x, constraint.x)
        and equals(point_3d.y, constraint.y)
        and equals(point_3d.z, constraint.z),
    )
    _fix_coord(context, point_3d, "xyz", color)


def _fix_coord(context, point_3d, label, color):
    """Draw the constraint FIX_{X,Y,Z}_COORD"""
    region = context.region
    rv3d = context.space_data.region_3d
    o = context.edit_object

    world_point_3d = _world_point(o, point_3d)
    world_point_2d = location_3d_to_region_2d(region, rv3d, point_3d)

    if world_point_2d is None:
        # Not in view
        return

    # Draw the box
    vertices = [
        world_point_2d + Vector((-VERTEX_BOX_MARGIN, -VERTEX_BOX_MARGIN)),
        world_point_2d + Vector((-VERTEX_BOX_MARGIN, VERTEX_BOX_MARGIN)),
        world_point_2d + Vector((VERTEX_BOX_MARGIN, VERTEX_BOX_MARGIN)),
        world_point_2d + Vector((VERTEX_BOX_MARGIN, -VERTEX_BOX_MARGIN)),
    ]
    indices = (
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
    )
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": vertices}, indices=indices)

    shader.bind()

    # Or leave it to draw violation thing ?
    shader.uniform_float("color", color)
    batch.draw(shader)

    # Now the label
    font_id = 0
    blf.position(
        font_id,
        world_point_2d[0] + 1.5 * VERTEX_BOX_MARGIN,
        world_point_2d[1] - VERTEX_BOX_MARGIN,
        0,
    )
    blf.size(font_id, FONT_SIZE, 72)
    blf.color(font_id, *color)
    blf.draw(font_id, label)


def _world_point(o, point_3d):
    """Transform a 3D point from the mesh to a 3D point of the world
    by multiplying with the matrix world
    o: object edited
    point_3d: 3D point of the object's mesh"""
    v = o.matrix_world @ point_3d.to_4d()
    return v.to_3d()


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
            return f"{distance:.2f} m"
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
