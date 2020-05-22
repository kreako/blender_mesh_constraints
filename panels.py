from bpy.types import Panel

from . import props


class MeshConstraintsPanelBase(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Constraints"


class MeshConstraintsPanelMain(MeshConstraintsPanelBase):
    bl_label = "Mesh Constraints"
    bl_idname = "MESH_CONSTRAINTS_PT_MAIN"

    def draw(self, context):
        box = self.layout.box()

        row = box.row()
        row.operator("mesh_constraints.solve", text="Solve", icon="SNAP_ON")

        row = box.row()
        icon = (
            "PAUSE"
            if context.window_manager.mesh_constraints_draw_constraints_definition
            else "PLAY"
        )
        row.operator(
            "mesh_constraints.draw_constraints_definition", text="Definition", icon=icon
        )
        icon = (
            "PAUSE"
            if context.window_manager.mesh_constraints_draw_constraints_violation
            else "PLAY"
        )
        row.operator(
            "mesh_constraints.draw_constraints_violation", text="Violation", icon=icon
        )


class MeshConstraintsPanelAdd(MeshConstraintsPanelBase):
    bl_label = "Add constraints"
    bl_idname = "MESH_CONSTRAINTS_PT_ADD"
    bl_parent_id = "MESH_CONSTRAINTS_PT_MAIN"

    def draw(self, context):
        box = self.layout.box()
        row = box.row()
        row.operator("mesh_constraints.constraint_distance_2_vertices", text="Distance")


class MeshConstraintsPanelItems(MeshConstraintsPanelBase):
    bl_label = "Items"
    bl_idname = "MESH_CONSTRAINTS_PT_ITEMS"
    bl_parent_id = "MESH_CONSTRAINTS_PT_MAIN"

    def draw(self, context):
        o = context.object
        if o is None or "MeshConstraintGenerator" not in o:
            # I need an object with constraints in it !
            return

        mc = props.MeshConstraints(o.MeshConstraintGenerator)

        box = self.layout.box()
        for index, c in enumerate(mc):
            row = box.row(align=True)
            icon = "HIDE_OFF" if c.view else "HIDE_ON"
            row.prop(c, "view", text="", toggle=True, icon=icon)
            row.prop(c, "show_details", text="", toggle=True, icon="PREFERENCES")
            row.prop(c, "value", text="")
            delete_op = "mesh_constraints.delete_constraint"
            row.operator(delete_op, text="", icon="X").index = index
            if c.show_details:
                # TODO do something with ValueError ?
                kind = props.ConstraintsKind(c.kind)
                if kind == props.ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES:
                    row = box.row(align=True)
                    row.prop(c, "point0", text="Point0")
                    row.prop(c, "point1", text="Point1")
                else:
                    row.label(text=f"Not supported yet : {kind}")
