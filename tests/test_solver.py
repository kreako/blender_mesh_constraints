import pytest
import math
from ..solver import Solver, EPSILON, NewtonSolver, symbols, sqrt, MeshPoint


class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"

    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z,)


def equal_float(value, ref):
    return ref - EPSILON < value and value < ref + EPSILON


def test_newton_solver_init():
    x = symbols("x")
    y = symbols("y")
    equations = [
        x + 42 * y - 6,
        2 * x ** 2 + y ** 2 + 8,
        2 * x + x ** 2 + 4 * y ** 2 + 8,
    ]
    initial_values = {x: 0, y: 0}
    s = NewtonSolver(equations, initial_values)
    s.prepare_matrix()

    assert len(s.params) == 2
    # number of equations
    assert len(s.a_eq) == 3
    assert len(s.b) == 3
    # number of params
    assert len(s.a_eq[0]) == 2

    if x == s.params[0]:
        x_index = 0
        y_index = 1
    else:
        x_index = 1
        y_index = 0

    assert s.a_eq[0][x_index] == 1
    assert s.a_eq[0][y_index] == 42

    assert s.a_eq[1][x_index] == 4 * x
    assert s.a_eq[1][y_index] == 2 * y

    assert s.a_eq[2][x_index] == 2 * x + 2
    assert s.a_eq[2][y_index] == 8 * y


def test_newton_solver_eval_jacobian():
    x = symbols("x")
    y = symbols("y")
    z = symbols("z")
    equations = [
        x + 42 * y + z ** 3,
        2 * x ** 2 + y ** 2 + z,
    ]
    initial_values = {x: 42, y: 43, z: 41}
    s = NewtonSolver(equations, initial_values)
    s.prepare_matrix()

    x_index = 0 if x == s.params[0] else 1 if x == s.params[1] else 2
    y_index = 0 if y == s.params[0] else 1 if y == s.params[1] else 2
    z_index = 0 if z == s.params[0] else 1 if z == s.params[1] else 2

    assert s.a[0][0] == 0
    assert s.a[0][1] == 0
    assert s.a[0][2] == 0
    assert s.a[1][0] == 0
    assert s.a[1][1] == 0
    assert s.a[1][2] == 0

    s._eval_jacobian()

    assert s.a[0][x_index] == 1
    assert s.a[0][y_index] == 42
    assert s.a[0][z_index] == 5043  # 3 * (41 ** 2)
    assert s.a[1][x_index] == 168  # 4 * 42
    assert s.a[1][y_index] == 86  # 2 * 43
    assert s.a[1][z_index] == 1


def test_compute_aat():
    x = symbols("x")
    y = symbols("y")
    z = symbols("z")
    equations = [
        x + y + z,
        x + y + z,
    ]
    initial_values = {x: 42, y: 43, z: 41}
    s = NewtonSolver(equations, initial_values)
    s.prepare_matrix()

    # Patch a by hand
    s.a[0][0] = 1
    s.a[0][1] = 2
    s.a[0][2] = 3
    s.a[1][0] = 4
    s.a[1][1] = 5
    s.a[1][2] = 6

    s._compute_aat()

    assert s.aat[0][0] == 14
    assert s.aat[0][1] == 32
    assert s.aat[1][0] == 32
    assert s.aat[1][1] == 77


def test_solve_linear_system():
    x = symbols("x")
    y = symbols("y")
    z = symbols("z")
    equations = [
        x + y + z,
        x + y + z,
    ]
    initial_values = {x: 42, y: 43, z: 41}
    s = NewtonSolver(equations, initial_values)
    s.prepare_matrix()

    # Patch a by hand
    s.aat[0][0] = 1
    s.aat[0][1] = 2
    s.aat[1][0] = 3
    s.aat[1][1] = 7

    s.b[0] = 42
    s.b[1] = 42

    assert s.z[0] == 0
    assert s.z[1] == 0

    s._solve_linear_system()

    assert equal_float(1 * s.z[0] + 2 * s.z[1], 42)
    assert equal_float(3 * s.z[0] + 7 * s.z[1], 42)


def test_solve_linear_system_2():
    x = symbols("x")
    y = symbols("y")
    z = symbols("z")
    equations = [
        x + y + z,
        x + y + z,
        x + y + z,
    ]
    initial_values = {x: 42, y: 43, z: 41}
    s = NewtonSolver(equations, initial_values)
    s.prepare_matrix()

    # Patch a by hand
    s.aat[0][0] = 42
    s.aat[0][1] = 1
    s.aat[0][2] = 2
    s.aat[1][0] = 3
    s.aat[1][1] = -2
    s.aat[1][2] = 18
    s.aat[2][0] = 4
    s.aat[2][1] = 5
    s.aat[2][2] = -6

    s.b[0] = 42
    s.b[1] = 42
    s.b[2] = 42

    s._solve_linear_system()

    assert equal_float(42 * s.z[0] + 1 * s.z[1] + 2 * s.z[2], 42)
    assert equal_float(3 * s.z[0] - 2 * s.z[1] + 18 * s.z[2], 42)
    assert equal_float(4 * s.z[0] + 5 * s.z[1] - 6 * s.z[2], 42)


def test_eval_b():
    x = symbols("x")
    y = symbols("y")
    z = symbols("z")
    equations = [
        x + y - z,
        x - y + z,
        x + y + z,
    ]
    initial_values = {x: 42, y: 43, z: 41}
    s = NewtonSolver(equations, initial_values)
    s.prepare_matrix()

    assert s.b[0] == 0
    assert s.b[1] == 0
    assert s.b[2] == 0

    s._eval_b()

    assert equal_float(s.b[0], 42 + 43 - 41)
    assert equal_float(s.b[1], 42 - 43 + 41)
    assert equal_float(s.b[2], 42 + 43 + 41)


def test_newton_solver():
    x = symbols("x")
    y = symbols("y")
    z = symbols("z")
    equations = [
        x + y - 5,
        2 * x - 3 * y,
    ]
    initial_values = {x: 0, y: 0}
    s = NewtonSolver(equations, initial_values)
    ret = s.solve()

    assert ret["solved"] is True
    x = ret["values"][x]
    y = ret["values"][y]
    assert x + y - 5 == 0
    assert 2 * x - 3 * y == 0


def test_newton_solver_basic_distance():
    x0 = symbols("x0")
    y0 = symbols("y0")
    z0 = symbols("z0")
    x1 = symbols("x1")
    y1 = symbols("y1")
    z1 = symbols("z1")
    equations = [sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2 + (z0 - z1) ** 2) - 30]
    initial_values = {x0: 10, y0: 10, z0: 10, x1: 20, y1: 20, z1: 20}
    s = NewtonSolver(equations, initial_values)

    ret = s.solve()
    assert ret["solved"]
    values = ret["values"]

    x0 = values[x0]
    y0 = values[y0]
    z0 = values[z0]
    x1 = values[x1]
    y1 = values[y1]
    z1 = values[z1]

    assert equal_float(math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2 + (z0 - z1) ** 2), 30)


def test_calculate_rank():
    x = symbols("x")
    y = symbols("y")
    z = symbols("z")
    equations = [
        x + y + z,
        x + y + z,
        x + y + z,
    ]
    initial_values = {x: 0, y: 0, z: 0}
    s = NewtonSolver(equations, initial_values)
    s.prepare_matrix()

    # Patch by hand
    s.a[0][0] = 42
    s.a[0][1] = 1
    s.a[0][2] = 2
    s.a[1][0] = 3
    s.a[1][1] = -3
    s.a[1][2] = -18
    s.a[2][0] = 4
    s.a[2][1] = 5
    s.a[2][2] = -6

    assert s.calculate_rank() == 3

    # Patch by hand
    s.a[0][0] = 1
    s.a[0][1] = 2
    s.a[0][2] = 3
    s.a[1][0] = 2
    s.a[1][1] = 4
    s.a[1][2] = 6
    s.a[2][0] = 4
    s.a[2][1] = 5
    s.a[2][2] = -6

    assert s.calculate_rank() == 2

    # Patch by hand
    s.a[0][0] = 1
    s.a[0][1] = 2
    s.a[0][2] = 3
    s.a[1][0] = 2
    s.a[1][1] = 4
    s.a[1][2] = 6
    s.a[2][0] = 4
    s.a[2][1] = 8
    s.a[2][2] = 12

    assert s.calculate_rank() == 1

    # Patch by hand
    s.a[0][0] = 0
    s.a[0][1] = 0
    s.a[0][2] = 0
    s.a[1][0] = 0
    s.a[1][1] = 0
    s.a[1][2] = 0
    s.a[2][0] = 0
    s.a[2][1] = 0
    s.a[2][2] = 0

    assert s.calculate_rank() == 0

    x = symbols("x")
    y = symbols("y")
    z = symbols("z")
    equations = [
        x + y + z,
        x + y + z,
    ]
    initial_values = {x: 0, y: 0, z: 0}
    s = NewtonSolver(equations, initial_values)
    s.prepare_matrix()

    # Patch by hand
    s.a[0][0] = 42
    s.a[0][1] = 1
    s.a[0][2] = 2
    s.a[1][0] = 3
    s.a[1][1] = -3
    s.a[1][2] = -18

    assert s.calculate_rank() == 2


def test_newton_solver_solve_by_substitution():
    x = symbols("x")
    y = symbols("y")
    z = symbols("z")
    equations = [
        x - y,
        2 * x - 3 * y + 5,
    ]
    initial_values = {x: 0, y: 0}
    s = NewtonSolver(equations, initial_values)
    s.solve_by_substitution()
    assert s.values[x] == 0
    assert s.values[y] == 0
    s.reduce_substitution()
    assert s.values[x] == 5
    assert s.values[y] == 5


def test_solver_parallel_fix():
    s = Solver(
        [
            MeshPoint(0, Vector3(0, 0, 0)),
            MeshPoint(1, Vector3(0, 10, 0)),
            MeshPoint(2, Vector3(5, 10, 5)),
            MeshPoint(3, Vector3(7, 8, 9)),
        ]
    )

    s.fix_x(42, 0, 0)
    s.fix_y(42, 0, 0)
    s.fix_z(42, 0, 0)

    s.fix_x(42, 1, 0)
    s.fix_y(42, 1, 10)
    s.fix_z(42, 1, 0)

    s.fix_x(42, 2, 5)
    s.fix_y(42, 2, 10)
    s.fix_z(42, 2, 5)

    s.parallel(42, 0, 1, 2, 3)

    ret = s.solve()

    assert ret["solved"]
    points = ret["points"]
    assert len(points) == 4
    p0 = points[0]
    p1 = points[1]
    p2 = points[2]
    p3 = points[3]

    assert p0.index == 0
    assert p1.index == 1
    assert p2.index == 2
    assert p3.index == 3

    assert equal_float(p0.x, 0)
    assert equal_float(p0.y, 0)
    assert equal_float(p0.z, 0)

    assert equal_float(p1.x, 0)
    assert equal_float(p1.y, 10)
    assert equal_float(p1.z, 0)

    assert equal_float(p2.x, 5)
    assert equal_float(p2.y, 10)
    assert equal_float(p2.z, 5)

    v0 = Vector3(p0.x, p0.y, p0.z) - Vector3(p1.x, p1.y, p1.z)
    v1 = Vector3(p2.x, p2.y, p2.z) - Vector3(p3.x, p3.y, p3.z)

    c = v0.cross(v1)

    assert equal_float(c.x, 0)
    assert equal_float(c.y, 0)
    assert equal_float(c.z, 0)


def test_solver_basic_distance():
    s = Solver([MeshPoint(0, Vector3(10, 10, 10)), MeshPoint(1, Vector3(20, 20, 20)),])
    s.distance_2_vertices(42, 0, 1, 30)
    ret = s.solve()
    assert ret["solved"]
    points = ret["points"]
    assert len(points) == 2
    p0 = points[0]
    p1 = points[1]
    distance = math.sqrt((p0.x - p1.x) ** 2 + (p0.y - p1.y) ** 2 + (p0.z - p1.z) ** 2)
    assert equal_float(distance, 30)


def test_solver_basic_distance_fix():
    s = Solver([MeshPoint(0, Vector3(10, 10, 10)), MeshPoint(1, Vector3(20, 20, 20)),])
    s.distance_2_vertices(42, 0, 1, 30)
    s.fix_x(42, 0, 10)
    s.fix_z(42, 1, 20)
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
    s = Solver([MeshPoint(0, Vector3(10, 10, 10)), MeshPoint(1, Vector3(20, 20, 20)),])
    s.distance_2_vertices(42, 0, 1, 30)
    s.fix_x(43, 0, 10)
    s.fix_y(43, 0, 10)
    s.fix_z(43, 0, 10)
    s.fix_x(44, 1, 20)
    s.fix_y(44, 1, 20)
    s.fix_z(44, 1, 20)
    ret = s.solve()
    assert ret["solved"] == False


def test_solver_low_rank():
    s = Solver([MeshPoint(0, Vector3(10, 10, 10)), MeshPoint(1, Vector3(20, 20, 20)),])
    s.distance_2_vertices(42, 0, 1, 30)
    s.distance_2_vertices(43, 0, 1, 20)
    ret = s.solve()
    assert ret["solved"] == False


def test_solver_perpendicular():
    s = Solver(
        [
            MeshPoint(0, Vector3(0, 0, 0)),
            MeshPoint(1, Vector3(10, 10, 10)),
            MeshPoint(2, Vector3(5, 10, 5)),
            MeshPoint(3, Vector3(7, 8, 9)),
        ]
    )

    s.fix_x(42, 0, 0)
    s.fix_y(42, 0, 0)
    s.fix_z(42, 0, 0)

    s.fix_x(42, 1, 10)
    s.fix_y(42, 1, 10)
    s.fix_z(42, 1, 10)

    s.fix_x(42, 2, 5)
    s.fix_y(42, 2, 10)
    s.fix_z(42, 2, 5)

    s.perpendicular(42, 0, 1, 2, 3)

    ret = s.solve()

    assert ret["solved"]
    points = ret["points"]
    assert len(points) == 4
    p0 = points[0]
    p1 = points[1]
    p2 = points[2]
    p3 = points[3]

    assert p0.index == 0
    assert p1.index == 1
    assert p2.index == 2
    assert p3.index == 3

    assert equal_float(p0.x, 0)
    assert equal_float(p0.y, 0)
    assert equal_float(p0.z, 0)

    assert equal_float(p1.x, 10)
    assert equal_float(p1.y, 10)
    assert equal_float(p1.z, 10)

    assert equal_float(p2.x, 5)
    assert equal_float(p2.y, 10)
    assert equal_float(p2.z, 5)

    v0 = Vector3(p0.x, p0.y, p0.z) - Vector3(p1.x, p1.y, p1.z)
    v1 = Vector3(p2.x, p2.y, p2.z) - Vector3(p3.x, p3.y, p3.z)

    d = v0.dot(v1)

    assert equal_float(d, 0)


def test_solver_on_x():
    s = Solver([MeshPoint(0, Vector3(0, 0, 0)), MeshPoint(1, Vector3(10, 10, 10)),])

    s.fix_x(42, 0, 0)
    s.fix_y(42, 0, 0)
    s.fix_z(42, 0, 0)

    s.on_x(42, 0, 1)

    ret = s.solve()

    assert ret["solved"]
    points = ret["points"]
    assert len(points) == 2
    p0 = points[0]
    p1 = points[1]

    assert p0.index == 0
    assert p1.index == 1

    assert equal_float(p0.x, 0)
    assert equal_float(p0.y, 0)
    assert equal_float(p0.z, 0)

    assert equal_float(p1.y, p0.y)
    assert equal_float(p1.z, p0.z)


def test_solver_on_y():
    s = Solver([MeshPoint(0, Vector3(0, 0, 0)), MeshPoint(1, Vector3(10, 10, 10)),])

    s.fix_x(42, 0, 0)
    s.fix_y(42, 0, 0)
    s.fix_z(42, 0, 0)

    s.on_y(42, 0, 1)

    ret = s.solve()

    assert ret["solved"]
    points = ret["points"]
    assert len(points) == 2
    p0 = points[0]
    p1 = points[1]

    assert p0.index == 0
    assert p1.index == 1

    assert equal_float(p0.x, 0)
    assert equal_float(p0.y, 0)
    assert equal_float(p0.z, 0)

    assert equal_float(p1.x, p0.x)
    assert equal_float(p1.z, p0.z)


def test_solver_on_z():
    s = Solver([MeshPoint(0, Vector3(0, 0, 0)), MeshPoint(1, Vector3(10, 10, 10)),])

    s.fix_x(42, 0, 0)
    s.fix_y(42, 0, 0)
    s.fix_z(42, 0, 0)

    s.on_z(42, 0, 1)

    ret = s.solve()

    assert ret["solved"]
    points = ret["points"]
    assert len(points) == 2
    p0 = points[0]
    p1 = points[1]

    assert p0.index == 0
    assert p1.index == 1

    assert equal_float(p0.x, 0)
    assert equal_float(p0.y, 0)
    assert equal_float(p0.z, 0)

    assert equal_float(p1.x, p0.x)
    assert equal_float(p1.y, p0.y)


def test_solver_avoid_loop_in_substitutes():
    s = Solver(
        [
            MeshPoint(0, Vector3(-1.1291875839233398, -1.1657862663269043, -1.2977023124694824)),
            MeshPoint(1, Vector3(-1.1291875839233398, -1.1657862663269043, 0.8831915855407715)),
            MeshPoint(2, Vector3(-1.1291875839233398, 0.6939811706542969, -0.9495291113853455)),
            MeshPoint(3, Vector3(-1.1291875839233398, 0.6939811706542969, 1.0)),
            MeshPoint(4, Vector3(1.5113141536712646, -1.1657862663269043, -1.2977023124694824)),
            MeshPoint(5, Vector3(1.5113141536712646, -1.1657862663269043, -1.1214728355407715)),
            MeshPoint(6, Vector3(1.5113141536712646, 0.6939811706542969, -1.2977023124694824)),
            MeshPoint(7, Vector3(1.5113141536712646, 0.6939811706542969, -0.7355250120162964)),
            MeshPoint(8, Vector3(0.17407408356666565, 0.8677473068237305, -1.465881109237671)),
        ]
    )

    s.on_z(0, 5, 4)
    s.fix_x(1, 6, s.points[6].x)
    s.fix_y(1, 6, s.points[6].y)
    s.fix_z(1, 6, s.points[6].z)
    s.on_z(2, 7, 6)
    s.on_y(3, 4, 6)
    s.on_y(4, 7, 5)
    s.on_z(5, 3, 2)
    s.on_x(6, 3, 7)
    s.on_y(7, 1, 3)
    s.parallel(8, 0, 1, 3, 2)
    s.on_x(9, 5, 1)
    s.parallel(10, 0, 4, 5, 1)

    ret = s.solve()

    assert ret["solved"]
    points = ret["points"]
    # 0
    assert equal_float(points[5].x, points[4].x)
    assert equal_float(points[5].y, points[4].y)
    # 1
    assert equal_float(points[6].x, 1.5113141536712646)
    assert equal_float(points[6].y, 0.6939811706542969)
    assert equal_float(points[6].z, -1.2977023124694824)
    # 2
    assert equal_float(points[7].x, points[6].x)
    assert equal_float(points[7].y, points[6].y)
    # 3
    assert equal_float(points[4].x, points[6].x)
    assert equal_float(points[4].z, points[6].z)
    # 4
    assert equal_float(points[7].x, points[5].x)
    assert equal_float(points[7].z, points[5].z)
    # 5
    assert equal_float(points[3].x, points[2].x)
    assert equal_float(points[3].y, points[2].y)
    # 6
    assert equal_float(points[3].z, points[7].z)
    assert equal_float(points[3].y, points[7].y)
    # 7
    assert equal_float(points[3].z, points[1].z)
    assert equal_float(points[3].x, points[1].x)
    # 8 parallel means cross product = 0
    v0 = Vector3(*points[0].xyz) - Vector3(*points[1].xyz)
    v1 = Vector3(*points[3].xyz) - Vector3(*points[2].xyz)
    cross = v0.cross(v1)
    assert equal_float(cross.x, 0)
    assert equal_float(cross.y, 0)
    assert equal_float(cross.z, 0)
    # 9
    assert equal_float(points[5].y, points[1].y)
    assert equal_float(points[5].z, points[1].z)
    # 10 parallel means cross product = 0
    v0 = Vector3(*points[0].xyz) - Vector3(*points[4].xyz)
    v1 = Vector3(*points[5].xyz) - Vector3(*points[1].xyz)
    cross = v0.cross(v1)
    assert equal_float(cross.x, 0)
    assert equal_float(cross.y, 0)
    assert equal_float(cross.z, 0)


def test_solver_same_distance():
    s = Solver([MeshPoint(0, Vector3(10, 10, 10)), MeshPoint(1, Vector3(20, 20, 20)),
MeshPoint(2, Vector3(11, 11, 11)), MeshPoint(3, Vector3(21, 22, 23)),
                ])
    s.same_distance(42, 0, 1, 2, 3)
    ret = s.solve()
    assert ret["solved"]
    points = ret["points"]
    assert len(points) == 4
    p0 = points[0]
    p1 = points[1]
    p2 = points[2]
    p3 = points[3]
    d1 = math.sqrt((p0.x - p1.x) ** 2 + (p0.y - p1.y) ** 2 + (p0.z - p1.z) ** 2)
    d2 = math.sqrt((p2.x - p3.x) ** 2 + (p2.y - p3.y) ** 2 + (p2.z - p3.z) ** 2)
    assert equal_float(d1, d2)
