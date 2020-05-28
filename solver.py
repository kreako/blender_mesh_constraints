# constraint parameters are whatever and will be used to report problems with constraint
#
# point parameters are indices of the mesh, in fact not really used by the solver,
# index is a nice and practical way to track parameters of the solver

import itertools
import sys
import math
from mathutils import Vector


sys.path.append("/home/noumir/.local/lib/python3.8/site-packages")
from sympy import symbols, sqrt, diff
from sympy.matrices import Matrix
import mpmath

EPSILON = 1e-6
CONVERGENCE_TOLERANCE = 1e-8
VERY_POSITIVE = 1e10
VERY_NEGATIVE = -1e10
MAX_ITERATIONS = 50
RANK_MAG_TOLERANCE = 1e-4


def is_not_reasonable(x):
    math.isnan(x) or x > VERY_POSITIVE or x < VERY_NEGATIVE


class NewtonSolver:
    def __init__(self, equations, initial_values):
        """Build a NewtonSolver around :
        - equations: list of equations
        - initial_values: dict params -> values"""
        self.equations = equations

        # First build list of params
        params = set()
        for eq in equations:
            params = params.union(eq.free_symbols)
        self.params = list(params)

        # Build values for the params and check I have initial values
        # for all my parameters
        self.values = {}
        for param in params:
            if param not in initial_values:
                raise Exception(f"Param '{param}' is not in initial_values dict")
            self.values[param] = initial_values[param]

        # For parameters being substitutes (simple equations)
        self.substitutes = {}

    def prepare_matrix(self):
        # For A and B dimensions
        self.nb_params = len(self.params)
        self.nb_equations = len(self.equations)

        # Jacobian is rows * cols = nb_equations * nb_params
        # Equations part
        self.a_eq = [
            [diff(self.equations[i], self.params[j]) for j in range(self.nb_params)]
            for i in range(self.nb_equations)
        ]
        # Values part
        self.a = [[0 for j in range(self.nb_params)] for i in range(self.nb_equations)]

        # Value of equations values on current point
        self.b = [0 for i in range(self.nb_equations)]

        # Temps for _solve_least_squares
        # a @ a' square matrix of size nb_equations
        self.aat = [
            [0 for j in range(self.nb_equations)] for i in range(self.nb_equations)
        ]
        # z is a column vector of size nb_equations
        self.z = [0 for i in range(self.nb_equations)]
        # x is a column vector of size nb_params
        self.x = [0 for i in range(self.nb_params)]

    def _eval_jacobian(self):
        """Evaluate jacobian with the current values"""
        for i in range(self.nb_equations):
            for j in range(self.nb_params):
                self.a[i][j] = self.a_eq[i][j].evalf(subs=self.values)

    def _eval_b(self):
        """Evaluate b with the current values"""
        for i in range(self.nb_equations):
            self.b[i] = self.equations[i].evalf(subs=self.values)

    def _compute_aat(self):
        """Compute value of a * a.transpose() and push results in self.aat"""
        for r in range(self.nb_equations):
            for c in range(self.nb_equations):
                s = 0
                for i in range(self.nb_params):
                    s += self.a[r][i] * self.a[c][i]
                self.aat[r][c] = s

    def _solve_linear_system(self):
        """Solve the system self.aat * self.z = self.b, for z
        by gaussian elimination with partial pivoting"""
        for i in range(self.nb_equations):
            # Try to eliminate term in column i for rows > i
            # First find pivot for rows >= i
            vmax = 0
            imax = 0
            for ip in range(i, self.nb_equations):
                if abs(self.aat[ip][i]) > vmax:
                    imax = ip
                    vmax = abs(self.aat[ip][i])

            if abs(vmax) < 1e-20:
                # Maybe a singular matrix, but I don't care
                # my job here is done : column i term is already 0
                continue

            # Swap for pivot row imax <-> i
            for j in range(self.nb_equations):
                self.aat[i][j], self.aat[imax][j] = self.aat[imax][j], self.aat[i][j]
            self.b[i], self.b[imax] = self.b[imax], self.b[i]

            # Now term elimination in column i for rows > i+1 (because row i is the row of the pivot)
            for ip in range(i + 1, self.nb_equations):
                frac = self.aat[ip][i] / self.aat[i][i]
                for jp in range(i, self.nb_equations):
                    self.aat[ip][jp] -= frac * self.aat[i][jp]
                self.b[ip] -= frac * self.b[i]

        # Now aat is in triangular shape with lower half = 0
        # It is time for backward substitution
        for i in range(self.nb_equations - 1, -1, -1):
            if abs(self.aat[i][i]) < 1e-20:
                # The factor for this parameter is 0
                # So I won't be able to do anything with it
                # Just continue for the others
                # Same type of strategy as 10 lines up
                continue

            t = self.b[i]
            for j in range(self.nb_equations - 1, i, -1):
                # Add already solved parameters
                t -= self.z[j] * self.aat[i][j]

            self.z[i] = t / self.aat[i][i]

    def _solve_least_squares(self):
        # compute aat
        self._compute_aat()
        # Gauss linear system solving z, for aat * z = b
        self._solve_linear_system()
        # now multiply z by aT for the solution
        for c in range(self.nb_params):
            s = 0
            for i in range(self.nb_equations):
                s += self.a[i][c] * self.z[i]
            self.x[c] = s

    def test_rank(self):
        """Test rank of the current jacobian.
        Designed to be called just after solve
        returning rank_ok (True if rank == number of rows) and rank"""
        # At the end of solve, the jacobian is not up to date
        # with the last values so update it
        self._eval_jacobian()
        rank = self.calculate_rank()
        return rank == self.nb_equations, rank

    def calculate_dof(self):
        """Return the number of degrees of freedom
        Used it only when rank of jacobian == number of equations (number of rows)
        (When self.test_rank returns True, X
        """
        return self.nb_params - self.nb_equations

    def calculate_rank(self):
        """Calculate the rank of the Jacobian matrix, by Gram-Schimdt orthogonalization
        in place. A row (~equation) is considered to be all zeros if its magnitude
        is less than the tolerance RANK_MAG_TOLERANCE."""
        tolerance = RANK_MAG_TOLERANCE * RANK_MAG_TOLERANCE
        rowMagnitude = [0 for _ in range(self.nb_equations)]

        rank = 0

        for i in range(self.nb_equations):
            # Subtract off this row's component in the direction of any previous rows
            for iprev in range(i):
                if rowMagnitude[iprev] < tolerance:
                    # ignore zero rows
                    continue

                dot = 0
                for j in range(self.nb_params):
                    dot += self.a[iprev][j] * self.a[i][j]

                for j in range(self.nb_params):
                    self.a[i][j] -= (dot / rowMagnitude[iprev]) * self.a[iprev][j]

            # Our row is now normal to all previous rows; calculate the
            # magnitude of what's left
            mag = 0
            for j in range(self.nb_params):
                mag += self.a[i][j] * self.a[i][j]

            if mag > tolerance:
                rank += 1

            rowMagnitude[i] = mag

        return rank

    def solve_by_substitution(self):
        # Build dict of possible substitute
        substitutes = {}
        for equation in self.equations:
            # Looking for equations in form of
            # * x - y with x and y both symbols
            # * x - 42 with x symbol, 42 a values
            if not equation.is_Add:
                continue
            coeff, args = equation.as_coeff_add()
            if len(args) == 1:
                # This is maybe a x - 42 type with x in args and 42 in coeff
                if coeff.is_real:
                    a0 = args[0]
                    if a0.is_symbol:
                        # We have a winner
                        substitutes[args[0]] = -coeff
                    if a0.is_Mul:
                        # Is this 42 + mul_coeff * x ?
                        mul_coeff, mul_args = a0.as_coeff_mul()
                        if len(mul_args) != 1:
                            continue
                        mul_sym = mul_args[0]
                        if not mul_sym.is_symbol:
                            continue
                        # We have a winner
                        substitutes[mul_sym] = -coeff / mul_coeff
            elif len(args) == 2:
                # This could be a x - 42.3 or a x - y
                if coeff != 0:
                    continue
                a0, a1 = args
                if a0.is_real and a1.is_symbol:
                    # We have a winner
                    substitutes[a1] = -a0
                if a0.is_symbol and a1.is_Mul:
                    # Is this x - mul_coeff * y ?
                    mul_coeff, mul_args = a1.as_coeff_mul()
                    if len(mul_args) != 1:
                        continue
                    mul_sym = mul_args[0]
                    if not mul_sym.is_symbol:
                        continue
                    # We have a winner
                    substitutes[a0] = -mul_coeff * mul_sym

        # Now substitute
        for i in range(len(self.equations)):
            self.equations[i] = self.equations[i].subs(substitutes)

        # Register substitutes for futures use
        self.substitutes.update(substitutes)

        # Remove substitutes from params
        for param in substitutes:
            self.params.remove(param)

        # return number of substitution done
        return len(substitutes)

    def _solve(self):
        # Prepare matrix for solving storage
        self.prepare_matrix()
        # Eval b now : values of equations with current values
        self._eval_b()
        count = 0
        while True:
            # Eval jacobian with current values
            self._eval_jacobian()

            # Solve with least squares
            self._solve_least_squares()

            # Use solutions in X to move param values, this is the newton step
            # x(n+1) - x(n) = 0 - F(x(n))
            for i in range(self.nb_params):
                param = self.params[i]
                self.values[param] -= self.x[i]
                if is_not_reasonable(self.values[param]):
                    return {
                        "solved": False,
                        "reason": "not_reasonable",
                        "source": "params",
                        "index": i,
                    }

            # Eval b now that values have changed
            self._eval_b()

            # Check convergence criteria in b
            converged = True
            for i in range(self.nb_equations):
                b = self.b[i]
                if is_not_reasonable(b):
                    return {
                        "solved": False,
                        "reason": "not_reasonable",
                        "source": "b",
                        "index": i,
                    }
                if abs(b) > CONVERGENCE_TOLERANCE:
                    converged = False
                    break

            if converged:
                return {"solved": True}

            if count > MAX_ITERATIONS:
                return {"solved": False, "reason": "count_over_max_iterations"}

            count += 1

    def reduce_substitution(self):
        # First substitute every values computed by _solve
        for param in self.values:
            if param in self.substitutes:
                continue
            for substitute in self.substitutes:
                self.substitutes[substitute] = self.substitutes[substitute].subs(
                    {param: self.values[param]}
                )

        # Now substitute what's left, in a loop in case there is some cross dependencies between them
        while True:
            done = set()
            for substitute in self.substitutes:
                value = self.substitutes[substitute]
                if value.is_real:
                    self.values[substitute] = value
                    done.add(substitute)

            for substitute in self.substitutes:
                for d in done:
                    self.substitutes[substitute] = self.substitutes[substitute].subs(
                        {d: self.substitutes[d]}
                    )

            for d in done:
                del self.substitutes[d]

            if len(done) == 0:
                break

    def solve(self):
        # Substitutes all I can first
        while True:
            i = self.solve_by_substitution()
            if i == 0:
                break
        # Non substituted parts
        if len(self.equations) > 0:
            ret = self._solve()
        if ret["solved"]:
            rank_ok, rank = self.test_rank()
            dof = None
            if rank_ok:
                dof = self.calculate_dof()
            self.reduce_substitution()
            return {"solved": True, "values": self.values, "dof": dof, "rank_ok": rank_ok, "rank": rank}
        else:
            # Error find out which one of the equations are problematics
            equations_in_error = set()
            for i in range(self.nb_equations):
                if self.b[i] > CONVERGENCE_TOLERANCE or is_not_reasonable(self.b[i]):
                    equations_in_error.add(i)
            ret["equations_in_error"] = equations_in_error
            return ret


class MeshPoint:
    def __init__(self, index, co):
        self.index = index
        self.x_value = co.x
        self.y_value = co.y
        self.z_value = co.z
        self.x_param = symbols(f"{self.index}.x")
        self.y_param = symbols(f"{self.index}.y")
        self.z_param = symbols(f"{self.index}.z")

    @property
    def xyz(self):
        return (self.x_value, self.y_value, self.z_value)

    @property
    def x(self):
        return self.x_value

    @property
    def y(self):
        return self.y_value

    @property
    def z(self):
        return self.z_value

    @property
    def params(self):
        return (self.x_param, self.y_param, self.z_param)

    def __repr__(self):
        return (
            f"MeshPoint({self.index}, {self.x_value}, {self.y_value}, {self.z_value})"
        )


class Solver:
    """Solver functionnality"""

    def __init__(self, points):
        # List of mesh points
        self.points = points

        # List of parameters from list of mesh points
        self.params = list(itertools.chain(*[pt.params for pt in self.points]))
        # List of values - same index as the param
        self.values = list(itertools.chain(*[pt.xyz for pt in self.points]))
        # Dict of initial values
        self.initial_values = {}
        for i in range(len(self.params)):
            self.initial_values[self.params[i]] = self.values[i]

        # List of equations
        self.equations = []
        # equations index -> constraint
        self.equations_constraints = {}

    def _add_equation(self, constraint, equation):
        self.equations.append(equation)
        index = len(self.equations) - 1
        self.equations_constraints[index] = constraint

    def distance_2_vertices(self, constraint, point0, point1, distance):
        """Add a distance constraint between 2 vertices"""
        p0 = self.points[point0]
        p1 = self.points[point1]
        x0, y0, z0 = p0.x_param, p0.y_param, p0.z_param
        x1, y1, z1 = p1.x_param, p1.y_param, p1.z_param
        self._add_equation(
            constraint,
            sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2 + (z0 - z1) ** 2) - distance,
        )

    def fix_x(self, constraint, point, x_value):
        """Add a fix x coordinate constraint"""
        p = self.points[point]
        self._add_equation(constraint, p.x_param - x_value)

    def fix_y(self, constraint, point, y_value):
        """Add a fix y coordinate constraint"""
        p = self.points[point]
        self._add_equation(constraint, p.y_param - y_value)

    def fix_z(self, constraint, point, z_value):
        """Add a fix z coordinate constraint"""
        p = self.points[point]
        self._add_equation(constraint, p.z_param - z_value)

    def parallel(self, constraint, point0, point1, point2, point3):
        """Add a parallel constraint between p0-p1 and p2-p3"""
        p0 = self.points[point0]
        p1 = self.points[point1]
        p2 = self.points[point2]
        p3 = self.points[point3]

        # v0 : vector p0-p1
        v0x = p1.x_param - p0.x_param
        v0y = p1.y_param - p0.y_param
        v0z = p1.z_param - p0.z_param

        # v1 : vector p2-p3
        v1x = p3.x_param - p2.x_param
        v1y = p3.y_param - p2.y_param
        v1z = p3.z_param - p2.z_param

        # Cross product of v0 and v1 = Vector(0, 0, 0)
        self._add_equation(constraint, v0y * v1z - v0z * v1y)
        self._add_equation(constraint, v0z * v1x - v0x * v1z)
        self._add_equation(constraint, v0x * v1y - v0y * v1x)

    def solve(self):
        """Solve and return an object representing the solve operation with
        - "solved" boolean, True if the solve process is a success
        - "points", if "solved" is True, list of MeshPoint with up to date values
        - "reason", if "solved" is False, try to explain why it failed
        - "equations_in_error", if "solved" is False, list of equations in error"""
        newton_solver = NewtonSolver(self.equations, self.initial_values)
        ret = newton_solver.solve()
        if ret["solved"]:
            values = ret["values"]
            # merge values in a list of MeshPoint
            for point in self.points:
                point.x_value = values.get(point.x_param, point.x_value)
                point.y_value = values.get(point.y_param, point.y_value)
                point.z_value = values.get(point.z_param, point.z_value)
            ret["points"] = self.points
            # TODO if rank_ok is False maybe I want
            # self.find_which_to_remove_to_fix_jacobian() ?
            del ret["values"]
            return ret
        else:
            # solve failed :(
            ret["equations_in_error"] = [self.equations_constraints[i] for i in ret["equations_in_error"]]
            return ret

    def find_which_to_remove_to_fix_jacobian():
        # TODO
        raise Exception("TODO")
