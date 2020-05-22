from ..props import ConstraintsKind, MeshConstraints

def test_remove(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    assert len(mc) == 0
    mc.add_distance_between_2_vertices(2, 0, 0)
    assert len(mc) == 1
    mc.remove(0)
    assert len(mc) == 0

def test_exist_constraint_distance_between_2_vertices(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
    assert mc.exist_constraint(k, point0=0, point1=1) == False
    assert mc.exist_constraint(k, point0=0, point1=2) == False
    assert mc.exist_constraint(k, point0=2, point1=0) == False
    mc.add_distance_between_2_vertices(2, 0, 0)
    assert mc.exist_constraint(k, point0=0, point1=1) == False
    assert mc.exist_constraint(k, point0=2, point1=0) == True
    assert mc.exist_constraint(k, point0=0, point1=2) == True


def test_exist_constraint_fix_x_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_X_COORD
    assert mc.exist_constraint(k, point0=0) == False
    assert mc.exist_constraint(k, point0=1) == False
    mc.add_fix_x_coord(0, 1)
    assert mc.exist_constraint(k, point0=0) == True
    assert mc.exist_constraint(k, point0=1) == False


def test_exist_constraint_fix_y_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_Y_COORD
    assert mc.exist_constraint(k, point0=0) == False
    assert mc.exist_constraint(k, point0=1) == False
    mc.add_fix_y_coord(0, 1)
    assert mc.exist_constraint(k, point0=0) == True
    assert mc.exist_constraint(k, point0=1) == False


def test_exist_constraint_fix_z_coord(mesh_constraints_data):
    mc = MeshConstraints(mesh_constraints_data)
    k = ConstraintsKind.FIX_Z_COORD
    assert mc.exist_constraint(k, point0=0) == False
    assert mc.exist_constraint(k, point0=1) == False
    mc.add_fix_z_coord(0, 1)
    assert mc.exist_constraint(k, point0=0) == True
    assert mc.exist_constraint(k, point0=1) == False


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
            assert c.point0 == 0
            assert c.value == 4
        elif i == 1:
            assert ConstraintsKind(c.kind) == ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
            assert c.point0 == 2
            assert c.point1 == 0
            assert c.value == 5
        elif i == 2:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_X_COORD
            assert c.point0 == 1
            assert c.value == 1.3
        elif i == 3:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_Y_COORD
            assert c.point0 == 1
            assert c.value == 0
        else:
            assert False
    mc.remove(1)
    assert len(mc) == 3
    for i, c in enumerate(mc):
        if i == 0:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_Z_COORD
            assert c.point0 == 0
            assert c.value == 4
        elif i == 1:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_X_COORD
            assert c.point0 == 1
            assert c.value == 1.3
        elif i == 2:
            assert ConstraintsKind(c.kind) == ConstraintsKind.FIX_Y_COORD
            assert c.point0 == 1
            assert c.value == 0
        else:
            assert False
