from bpy.props import IntProperty
from . import base
from .. import props


class MiscOperatorBase(base.MeshConstraintsOperator):

    def execute(self, context):
        if context.area.type != "VIEW_3D":
            return self.warning("I'm not able to find VIEW_3D, so I won't run")
        o = context.object
        if o is None:
            return self.warning(f"No object found")
        if "MeshConstraintGenerator" not in o:
            return self.warning(f"No constraints found on this object {o.name}")

        self.mc = props.MeshConstraints(o.MeshConstraintGenerator)

        ret = self.misc_execute(context)

        context.area.tag_redraw()
        return ret


class MESH_CONSTRAINTS_OT_DeleteConstraint(MiscOperatorBase):
    bl_idname = "mesh_constraints.delete_constraint"
    bl_label = "Delete"
    bl_description = "Delete a constraint based on its index"

    index: IntProperty(name="index", description="Index of the constraint to delete")

    def misc_execute(self, context):
        if self.index >= len(self.mc):
            return self.warning(f"No constraints found with index '{self.index}' on this object {o.name}")
        self.mc.remove(self.index)
        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_DeleteAllConstraints(MiscOperatorBase):
    bl_idname = "mesh_constraints.delete_all_constraints"
    bl_label = "Delete all"
    bl_description = "Delete all constraints"

    def misc_execute(self, context):
        self.mc.delete_all()
        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_HideAllConstraints(MiscOperatorBase):
    bl_idname = "mesh_constraints.hide_all_constraints"
    bl_label = "Hide all"
    bl_description = "Hide all constraints"

    def misc_execute(self, context):
        self.mc.hide_all()
        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ShowAllConstraints(MiscOperatorBase):
    bl_idname = "mesh_constraints.show_all_constraints"
    bl_label = "Show all"
    bl_description = "Show all constraints"

    def misc_execute(self, context):
        self.mc.show_all()
        return {"FINISHED"}
