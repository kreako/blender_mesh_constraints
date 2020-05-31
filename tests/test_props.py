from ..props import ConstraintsKind, MeshConstraints, constraints_kind_abbreviation

def test_remove(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    assert len(mc) == 0
    mc.add_distance_between_2_vertices(2, 0, 0)
    assert len(mc) == 1
    mc.remove(0)
    assert len(mc) == 0

def test_exist_constraint_multiple(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
    assert mc.exist_constraint(k, point0=0, point1=1) is None
    mc.add_fix_x_coord(0, 1)
    mc.add_fix_y_coord(0, 1)
    mc.add_distance_between_2_vertices(2, 0, 0)
    mc.add_fix_z_coord(0, 1)
    assert mc.exist_constraint(k, point0=2, point1=0) == 2
    mc.remove(1)
    assert mc.exist_constraint(k, point0=2, point1=0) == 1

def test_distance_between_2_vertices(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
    assert mc.exist_constraint(k, point0=0, point1=1) is None
    assert mc.exist_constraint(k, point0=0, point1=2) is None
    assert mc.exist_constraint(k, point0=2, point1=0) is None
    mc.add_distance_between_2_vertices(2, 0, 42.3)
    assert mc.exist_constraint(k, point0=0, point1=1) is None
    assert mc.exist_constraint(k, point0=2, point1=0) == 0
    assert mc.exist_constraint(k, point0=0, point1=2) == 0
    c = mc[0]
    assert c.kind == ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
    assert c.point0 == 2
    assert c.point1 == 0
    assert c.distance == 42.3


def test_fix_x_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_X_COORD
    assert mc.exist_constraint(k, point=2) is None
    assert mc.exist_constraint(k, point=1) is None
    mc.add_fix_x_coord(2, 1)
    assert mc.exist_constraint(k, point=2) == 0
    assert mc.exist_constraint(k, point=1) is None
    c = mc[0]
    assert c.kind == ConstraintsKind.FIX_X_COORD
    assert c.point == 2
    assert c.x == 1


def test_fix_y_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_Y_COORD
    assert mc.exist_constraint(k, point=2) is None
    assert mc.exist_constraint(k, point=1) is None
    mc.add_fix_y_coord(2, 1)
    assert mc.exist_constraint(k, point=2) == 0
    assert mc.exist_constraint(k, point=1) is None
    c = mc[0]
    assert c.kind == ConstraintsKind.FIX_Y_COORD
    assert c.point == 2
    assert c.y == 1


def test_fix_z_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_Z_COORD
    assert mc.exist_constraint(k, point=2) is None
    assert mc.exist_constraint(k, point=1) is None
    mc.add_fix_z_coord(2, 1)
    assert mc.exist_constraint(k, point=2) == 0
    assert mc.exist_constraint(k, point=1) is None
    c = mc[0]
    assert c.kind == ConstraintsKind.FIX_Z_COORD
    assert c.point == 2
    assert c.z == 1


def test_fix_xy_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_XY_COORD
    assert mc.exist_constraint(k, point=2) is None
    assert mc.exist_constraint(k, point=1) is None
    mc.add_fix_xy_coord(2, 1.1, 3.3)
    assert mc.exist_constraint(k, point=2) == 0
    assert mc.exist_constraint(k, point=1) is None
    c = mc[0]
    assert c.kind == ConstraintsKind.FIX_XY_COORD
    assert c.point == 2
    assert c.x == 1.1
    assert c.y == 3.3


def test_fix_xz_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_XZ_COORD
    assert mc.exist_constraint(k, point=2) is None
    assert mc.exist_constraint(k, point=1) is None
    mc.add_fix_xz_coord(2, 1.1, 3.3)
    assert mc.exist_constraint(k, point=2) == 0
    assert mc.exist_constraint(k, point=1) is None
    c = mc[0]
    assert c.kind == ConstraintsKind.FIX_XZ_COORD
    assert c.point == 2
    assert c.x == 1.1
    assert c.z == 3.3


def test_fix_yz_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_YZ_COORD
    assert mc.exist_constraint(k, point=2) is None
    assert mc.exist_constraint(k, point=1) is None
    mc.add_fix_yz_coord(2, 1.1, 3.3)
    assert mc.exist_constraint(k, point=2) == 0
    assert mc.exist_constraint(k, point=1) is None
    c = mc[0]
    assert c.kind == ConstraintsKind.FIX_YZ_COORD
    assert c.point == 2
    assert c.y == 1.1
    assert c.z == 3.3


def test_fix_xyz_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_XYZ_COORD
    assert mc.exist_constraint(k, point=2) is None
    assert mc.exist_constraint(k, point=1) is None
    mc.add_fix_xyz_coord(2, 2.2, 1.1, 3.3)
    assert mc.exist_constraint(k, point=2) == 0
    assert mc.exist_constraint(k, point=1) is None
    c = mc[0]
    assert c.kind == ConstraintsKind.FIX_XYZ_COORD
    assert c.point == 2
    assert c.x == 2.2
    assert c.y == 1.1
    assert c.z == 3.3


def test_iter(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    assert len(mc) == 0
    mc.add_fix_z_coord(0, 4)
    mc.add_distance_between_2_vertices(2, 0, 5)
    mc.add_fix_x_coord(1, 1.3)
    mc.add_fix_y_coord(1, 0)
    assert len(mc) == 4
    for i, c in enumerate(mc):
        if i == 0:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_Z_COORD
            assert c.point == 0
            assert c.z == 4
        elif i == 1:
            assert ConstraintsKind(c.kind) == ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
            assert c.point0 == 2
            assert c.point1 == 0
            assert c.distance == 5
        elif i == 2:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_X_COORD
            assert c.point == 1
            assert c.x == 1.3
        elif i == 3:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_Y_COORD
            assert c.point == 1
            assert c.y == 0
        else:
            assert False
    mc.remove(1)
    assert len(mc) == 3
    for i, c in enumerate(mc):
        if i == 0:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_Z_COORD
            assert c.point == 0
            assert c.z == 4
        elif i == 1:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_X_COORD
            assert c.point == 1
            assert c.x == 1.3
        elif i == 2:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_Y_COORD
            assert c.point == 1
            assert c.y == 0
        else:
            assert False


def test_parallel(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.PARALLEL
    assert mc.exist_constraint(k, point0=2, point1=3, point2=5, point3=6) is None
    assert mc.exist_constraint(k, point0=1, point1=3, point2=5, point3=6) is None
    mc.add_parallel(2, 3, 5, 6)
    assert mc.exist_constraint(k, point0=1, point1=3, point2=5, point3=6) is None
    assert mc.exist_constraint(k, point0=2, point1=3, point2=5, point3=6) == 0
    assert mc.exist_constraint(k, point0=3, point1=2, point2=5, point3=6) == 0
    assert mc.exist_constraint(k, point0=3, point1=2, point2=6, point3=5) == 0
    assert mc.exist_constraint(k, point0=2, point1=3, point2=6, point3=5) == 0
    c = mc[0]
    assert c.kind == ConstraintsKind.PARALLEL
    assert c.point0 == 2
    assert c.point1 == 3
    assert c.point2 == 5
    assert c.point3 == 6


def test_constraints_abbreviation():
    for k in ConstraintsKind:
        assert k in constraints_kind_abbreviation


def test_perpendicular(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.PERPENDICULAR
    assert mc.exist_constraint(k, point0=2, point1=3, point2=5, point3=6) is None
    assert mc.exist_constraint(k, point0=1, point1=3, point2=5, point3=6) is None
    mc.add_perpendicular(2, 3, 5, 6)
    assert mc.exist_constraint(k, point0=1, point1=3, point2=5, point3=6) is None
    assert mc.exist_constraint(k, point0=2, point1=3, point2=5, point3=6) == 0
    assert mc.exist_constraint(k, point0=3, point1=2, point2=5, point3=6) == 0
    assert mc.exist_constraint(k, point0=3, point1=2, point2=6, point3=5) == 0
    assert mc.exist_constraint(k, point0=2, point1=3, point2=6, point3=5) == 0
    c = mc[0]
    assert c.kind == ConstraintsKind.PERPENDICULAR
    assert c.point0 == 2
    assert c.point1 == 3
    assert c.point2 == 5
    assert c.point3 == 6


def test_on_x(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.ON_X
    assert mc.exist_constraint(k, point0=2, point1=3) is None
    assert mc.exist_constraint(k, point0=1, point1=3) is None
    mc.add_on_x(2, 3)
    assert mc.exist_constraint(k, point0=1, point1=3) is None
    assert mc.exist_constraint(k, point0=2, point1=3) == 0
    assert mc.exist_constraint(k, point0=3, point1=2) == 0
    c = mc[0]
    assert c.kind == ConstraintsKind.ON_X
    assert c.point0 == 2
    assert c.point1 == 3


def test_on_y(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.ON_Y
    assert mc.exist_constraint(k, point0=2, point1=3) is None
    assert mc.exist_constraint(k, point0=1, point1=3) is None
    mc.add_on_y(2, 3)
    assert mc.exist_constraint(k, point0=1, point1=3) is None
    assert mc.exist_constraint(k, point0=2, point1=3) == 0
    assert mc.exist_constraint(k, point0=3, point1=2) == 0
    c = mc[0]
    assert c.kind == ConstraintsKind.ON_Y
    assert c.point0 == 2
    assert c.point1 == 3


def test_on_z(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.ON_Z
    assert mc.exist_constraint(k, point0=2, point1=3) is None
    assert mc.exist_constraint(k, point0=1, point1=3) is None
    mc.add_on_z(2, 3)
    assert mc.exist_constraint(k, point0=1, point1=3) is None
    assert mc.exist_constraint(k, point0=2, point1=3) == 0
    assert mc.exist_constraint(k, point0=3, point1=2) == 0
    c = mc[0]
    assert c.kind == ConstraintsKind.ON_Z
    assert c.point0 == 2
    assert c.point1 == 3


def test_same_distance(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.SAME_DISTANCE
    assert mc.exist_constraint(k, point0=2, point1=3, point2=5, point3=6) is None
    assert mc.exist_constraint(k, point0=1, point1=3, point2=5, point3=6) is None
    mc.add_same_distance(2, 3, 5, 6)
    assert mc.exist_constraint(k, point0=1, point1=3, point2=5, point3=6) is None
    assert mc.exist_constraint(k, point0=2, point1=3, point2=5, point3=6) == 0
    assert mc.exist_constraint(k, point0=3, point1=2, point2=5, point3=6) == 0
    assert mc.exist_constraint(k, point0=3, point1=2, point2=6, point3=5) == 0
    assert mc.exist_constraint(k, point0=2, point1=3, point2=6, point3=5) == 0
    c = mc[0]
    assert c.kind == ConstraintsKind.SAME_DISTANCE
    assert c.point0 == 2
    assert c.point1 == 3
    assert c.point2 == 5
    assert c.point3 == 6


def test_angle(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.ANGLE
    assert mc.exist_constraint(k, point0=2, point1=3, point2=5, point3=6) is None
    assert mc.exist_constraint(k, point0=1, point1=3, point2=5, point3=6) is None
    mc.add_angle(2, 3, 5, 6, 42.3)
    assert mc.exist_constraint(k, point0=1, point1=3, point2=5, point3=6) is None
    assert mc.exist_constraint(k, point0=2, point1=3, point2=5, point3=6) == 0
    assert mc.exist_constraint(k, point0=3, point1=2, point2=5, point3=6) == 0
    assert mc.exist_constraint(k, point0=3, point1=2, point2=6, point3=5) == 0
    assert mc.exist_constraint(k, point0=2, point1=3, point2=6, point3=5) == 0
    c = mc[0]
    assert c.kind == ConstraintsKind.ANGLE
    assert c.point0 == 2
    assert c.point1 == 3
    assert c.point2 == 5
    assert c.point3 == 6
    assert c.angle == 42.3


def test_reverse_iter(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    assert len(mc) == 0
    mc.add_fix_z_coord(0, 4)
    mc.add_distance_between_2_vertices(2, 0, 5)
    mc.add_fix_x_coord(1, 1.3)
    mc.add_fix_y_coord(1, 0)
    assert len(mc) == 4
    for i, c in enumerate(mc.reverse()):
        if i == 3:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_Z_COORD
            assert c.point == 0
            assert c.z == 4
        elif i == 2:
            assert ConstraintsKind(c.kind) == ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
            assert c.point0 == 2
            assert c.point1 == 0
            assert c.distance == 5
        elif i == 1:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_X_COORD
            assert c.point == 1
            assert c.x == 1.3
        elif i == 0:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_Y_COORD
            assert c.point == 1
            assert c.y == 0
        else:
            assert False


def test_delete_all(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    assert len(mc) == 0
    mc.add_fix_z_coord(0, 4)
    mc.add_distance_between_2_vertices(2, 0, 5)
    mc.add_fix_x_coord(1, 1.3)
    mc.add_fix_y_coord(1, 0)
    assert len(mc) == 4
    mc.delete_all()
    assert len(mc) == 0
