from enum import Enum, unique
from bpy.types import PropertyGroup
from bpy.props import (
    CollectionProperty,
    EnumProperty,
    IntProperty,
    FloatVectorProperty,
    FloatProperty,
    BoolProperty,
)


@unique
class ConstraintsKind(Enum):
    UNKNOWN = "0"
    DISTANCE_BETWEEN_2_VERTICES = "1"
    FIX_X_COORD = "2"
    FIX_Y_COORD = "3"
    FIX_Z_COORD = "4"
    FIX_XY_COORD = "5"
    FIX_YZ_COORD = "6"
    FIX_XZ_COORD = "7"
    FIX_XYZ_COORD = "8"
    PARALLEL = "9"
    PERPENDICULAR = "10"
    ON_X = "11"
    ON_Y = "12"
    ON_Z = "13"
    SAME_DISTANCE = "14"
    ANGLE = "15"


# For kind EnumProperty
constraints_kind_items = [
    (k.value, " ".join(s.lower() for s in k.name.split("_")), "")
    for k in ConstraintsKind
]

# For full display
constraints_kind_display = {
    k: " ".join(s.lower() for s in k.name.split("_")) for k in ConstraintsKind
}

# For abbreviation display
constraints_kind_abbreviation = {
    ConstraintsKind.UNKNOWN: "?",
    ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES: "Dist.",
    ConstraintsKind.FIX_X_COORD: "FixX",
    ConstraintsKind.FIX_Y_COORD: "FixY",
    ConstraintsKind.FIX_Z_COORD: "FixZ",
    ConstraintsKind.FIX_XY_COORD: "FixXY",
    ConstraintsKind.FIX_YZ_COORD: "FixYZ",
    ConstraintsKind.FIX_XZ_COORD: "FixXZ",
    ConstraintsKind.FIX_XYZ_COORD: "FixXYZ",
    ConstraintsKind.PARALLEL: "Para.",
    ConstraintsKind.PERPENDICULAR: "Perp.",
    ConstraintsKind.ON_X: "On X",
    ConstraintsKind.ON_Y: "On Y",
    ConstraintsKind.ON_Z: "On Z",
    ConstraintsKind.SAME_DISTANCE: "Dist. =",
    ConstraintsKind.ANGLE: "Angle",
}


class MeshConstraintProperties(PropertyGroup):
    # Data of the constraint
    kind: EnumProperty(
        items=constraints_kind_items, name="Kind", description="Kind of constraints"
    )
    point0: IntProperty(name="point0", description="Point 0 of the constraint")
    point1: IntProperty(name="point1", description="Point 1 of the constraint")
    point2: IntProperty(name="point2", description="Point 2 of the constraint")
    point3: IntProperty(name="point3", description="Point 3 of the constraint")
    value0: FloatProperty(name="value0", description="Value 0 of the constraint")
    value1: FloatProperty(name="value1", description="Value 1 of the constraint")
    value2: FloatProperty(name="value2", description="Value 2 of the constraint")
    in_error: BoolProperty(
        name="in_error", description="Constraint in error after solve"
    )
    # View related
    view: BoolProperty(name="view", description="Show/hide in 3D view", default=True)
    show_details: BoolProperty(
        name="show_details", description="Show/hide details in panel", default=False
    )


class MeshConstraintsContainer(PropertyGroup):
    constraints: CollectionProperty(type=MeshConstraintProperties)


class PropsException(Exception):
    pass


class Constraint:
    def __init__(self, constraint_properties):
        self.kind = ConstraintsKind(constraint_properties.kind)
        self.data = {
            "in_error": constraint_properties.in_error,
            "view": constraint_properties.view,
            "show_details": constraint_properties.show_details,
        }
        # Nb of values used by the constraint, default to 1 - the most common
        self.nb_values = 1
        self.raw = constraint_properties
        if self.kind == ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES:
            self.data["point0"] = constraint_properties.point0
            self.data["point1"] = constraint_properties.point1
            self.data["distance"] = constraint_properties.value0
        elif self.kind == ConstraintsKind.FIX_X_COORD:
            self.data["point"] = constraint_properties.point0
            self.data["x"] = constraint_properties.value0
        elif self.kind == ConstraintsKind.FIX_Y_COORD:
            self.data["point"] = constraint_properties.point0
            self.data["y"] = constraint_properties.value0
        elif self.kind == ConstraintsKind.FIX_Z_COORD:
            self.data["point"] = constraint_properties.point0
            self.data["z"] = constraint_properties.value0
        elif self.kind == ConstraintsKind.FIX_XY_COORD:
            self.data["point"] = constraint_properties.point0
            self.data["x"] = constraint_properties.value0
            self.data["y"] = constraint_properties.value1
            self.nb_values = 2
        elif self.kind == ConstraintsKind.FIX_XZ_COORD:
            self.data["point"] = constraint_properties.point0
            self.data["x"] = constraint_properties.value0
            self.data["z"] = constraint_properties.value1
            self.nb_values = 2
        elif self.kind == ConstraintsKind.FIX_YZ_COORD:
            self.data["point"] = constraint_properties.point0
            self.data["y"] = constraint_properties.value0
            self.data["z"] = constraint_properties.value1
            self.nb_values = 2
        elif self.kind == ConstraintsKind.FIX_XYZ_COORD:
            self.data["point"] = constraint_properties.point0
            self.data["x"] = constraint_properties.value0
            self.data["y"] = constraint_properties.value1
            self.data["z"] = constraint_properties.value2
            self.nb_values = 3
        elif self.kind == ConstraintsKind.PARALLEL:
            self.data["point0"] = constraint_properties.point0
            self.data["point1"] = constraint_properties.point1
            self.data["point2"] = constraint_properties.point2
            self.data["point3"] = constraint_properties.point3
            self.nb_values = 0
        elif self.kind == ConstraintsKind.PERPENDICULAR:
            self.data["point0"] = constraint_properties.point0
            self.data["point1"] = constraint_properties.point1
            self.data["point2"] = constraint_properties.point2
            self.data["point3"] = constraint_properties.point3
            self.nb_values = 0
        elif self.kind == ConstraintsKind.ON_X:
            self.data["point0"] = constraint_properties.point0
            self.data["point1"] = constraint_properties.point1
            self.nb_values = 0
        elif self.kind == ConstraintsKind.ON_Y:
            self.data["point0"] = constraint_properties.point0
            self.data["point1"] = constraint_properties.point1
            self.nb_values = 0
        elif self.kind == ConstraintsKind.ON_Z:
            self.data["point0"] = constraint_properties.point0
            self.data["point1"] = constraint_properties.point1
            self.nb_values = 0
        elif self.kind == ConstraintsKind.SAME_DISTANCE:
            self.data["point0"] = constraint_properties.point0
            self.data["point1"] = constraint_properties.point1
            self.data["point2"] = constraint_properties.point2
            self.data["point3"] = constraint_properties.point3
            self.nb_values = 0
        elif self.kind == ConstraintsKind.ANGLE:
            self.data["point0"] = constraint_properties.point0
            self.data["point1"] = constraint_properties.point1
            self.data["point2"] = constraint_properties.point2
            self.data["point3"] = constraint_properties.point3
            self.data["angle"] = constraint_properties.value0
            self.nb_values = 1
        else:
            raise Exception(f"Unknown kind of constraints {self.kind}")

    def __repr__(self):
        return f"Constraint({self.kind}, {self.data})"

    def __getattr__(self, attr):
        return self.data[attr]


class MeshConstraints:
    """Utilities around MeshConstraintsContainer datas"""

    def __init__(self, generator):
        self.mc = generator[0]

    def __len__(self):
        return len(self.mc.constraints)

    def __iter__(self):
        for c in self.mc.constraints:
            yield Constraint(c)

    def reverse(self):
        class ReverseIter:
            def __init__(self, constraints):
                self.constraints = constraints

            def __iter__(self):
                for c in self.constraints[::-1]:
                    yield Constraint(c)

        return ReverseIter(self.mc.constraints)

    def __getitem__(self, key):
        return Constraint(self.mc.constraints[key])

    def remove(self, index):
        self.mc.constraints.remove(index)

    def clear_in_errors(self):
        """Clear all in_error flags on constraints"""
        for c in self.mc.constraints:
            c.in_error = False

    def set_in_error(self, index):
        """Set in_error flag to True on the linked constraint"""
        self.mc.constraints[index].in_error = True

    def exist_constraint(self, kind, **kwargs):
        """Return index of the constraint if a constraint already exists on the MeshConstraintsContainer
        with the same kind and parameters
        Return None if no constraint found
        mc: MeshConstraintsContainer instance
        kind: Kind enum for the constraint kind
        kwargs: parameters of the constraint"""
        for index, c in enumerate(self.mc.constraints):
            c_kind = ConstraintsKind(c.kind)
            if c_kind == kind:
                # This is the same type of constraint I'm looking for
                # so continue the search
                if c_kind in (
                    ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES,
                    ConstraintsKind.ON_X,
                    ConstraintsKind.ON_Y,
                    ConstraintsKind.ON_Z,
                ):
                    # TODO error handling on kwarg access ?
                    point0 = kwargs["point0"]
                    point1 = kwargs["point1"]
                    if (c.point0 == point0 and c.point1 == point1) or (
                        c.point0 == point1 and c.point1 == point0
                    ):
                        # this is the one !
                        return index
                elif c_kind in (
                    ConstraintsKind.FIX_X_COORD,
                    ConstraintsKind.FIX_Y_COORD,
                    ConstraintsKind.FIX_Z_COORD,
                    ConstraintsKind.FIX_XY_COORD,
                    ConstraintsKind.FIX_XZ_COORD,
                    ConstraintsKind.FIX_YZ_COORD,
                    ConstraintsKind.FIX_XYZ_COORD,
                ):
                    point = kwargs["point"]
                    if c.point0 == point:
                        return index
                elif c_kind in (
                    ConstraintsKind.PARALLEL,
                    ConstraintsKind.PERPENDICULAR,
                    ConstraintsKind.SAME_DISTANCE,
                    ConstraintsKind.ANGLE,
                ):
                    point0 = kwargs["point0"]
                    point1 = kwargs["point1"]
                    point2 = kwargs["point2"]
                    point3 = kwargs["point3"]
                    if (c.point0 == point0 and c.point1 == point1) or (
                        c.point0 == point1 and c.point1 == point0
                    ):
                        if (c.point2 == point2 and c.point3 == point3) or (
                            c.point2 == point3 and c.point3 == point2
                        ):
                            return index
                else:
                    raise PropsException(
                        f"Internal error : Unknown constraint : {c_kind}"
                    )
        return None

    def _add(self):
        """Internal utility to add a new constraint in MeshConstraintGenerator"""
        # A place for the new constraint
        self.mc.constraints.add()

        # I'm fairly confident this is single threaded
        # so should be OK
        # and I'm not able to find another type of API like .append() or .push()
        # So this should be the blender way
        last = len(self.mc.constraints) - 1

        # The constraint that has been created for me
        return self.mc.constraints[last]

    def add_distance_between_2_vertices(self, point0, point1, distance):
        """Add a ConstraintsKind::DISTANCE_BETWEEN_2_VERTICES with parameters
        point0: vertex index of point0
        point1: vertex index of point1
        distance: distance"""
        c = self._add()
        c.kind = ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES.value
        c.point0 = point0
        c.point1 = point1
        c.value0 = distance

    def add_fix_x_coord(self, point0, x):
        """Add a ConstraintsKind::FIX_X_COORD with parameters
        point0: vertex index of point0
        x: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_X_COORD.value
        c.point0 = point0
        c.value0 = x

    def add_fix_y_coord(self, point0, y):
        """Add a ConstraintsKind::FIX_Y_COORD with parameters
        point0: vertex index of point0
        y: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_Y_COORD.value
        c.point0 = point0
        c.value0 = y

    def add_fix_z_coord(self, point0, z):
        """Add a ConstraintsKind::FIX_Z_COORD with parameters
        point0: vertex index of point0
        z: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_Z_COORD.value
        c.point0 = point0
        c.value0 = z

    def add_fix_xy_coord(self, point0, x, y):
        """Add a ConstraintsKind::FIX_XY_COORD with parameters
        point0: vertex index of point0
        x: coordinate
        y: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_XY_COORD.value
        c.point0 = point0
        c.value0 = x
        c.value1 = y

    def add_fix_xz_coord(self, point0, x, z):
        """Add a ConstraintsKind::FIX_XZ_COORD with parameters
        point0: vertex index of point0
        x: coordinate
        z: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_XZ_COORD.value
        c.point0 = point0
        c.value0 = x
        c.value1 = z

    def add_fix_yz_coord(self, point0, y, z):
        """Add a ConstraintsKind::FIX_YZ_COORD with parameters
        point0: vertex index of point0
        y: coordinate
        z: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_YZ_COORD.value
        c.point0 = point0
        c.value0 = y
        c.value1 = z

    def add_fix_xyz_coord(self, point0, x, y, z):
        """Add a ConstraintsKind::FIX_XYZ_COORD with parameters
        point0: vertex index of point0
        x: coordinate
        y: coordinate
        z: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_XYZ_COORD.value
        c.point0 = point0
        c.value0 = x
        c.value1 = y
        c.value2 = z

    def add_parallel(self, point0, point1, point2, point3):
        """Add a ConstraintsKind::PARALLEL with parameters
        point0: vertex index of 1st point of the 1st vector
        point1: vertex index of 2nd point of the 1st vector
        point2: vertex index of 1st point of the 2nd vector
        point3: vertex index of 2nd point of the 2nd vector"""
        c = self._add()
        c.kind = ConstraintsKind.PARALLEL.value
        c.point0 = point0
        c.point1 = point1
        c.point2 = point2
        c.point3 = point3

    def add_perpendicular(self, point0, point1, point2, point3):
        """Add a ConstraintsKind::PERPENDICULAR with parameters
        point0: vertex index of 1st point of the 1st vector
        point1: vertex index of 2nd point of the 1st vector
        point2: vertex index of 1st point of the 2nd vector
        point3: vertex index of 2nd point of the 2nd vector"""
        c = self._add()
        c.kind = ConstraintsKind.PERPENDICULAR.value
        c.point0 = point0
        c.point1 = point1
        c.point2 = point2
        c.point3 = point3

    def add_on_x(self, point0, point1):
        """Add a ConstraintsKind::ON_X with parameters
        point0: vertex index of 1st point of the vector
        point1: vertex index of 2nd point of the vector"""
        c = self._add()
        c.kind = ConstraintsKind.ON_X.value
        c.point0 = point0
        c.point1 = point1

    def add_on_y(self, point0, point1):
        """Add a ConstraintsKind::ON_X with parameters
        point0: vertex index of 1st point of the vector
        point1: vertex index of 2nd point of the vector"""
        c = self._add()
        c.kind = ConstraintsKind.ON_Y.value
        c.point0 = point0
        c.point1 = point1

    def add_on_z(self, point0, point1):
        """Add a ConstraintsKind::ON_X with parameters
        point0: vertex index of 1st point of the vector
        point1: vertex index of 2nd point of the vector"""
        c = self._add()
        c.kind = ConstraintsKind.ON_Z.value
        c.point0 = point0
        c.point1 = point1

    def add_same_distance(self, point0, point1, point2, point3):
        """Add a ConstraintsKind::SAME_DISTANCE with parameters
        point0: vertex index of 1st point of the 1st vector
        point1: vertex index of 2nd point of the 1st vector
        point2: vertex index of 1st point of the 2nd vector
        point3: vertex index of 2nd point of the 2nd vector"""
        c = self._add()
        c.kind = ConstraintsKind.SAME_DISTANCE.value
        c.point0 = point0
        c.point1 = point1
        c.point2 = point2
        c.point3 = point3

    def add_angle(self, point0, point1, point2, point3, angle):
        """Add a ConstraintsKind::ANGLE with parameters
        point0: vertex index of point0
        point1: vertex index of point1
        point2: vertex index of point2
        point3: vertex index of point3
        angle: angle in degree"""
        c = self._add()
        c.kind = ConstraintsKind.ANGLE.value
        c.point0 = point0
        c.point1 = point1
        c.point2 = point2
        c.point3 = point3
        c.value0 = angle
