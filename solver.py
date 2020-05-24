# constraint parameters are whatever and will be used to report problems with constraint
#
# point parameters are indices of the mesh, in fact not really used by the solver,
# index is a nice and practical way to track parameters of the solver

import itertools
import sys
from mathutils import Vector


sys.path.append("/home/noumir/.local/lib/python3.8/site-packages")
from sympy import symbols, sqrt, diff
from sympy.matrices import Matrix


class Point:
    def __init__(self, index, x, y, z):
        self.index = index
        self.x = x
        self.y = y
        self.z = z

    @property
    def xyz(self):
        return (self.x, self.y, self.z)


class Solver:
    """Solver functionnality"""

    def __init__(self):
        # point index -> coord -> value
        self.values = {}
        # point index -> coord -> symbol
        self.params = {}
        # constraint -> [equations...]
        self.equations = {}
        # Special fix equations that can be easily substituted
        # constraint -> params -> value
        self.fix_equations = {}

    def _register_point(self, point, point_initial_value):
        if point not in self.values:
            self.values[point] = {}
            self.values[point]["x"] = point_initial_value.x
            self.values[point]["y"] = point_initial_value.y
            self.values[point]["z"] = point_initial_value.z
        if point not in self.params:
            self.params[point] = {}
            self.params[point]["x"] = symbols(f"{point}.x")
            self.params[point]["y"] = symbols(f"{point}.y")
            self.params[point]["z"] = symbols(f"{point}.z")

    def distance_2_vertices(self, constraint, p0, p0_ival, p1, p1_ival, distance):
        """Add a distance constraint between 2 vertices"""
        self._register_point(p0, p0_ival)
        self._register_point(p1, p1_ival)
        p0 = self.params[p0]
        x0, y0, z0 = p0["x"], p0["y"], p0["z"]
        p1 = self.params[p1]
        x1, y1, z1 = p1["x"], p1["y"], p1["z"]
        self.equations[constraint] = sqrt((x0 -x1) ** 2 + (y0 - y1) ** 2 + (z0 - z1) ** 2) - distance

    def fix_x(self, constraint, point, point_ival, x):
        """Add a fix x coordinate constraint"""
        self._register_point(point, point_ival)
        x_param = self.params[point]["x"]
        if constraint not in self.fix_equations:
            self.fix_equations[constraint] = {}
        self.fix_equations[constraint][x_param] = x

    def fix_y(self, constraint, point, point_ival, y):
        """Add a fix y coordinate constraint"""
        self._register_point(point, point_ival)
        y_param = self.params[point]["y"]
        if constraint not in self.fix_equations:
            self.fix_equations[constraint] = {}
        self.fix_equations[constraint][y_param] = y

    def fix_z(self, constraint, point, point_ival, z):
        """Add a fix z coordinate constraint"""
        self._register_point(point, point_ival)
        z_param = self.params[point]["z"]
        if constraint not in self.fix_equations:
            self.fix_equations[constraint] = {}
        self.fix_equations[constraint][z_param] = z

    def solve(self):
        """Solve and return an object representing the solve operation"""
        # TODO substitute fix equations

        # Solve AX = B, searching X
        # with A the value of the jacobian
        # with B each equations value on current point

        # Build list of equations
        equations = []
        for _, equation in self.equations.items():
            equations.append(equation)
        for _, values in self.fix_equations.items():
            for param, value in values.items():
                equations.append(param - value)
        print("equations", equations)

        # params -> values
        params_values = {}
        # params -> (point index, coord)
        params_index_coord = {}
        # params list
        params = []
        for index, coords_dict in self.params.items():
            for coord, param in coords_dict.items():
                params_index_coord[param] = (index, coord)
                params_values[param] = self.values[index][coord]
                params.append(param)

        # For matrix dimensions
        nb_params = len(params)
        nb_equations = len(equations)

        # Values of equations on current point
        b = Matrix(1, nb_equations, [0] * nb_equations)
        for i in range(nb_equations):
            b[0, i] = equations[i].evalf(subs=params_values)
        print("b", b.shape, b)

        # Build jacobian
        # The equation part
        a_eq = Matrix(nb_params, nb_equations, [0] * (nb_params * nb_equations))
        # The value part
        a = Matrix(nb_params, nb_equations, [0] * (nb_params * nb_equations))
        for i in range(nb_params):
            for j in range(nb_equations):
                a_eq[i, j] = diff(equations[j], params[i])
        print("a_eq", a_eq.shape, a_eq)

        count = 0

        while True:
            # And let's begin the big show of solver iterations

            # Eval jacobian on point
            for i in range(nb_params):
                for j in range(nb_equations):
                    a[i, j] = a_eq[i, j].evalf(subs=params_values)

            # Transpose
            at = a.transpose()
            aat = at * a
            bt = b.transpose()

            # LU Solve
            z = aat.LUsolve(bt)

            # Compute X
            zt = z.transpose()
            x = zt * at

            # Move values
            for i, param in enumerate(params):
                params_values[param] -= x[0, i]

            # Values of equations on current point
            done = True
            for i in range(nb_equations):
                e_eval = equations[i].evalf(subs=params_values)
                b[0, i] = e_eval
                if e_eval > 1e-4:
                    # To big to quit, continue
                    done = False

            if done:
                break

            count += 1
            if count > 50:
                # Over 50 ? probably a convergence error
                break

        if done:
            points_index_coord = {}
            for param, value in params_values.items():
                index, coord = params_index_coord[param]
                if index not in points_index_coord:
                    points_index_coord[index] = {}
                points_index_coord[index][coord] = value

            points = []
            for index, d in points_index_coord.items():
                points.append(Point(index, d["x"], d["y"], d["z"]))

            return {"solved": True, "points": points}
        else:
            return {"solved": False, "error": "Convergence error"}