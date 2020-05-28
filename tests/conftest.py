from ..props import ConstraintsKind
import pytest


@pytest.fixture(scope="function")
def mesh_constraints_data():
    class Properties:
        def __init__(self, **kwargs):
            self.kind = kwargs.get("kind", ConstraintsKind.UNKNOWN)
            self.point0 = kwargs.get("point0", -1)
            self.point1 = kwargs.get("point1", -1)
            self.point2 = kwargs.get("point2", -1)
            self.point3 = kwargs.get("point3", -1)
            self.value1 = kwargs.get("value1", 0.0)
            self.value2 = kwargs.get("value2", 0.0)
            self.value3 = kwargs.get("value3", 0.0)
            self.in_error = kwargs.get("in_error", False)
            self.view = kwargs.get("view", False)
            self.show_details = kwargs.get("show_details", False)

    class Collection(list):
        def add(self):
            self.append(Properties())

        def remove(self, index):
            del self[index]

    class Constraints:
        def __init__(self):
            self.constraints = Collection()

    return [Constraints()]
