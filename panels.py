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

        icon = (
            "PAUSE"
            if context.window_manager.mesh_constraints_draw_constraints_definition
            else "PLAY"
        )
        row.operator(
            "mesh_constraints.draw_constraints_definition", text="Definition", icon=icon
        )

        # TODO display Solver error here ?
        # o = context.object
        # if o is not None and "MeshConstraintGenerator" in o:
        # an object with constraints in it
        # mc = props.MeshConstraints(o.MeshConstraintGenerator)
        # if


class MeshConstraintsPanelAdd(MeshConstraintsPanelBase):
    bl_label = "Add constraints"
    bl_idname = "MESH_CONSTRAINTS_PT_ADD"
    bl_parent_id = "MESH_CONSTRAINTS_PT_MAIN"

    def draw(self, context):
        box = self.layout.box()
        row = box.row()
        row.operator(
            "mesh_constraints.constraint_distance_2_vertices",
            text=props.constraints_kind_abbreviation[
                props.ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
            ],
        )
        row.operator(
            "mesh_constraints.constraint_parallel_2_edges",
            text=props.constraints_kind_abbreviation[props.ConstraintsKind.PARALLEL],
        )
        row.operator(
            "mesh_constraints.constraint_perpendicular_2_edges",
            text=props.constraints_kind_abbreviation[
                props.ConstraintsKind.PERPENDICULAR
            ],
        )
        row = box.row()
        row.operator(
            "mesh_constraints.constraint_fix_xyz_coord",
            text=props.constraints_kind_abbreviation[
                props.ConstraintsKind.FIX_XYZ_COORD
            ],
        )
        row.operator(
            "mesh_constraints.constraint_fix_x_coord",
            text=props.constraints_kind_abbreviation[props.ConstraintsKind.FIX_X_COORD],
        )
        row.operator(
            "mesh_constraints.constraint_fix_y_coord",
            text=props.constraints_kind_abbreviation[props.ConstraintsKind.FIX_Y_COORD],
        )
        row.operator(
            "mesh_constraints.constraint_fix_z_coord",
            text=props.constraints_kind_abbreviation[props.ConstraintsKind.FIX_Z_COORD],
        )
        # row = box.row()
        # row.operator("mesh_constraints.constraint_fix_xy_coord", text="XY")
        # row.operator("mesh_constraints.constraint_fix_xz_coord", text="XZ")
        # row.operator("mesh_constraints.constraint_fix_yz_coord", text="YZ")
        row = box.row()
        row.operator(
            "mesh_constraints.constraint_on_x",
            text=props.constraints_kind_abbreviation[props.ConstraintsKind.ON_X],
        )
        row.operator(
            "mesh_constraints.constraint_on_y",
            text=props.constraints_kind_abbreviation[props.ConstraintsKind.ON_Y],
        )
        row.operator(
            "mesh_constraints.constraint_on_z",
            text=props.constraints_kind_abbreviation[props.ConstraintsKind.ON_Z],
        )


class MeshConstraintsPanelItems(MeshConstraintsPanelBase):
    bl_label = "Items"
    bl_idname = "MESH_CONSTRAINTS_PT_ITEMS"
    bl_parent_id = "MESH_CONSTRAINTS_PT_MAIN"

    def draw(self, context):
        o = context.object
        if o is None or "MeshConstraintGenerator" not in o:
            # I need an object with constraints in it !
            self.layout.box().row(align=True).label(text="No constraints yet")
            return

        mc = props.MeshConstraints(o.MeshConstraintGenerator)

        box = self.layout.box()
        if len(mc) == 0:
            box.row(align=True).label(text="No constraints yet")
        for index, c in enumerate(mc):
            # TODO do something with ValueError ?
            c_kind = props.ConstraintsKind(c.kind)
            c_abbreviation = props.constraints_kind_abbreviation[c_kind]
            c_display = props.constraints_kind_display[c_kind]

            row = box.row(align=True)
            icon = "HIDE_OFF" if c.view else "HIDE_ON"
            row.prop(c.raw, "view", text="", toggle=True, icon=icon)
            row.prop(c.raw, "show_details", text="", toggle=True, icon="PREFERENCES")
            icon = "ERROR" if c.in_error else "NONE"
            row.label(text=c_abbreviation, icon=icon)
            if c.nb_values == 1:
                row.prop(c.raw, "value0", text="")
            delete_op = "mesh_constraints.delete_constraint"

            row.operator(delete_op, text="", icon="X").index = index
            if c.show_details:
                row = box.row(align=True)
                row.label(text=c_display)
                if c_kind == props.ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES:
                    box.row(align=True).prop(c.raw, "point0", text="Point0")
                    box.row(align=True).prop(c.raw, "point1", text="Point1")
                    box.row(align=True).prop(c.raw, "value0", text="Distance")
                elif c_kind == props.ConstraintsKind.FIX_X_COORD:
                    box.row(align=True).prop(c.raw, "point0", text="Point")
                    box.row(align=True).prop(c.raw, "value0", text="X")
                elif c_kind == props.ConstraintsKind.FIX_Y_COORD:
                    box.row(align=True).prop(c.raw, "point0", text="Point")
                    box.row(align=True).prop(c.raw, "value0", text="Y")
                elif c_kind == props.ConstraintsKind.FIX_Z_COORD:
                    box.row(align=True).prop(c.raw, "point0", text="Point")
                    box.row(align=True).prop(c.raw, "value0", text="Z")
                elif c_kind == props.ConstraintsKind.FIX_XY_COORD:
                    box.row(align=True).prop(c.raw, "point0", text="Point")
                    box.row(align=True).prop(c.raw, "value0", text="X")
                    box.row(align=True).prop(c.raw, "value1", text="Y")
                elif c_kind == props.ConstraintsKind.FIX_XZ_COORD:
                    box.row(align=True).prop(c.raw, "point0", text="Point")
                    box.row(align=True).prop(c.raw, "value0", text="X")
                    box.row(align=True).prop(c.raw, "value1", text="Z")
                elif c_kind == props.ConstraintsKind.FIX_YZ_COORD:
                    box.row(align=True).prop(c.raw, "point0", text="Point")
                    box.row(align=True).prop(c.raw, "value0", text="Y")
                    box.row(align=True).prop(c.raw, "value1", text="Z")
                elif c_kind == props.ConstraintsKind.FIX_XYZ_COORD:
                    box.row(align=True).prop(c.raw, "point0", text="Point")
                    box.row(align=True).prop(c.raw, "value0", text="X")
                    box.row(align=True).prop(c.raw, "value1", text="Y")
                    box.row(align=True).prop(c.raw, "value2", text="Z")
                elif c_kind == props.ConstraintsKind.PARALLEL:
                    box.row(align=True).prop(c.raw, "point0", text="Point0")
                    box.row(align=True).prop(c.raw, "point1", text="Point1")
                    box.row(align=True).prop(c.raw, "point2", text="Point2")
                    box.row(align=True).prop(c.raw, "point3", text="Point3")
                elif c_kind == props.ConstraintsKind.PERPENDICULAR:
                    box.row(align=True).prop(c.raw, "point0", text="Point0")
                    box.row(align=True).prop(c.raw, "point1", text="Point1")
                    box.row(align=True).prop(c.raw, "point2", text="Point2")
                    box.row(align=True).prop(c.raw, "point3", text="Point3")
                elif c_kind == props.ConstraintsKind.ON_X:
                    box.row(align=True).prop(c.raw, "point0", text="Point0")
                    box.row(align=True).prop(c.raw, "point1", text="Point1")
                elif c_kind == props.ConstraintsKind.ON_Y:
                    box.row(align=True).prop(c.raw, "point0", text="Point0")
                    box.row(align=True).prop(c.raw, "point1", text="Point1")
                elif c_kind == props.ConstraintsKind.ON_Z:
                    box.row(align=True).prop(c.raw, "point0", text="Point0")
                    box.row(align=True).prop(c.raw, "point1", text="Point1")
                else:
                    raise Exception(f"Not supported: {c_display}")
                row = box.row(align=True)
                row.label(text="")
