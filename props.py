from enum import Enum, unique
from bpy.types import PropertyGroup
from bpy.props import (
    CollectionProperty,
    EnumProperty,
    IntProperty,
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


# For kind EnumProperty
kind_items = [
    (k.value, " ".join(s.lower() for s in k.name.split("_")), "")
    for k in ConstraintsKind
]


class MeshConstraintProperties(PropertyGroup):
    # Data of the constraint
    kind: EnumProperty(items=kind_items, name="Kind", description="Kind of constraints")
    point0: IntProperty(name="point0", description="Point 0 of the constraint")
    point1: IntProperty(name="point1", description="Point 1 of the constraint")
    value: FloatProperty(name="value", description="Value of the constraint")
    # View related
    view: BoolProperty(name="view", description="Show/hide in 3D view", default=True)
    show_details: BoolProperty(
        name="show_details", description="Show/hide details in panel", default=False
    )


class MeshConstraintsContainer(PropertyGroup):
    constraints: CollectionProperty(type=MeshConstraintProperties)


class PropsException(Exception):
    pass


class MeshConstraints:
    """Utilities around MeshConstraintsContainer datas"""

    def __init__(self, generator):
        self.mc = generator[0]

    def __len__(self):
        return len(self.mc.constraints)

    def remove(self, index):
        self.mc.constraints.remove(index)

    def exist_constraint(self, kind, **kwargs):
        """Return true if a constraint already exists on the MeshConstraintsContainer
        mc: MeshConstraintsContainer instance
        kind: Kind enum for the constraint kind
        kwargs: parameters of the constraint"""
        for c in self.mc.constraints:
            c_kind = ConstraintsKind(c.kind)
            if c_kind == kind:
                # This is the same type of constraint I'm looking for
                # so continue the search
                if c_kind == ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES:
                    # TODO error handling on kwarg access ?
                    point0 = kwargs["point0"]
                    point1 = kwargs["point1"]
                    if (c.point0 == point0 and c.point1 == point1) or (
                        c.point0 == point1 and c.point1 == point0
                    ):
                        # this is the one !
                        return True
                elif c_kind in (
                    ConstraintsKind.FIX_X_COORD,
                    ConstraintsKind.FIX_Y_COORD,
                    ConstraintsKind.FIX_Z_COORD,
                ):
                    point0 = kwargs["point0"]
                    if c.point0 == point0:
                        return True
                else:
                    raise PropsException(
                        f"Internal error : Unknown constraint : {c_kind}"
                    )
        return False

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

    def add_distance_between_2_vertices(self, point0, point1, value):
        """Add a ConstraintsKind::DISTANCE_BETWEEN_2_VERTICES with parameters
        point0: vertex index of point0
        point1: vertex index of point1
        value: distance"""
        c = self._add()
        c.kind = ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES.value
        c.point0 = point0
        c.point1 = point1
        c.value = value

    def add_fix_x_coord(self, point0, value):
        """Add a ConstraintsKind::FIX_X_COORD with parameters
        point0: vertex index of point0
        value: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_X_COORD.value
        c.point0 = point0
        c.value = value

    def add_fix_y_coord(self, point0, value):
        """Add a ConstraintsKind::FIX_Y_COORD with parameters
        point0: vertex index of point0
        value: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_Y_COORD.value
        c.point0 = point0
        c.value = value

    def add_fix_z_coord(self, point0, value):
        """Add a ConstraintsKind::FIX_Z_COORD with parameters
        point0: vertex index of point0
        value: coordinate"""
        c = self._add()
        c.kind = ConstraintsKind.FIX_Z_COORD.value
        c.point0 = point0
        c.value = value
