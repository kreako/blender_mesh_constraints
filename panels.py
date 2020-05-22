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
        icon = "PAUSE" if context.window_manager.mesh_constraints_draw_constraints_definition else "PLAY"
        row.operator("mesh_constraints.draw_constraints_definition", text="Definition", icon=icon)
        icon = "PAUSE" if context.window_manager.mesh_constraints_draw_constraints_violation else "PLAY"
        row.operator("mesh_constraints.draw_constraints_violation", text="Violation", icon=icon)


        box = self.layout.box()
        # box.label(text="Add constraints")
        row = box.row()
        row.operator("mesh_constraints.constraint_distance_2_vertices", text="Distance")
