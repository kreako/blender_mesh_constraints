from ..props import ConstraintsKind
import pytest

@pytest.fixture(scope="module")
def mesh_constraints_data():
    class Properties:
        def __init__(self, **kwargs):
            self.kind = kwargs.get("kind", ConstraintsKind.UNKNOWN)
            self.point0 = kwargs.get("point0", -1)
            self.point1 = kwargs.get("point1", -1)
            self.value = kwargs.get("value", 0.0)
            self.view = kwargs.get("view", False)
            self.show_details = kwargs.get("show_details", False)

    class Collection(list):
        def add(self):
            self.append(Properties())

    class Constraints:
        def __init__(self):
            self.constraints = Collection()

    return [Constraints()]
