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
        row = box.row()
        row.operator("mesh_constraints.constraint_fix_xyz_coord", text="XYZ")
        row.operator("mesh_constraints.constraint_fix_x_coord", text="X")
        row.operator("mesh_constraints.constraint_fix_y_coord", text="Y")
        row.operator("mesh_constraints.constraint_fix_z_coord", text="Z")
        row = box.row()
        row.operator("mesh_constraints.constraint_fix_xy_coord", text="XY")
        row.operator("mesh_constraints.constraint_fix_xz_coord", text="XZ")
        row.operator("mesh_constraints.constraint_fix_yz_coord", text="YZ")


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
            # TODO do something with ValueError ?
            c_kind = props.ConstraintsKind(c.kind)
            c_abbreviation = props.constraints_kind_abbreviation[c_kind]
            c_display = props.constraints_kind_display[c_kind]

            row = box.row(align=True)
            icon = "HIDE_OFF" if c.view else "HIDE_ON"
            row.prop(c.raw, "view", text="", toggle=True, icon=icon)
            row.prop(c.raw, "show_details", text="", toggle=True, icon="PREFERENCES")
            row.label(text=c_abbreviation)
            row.prop(c.raw, "value0", text="")
            if c.nb_values > 1:
                row.prop(c.raw, "value1", text="")
            if c.nb_values > 2:
                row.prop(c.raw, "value2", text="")
            delete_op = "mesh_constraints.delete_constraint"

            row.operator(delete_op, text="", icon="X").index = index
            if c.show_details:
                row = box.row(align=True)
                row.label(text=c_display)
                if c_kind == props.ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES:
                    row = box.row(align=True)
                    row.prop(c.raw, "point0", text="Point0")
                    row.prop(c.raw, "point1", text="Point1")
                    row = box.row(align=True)
                    row.label(text="")
                elif c_kind in (
                    props.ConstraintsKind.FIX_X_COORD,
                    props.ConstraintsKind.FIX_Y_COORD,
                    props.ConstraintsKind.FIX_Z_COORD,
                ):
                    row = box.row(align=True)
                    row.prop(c.raw, "point0", text="Point")
                else:
                    raise Exception(f"Not supported: {c_display}")
                row = box.row(align=True)
                row.label(text="")
