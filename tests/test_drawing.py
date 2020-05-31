from ..drawing import _format_distance


def test_format_distance():
    class UnitSettings:
        def __init__(self, system):
            self.system = system

    class Scene:
        def __init__(self, unit_settings):
            self.unit_settings = unit_settings

    class Context:
        def __init__(self, scene):
            self.scene = scene

    context = Context(Scene(UnitSettings("METRIC")))
    assert _format_distance(context, 1.34567) == "1.35 m"
    assert _format_distance(context, 0.34567) == "34.6 cm"
    assert _format_distance(context, 0.034567) == "3.46 cm"
    assert _format_distance(context, 0.0034567) == "3.46 mm"
    assert _format_distance(context, 0.00034567) == "0.35 mm"

    context = Context(Scene(UnitSettings("IMPERIAL")))
    assert _format_distance(context, 1.34567) == "4.41 ft"
    assert _format_distance(context, 0.034567) == "1.36 in"
