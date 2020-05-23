import gpu
from gpu_extras.batch import batch_for_shader
from bpy.types import WindowManager
from bpy_extras import view3d_utils
import bmesh
from mathutils import Vector
import blf

from . import props


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
            _distance_between_2_vertices(context, point0, point1)
        elif c_kind == props.ConstraintsKind.FIX_X_COORD:
            point = bm.verts[c.point].co
            _fix_xyz_coord(context, point, "x")
        elif c_kind == props.ConstraintsKind.FIX_Y_COORD:
            point = bm.verts[c.point].co
            _fix_xyz_coord(context, point, "y")
        elif c_kind == props.ConstraintsKind.FIX_Z_COORD:
            point = bm.verts[c.point].co
            _fix_xyz_coord(context, point, "z")
        elif c_kind == props.ConstraintsKind.FIX_XY_COORD:
            point = bm.verts[c.point].co
            _fix_xyz_coord(context, point, "xy")
        elif c_kind == props.ConstraintsKind.FIX_XZ_COORD:
            point = bm.verts[c.point].co
            _fix_xyz_coord(context, point, "xz")
        elif c_kind == props.ConstraintsKind.FIX_YZ_COORD:
            point = bm.verts[c.point].co
            _fix_xyz_coord(context, point, "yz")
        elif c_kind == props.ConstraintsKind.FIX_XYZ_COORD:
            point = bm.verts[c.point].co
            _fix_xyz_coord(context, point, "xyz")
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
    shader.uniform_float("color", COLOR_TEAL_400)
    batch.draw(shader)


def _distance_between_2_vertices(context, point0_3d, point1_3d):
    """Draw the constraint DISTANCE_BETWEEN_2_VERTICES"""
    pass


def _fix_xyz_coord(context, point_3d, label):
    """Draw the constraint FIX_{X,Y,Z}_COORD"""
    region = context.region
    rv3d = context.space_data.region_3d
    o = context.edit_object

    world_point_3d = _world_point(o, point_3d)
    world_point_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, point_3d)

    if world_point_2d is None:
        # Not in view
        return

    # Draw the box
    vertices = [world_point_2d + Vector((-VERTEX_BOX_MARGIN, -VERTEX_BOX_MARGIN)),
                world_point_2d + Vector((-VERTEX_BOX_MARGIN, VERTEX_BOX_MARGIN)),
                world_point_2d + Vector((VERTEX_BOX_MARGIN, VERTEX_BOX_MARGIN)),
                world_point_2d + Vector((VERTEX_BOX_MARGIN, -VERTEX_BOX_MARGIN))]
    indices = ((0, 1), (1, 2), (2, 3), (3, 0),)
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": vertices}, indices=indices)

    shader.bind()
    shader.uniform_float("color", COLOR_TEAL_400)
    batch.draw(shader)

    # Now the label
    font_id = 0
    blf.position(font_id, world_point_2d[0] + 1.5 * VERTEX_BOX_MARGIN, world_point_2d[1] - VERTEX_BOX_MARGIN, 0)
    blf.size(font_id, 15, 72)
    blf.color(font_id, *COLOR_TEAL_400)
    blf.draw(font_id, label)


def _world_point(o, point_3d):
    """Transform a 3D point from the mesh to a 3D point of the world
    by multiplying with the matrix world
    o: object edited
    point_3d: 3D point of the object's mesh"""
    v = o.matrix_world @ point_3d.to_4d()
    return v.to_3d()


def _normal_vector(o, point0_3d, point1_3d):
    """Return the normal vector (pointing outside) to an object
    and a pair of vertices"""
    # The vector between middle point of v1-v2 and object center location
    # is the normal vector I'm looking for
    vn = v1.lerp(v2, 0.5) - o.matrix_world.translation
    # normalize so I can to length computation on it
    vn.normalize()
    return vn


def _from_hex_rgb(r, g, b):
    return list(map(lambda x: x / 0xFF, (r, g, b, 0xFF)))


def draw_constraints_violation(context):
    pass


# TODO move all of this in preferences of the addon

VERTEX_BOX_MARGIN = 4

COLOR_TEAL_400 = _from_hex_rgb(0x4F, 0xD1, 0xC5)
