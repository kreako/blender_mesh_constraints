import math
from ..solver import Solver, EPSILON


class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


def equal_float(value, ref):
    return ref - EPSILON < value and value < ref + EPSILON


def test_solver_basic_distance():
    s = Solver()
    s.distance_2_vertices(42, 1, Vector3(10, 10, 10), 2, Vector3(20, 20, 20), 30)
    ret = s.solve()
    assert ret["solved"]
    points = ret["points"]
    assert len(points) == 2
    p0 = points[0]
    p1 = points[1]
    assert equal_float(p0.x, 6.33974596215561)
    assert equal_float(p0.y, 6.33974596215561)
    assert equal_float(p0.z, 6.33974596215561)
    assert equal_float(p1.x, 23.6602540378444)
    assert equal_float(p1.y, 23.6602540378444)
    assert equal_float(p1.z, 23.6602540378444)


def test_solver_basic_distance_fix():
    s = Solver()
    p1_ival = Vector3(10, 10, 10)
    p2_ival = Vector3(20, 20, 20)
    s.distance_2_vertices(42, 1, p1_ival, 2, p2_ival, 30)
    s.fix_x(42, 1, p1_ival, 10)
    s.fix_z(42, 2, p2_ival, 20)
    ret = s.solve()
    assert ret["solved"]
    points = ret["points"]
    assert len(points) == 2
    p0 = points[0]
    p1 = points[1]
    assert equal_float(p0.x, 10)
    assert equal_float(p1.z, 20)
    distance = math.sqrt((p0.x - p1.x) ** 2 + (p0.y - p1.y) ** 2 + (p0.z - p1.z) ** 2)
    assert equal_float(distance, 30)


def test_solver_unsolvable():
    s = Solver()
    p1_ival = Vector3(10, 10, 10)
    p2_ival = Vector3(20, 20, 20)
    s.distance_2_vertices(42, 1, p1_ival, 2, p2_ival, 30)
    s.fix_x(43, 1, p1_ival, 10)
    s.fix_y(43, 1, p1_ival, 10)
    s.fix_z(43, 1, p1_ival, 10)
    s.fix_x(44, 2, p2_ival, 20)
    s.fix_y(44, 2, p2_ival, 20)
    s.fix_z(44, 2, p2_ival, 20)
    ret = s.solve()
    assert ret["solved"] == False
    assert ret["not_convergent"] == False
    assert ret["overflow_count"] == True
    assert ret["singular_matrix"] == False
    assert ret["equations_in_error"] == [42]


def test_solver_low_rank():
    s = Solver()
    p1_ival = Vector3(10, 10, 10)
    p2_ival = Vector3(20, 20, 20)
    s.distance_2_vertices(42, 1, p1_ival, 2, p2_ival, 30)
    s.distance_2_vertices(43, 1, p1_ival, 2, p2_ival, 20)
    ret = s.solve()
    assert ret["solved"] == False
    assert ret["not_convergent"] == False
    assert ret["singular_matrix"] == True
    assert ret["overflow_count"] == False
    assert ret["equations_in_error"] == [42, 43]
