from bpy.types import Operator


class MeshConstraintsOperator(Operator):
    def info(self, msg):
        self.report({"INFO"}, msg)

    def warning(self, msg):
        self.report({"WARNING"}, msg)
        return {"CANCELLED"}

    def error(self, msg):
        self.report({"ERRRO"}, msg)
        return {"CANCELLED"}
