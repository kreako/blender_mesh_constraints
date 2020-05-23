from bpy.props import IntProperty
from . import base
from .. import props


class MESH_CONSTRAINTS_OT_DeleteConstraint(base.MeshConstraintsOperator):
    bl_idname = "mesh_constraints.delete_constraint"
    bl_label = "Delete"
    bl_description = "Delete a constraint based on its index"

    index: IntProperty(name="index", description="Index of the constraint to delete")

    def execute(self, context):
        if context.area.type != "VIEW_3D":
            return self.warning("I'm not able to find VIEW_3D, so I won't run")
        o = context.object
        if o is None:
            return self.warning(f"No object found")
        if "MeshConstraintGenerator" not in o:
            return self.warning(f"No constraints found on this object {o.name}")

        mc = props.MeshConstraints(o.MeshConstraintGenerator)

        if self.index >= len(mc):
            return self.warning(f"No constraints found with index '{self.index}' on this object {o.name}")

        mc.remove(self.index)

        context.area.tag_redraw()
        return {"FINISHED"}
