import bmesh

from . import base
from .. import props


class ConstraintOperator(base.MeshConstraintsOperator):
    @classmethod
    def poll(cls, context):
        # A selected mesh in edit mode : I'm in, but not for the rest
        o = context.object
        return o is not None and o.type == "MESH" and context.mode == "EDIT_MESH"

    def execute(self, context):
        if context.area.type != "VIEW_3D":
            return self.warning("I'm not able to find VIEW_3D, so I won't run")

        # object accessor
        self.o = context.edit_object

        # Build the mesh
        self.bm = bmesh.from_edit_mesh(self.o.data)

        if "MeshConstraintGenerator" not in self.o:
            # Nothing yet in this object so add the main collection
            self.o.MeshConstraintGenerator.add()

        # Accessor for the main collection
        self.mc = props.MeshConstraints(self.o.MeshConstraintGenerator)

        # Call the child execute
        ret = self.constraint_execute(context)

        # redraw
        context.area.tag_redraw()

        return ret

    def selected_verts(self):
        """Return list of selected vertex indices"""
        return [v.index for v in self.bm.verts if v.select]

    def selected_edges(self):
        """Return list of selected edges indices"""
        return [e.index for e in self.bm.edges if e.select]

    def distance(self, point0, point1):
        """Compute a distance between 2 vertices of a mesh
        point0: vertex index of the first point
        point1: vertex index of the second point"""
        co0 = self.bm.verts[point0].co
        co1 = self.bm.verts[point1].co
        return (co1 - co0).length


class MESH_CONSTRAINTS_OT_ConstraintDistance2Vertices(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_distance_2_vertices"
    bl_label = "Add distance constraint"
    bl_description = "Add a distance constraint between 2 vertices (select 2 vertices) (EDITMODE only)"

    def constraint_execute(self, context):
        vertices_list = self.selected_verts()

        if len(vertices_list) != 2:
            # I need 2 vertices !
            # TODO: add multiple constraints at once
            return self.warning(
                "I need you to select 2 vertices or I'm not able to add a distance constraint between 2 vertices"
            )

        point0, point1 = vertices_list

        k = props.ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
        if self.mc.exist_constraint(k, point0=point0, point1=point1) is not None:
            return self.warning("This constraint already exists...")

        self.mc.add_distance_between_2_vertices(
            point0, point1, self.distance(point0, point1)
        )

        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintFixXCoord(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_fix_x_coord"
    bl_label = "Add a fix X coordinate constraint"
    bl_description = (
        "Add a constraint to fix X coordinate (select 1 vertex or more) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        vertices_list = self.selected_verts()
        if not vertices_list:
            return self.warning("You must select at least 1 vertex")

        k = props.ConstraintsKind.FIX_X_COORD
        added = 0
        existing = 0
        for point in vertices_list:
            if self.mc.exist_constraint(k, point=point) is not None:
                existing += 1
                continue
            self.mc.add_fix_x_coord(point, self.bm.verts[point].co.x)
            added += 1

        if existing > 0 and added == 0:
            return self.warning(f"{existing} constraints already exist, so I did nothing...")

        if existing > 0 and added > 0:
            self.info(f"Added {added} constraints, {existing} already existing.")
        else:
            self.info(f"Added {added} constraints")
        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintFixYCoord(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_fix_y_coord"
    bl_label = "Add a fix Y coordinate constraint"
    bl_description = (
        "Add a constraint to fix Y coordinate (select 1 vertex) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        vertices_list = self.selected_verts()
        if not vertices_list:
            return self.warning("You must select at least 1 vertex")

        k = props.ConstraintsKind.FIX_Y_COORD
        added = 0
        existing = 0
        for point in vertices_list:
            if self.mc.exist_constraint(k, point=point) is not None:
                existing += 1
                continue
            self.mc.add_fix_y_coord(point, self.bm.verts[point].co.y)
            added += 1

        if existing > 0 and added == 0:
            return self.warning(f"{existing} constraints already exist, so I did nothing...")

        if existing > 0 and added > 0:
            self.info(f"Added {added} constraints, {existing} already existing.")
        else:
            self.info(f"Added {added} constraints")
        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintFixZCoord(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_fix_z_coord"
    bl_label = "Add a fix Z coordinate constraint"
    bl_description = (
        "Add a constraint to fix Z coordinate (select 1 vertex) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        vertices_list = self.selected_verts()
        if not vertices_list:
            return self.warning("You must select at least 1 vertex")

        k = props.ConstraintsKind.FIX_Z_COORD
        added = 0
        existing = 0
        for point in vertices_list:
            if self.mc.exist_constraint(k, point=point) is not None:
                existing += 1
                continue
            self.mc.add_fix_z_coord(point, self.bm.verts[point].co.z)
            added += 1

        if existing > 0 and added == 0:
            return self.warning(f"{existing} constraints already exist, so I did nothing...")

        if existing > 0 and added > 0:
            self.info(f"Added {added} constraints, {existing} already existing.")
        else:
            self.info(f"Added {added} constraints")
        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintFixXYCoord(ConstraintOperator):
    # TODO remove ?
    bl_idname = "mesh_constraints.constraint_fix_xy_coord"
    bl_label = "Add fix X and Y coordinates constraints"
    bl_description = (
        "Add constraints to fix X and Y coordinates (select 1 vertex) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        vertices_list = self.selected_verts()

        if len(vertices_list) != 1:
            # TODO: add multiple constraints at once
            return self.warning(
                "I need you to select 1 vertex or I'm not able to fix a coordinate of a vertex"
            )

        point = vertices_list[0]

        # TODO on Fix...Coord operator, merge existing coordinate for the same point
        # Like : Existing FIX_X_COORD constraint, add a FIX_XY_COORD, merge them both in the latest
        k = props.ConstraintsKind.FIX_XY_COORD
        if self.mc.exist_constraint(k, point=point) is not None:
            return self.warning("This constraint already exists...")

        self.mc.add_fix_xy_coord(point, *self.bm.verts[point].co.xy)

        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintFixXZCoord(ConstraintOperator):
    # TODO remove ?
    bl_idname = "mesh_constraints.constraint_fix_xz_coord"
    bl_label = "Add fix X and Z coordinates constraints"
    bl_description = (
        "Add constraints to fix X and Z coordinates (select 1 vertex) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        vertices_list = self.selected_verts()

        if len(vertices_list) != 1:
            # TODO: add multiple constraints at once
            return self.warning(
                "I need you to select 1 vertex or I'm not able to fix a coordinate of a vertex"
            )

        point = vertices_list[0]

        k = props.ConstraintsKind.FIX_XZ_COORD
        if self.mc.exist_constraint(k, point=point) is not None:
            return self.warning("This constraint already exists...")

        self.mc.add_fix_xz_coord(point, *self.bm.verts[point].co.xz)

        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintFixYZCoord(ConstraintOperator):
    # TODO remove ?
    bl_idname = "mesh_constraints.constraint_fix_yz_coord"
    bl_label = "Add fix Y and Z coordinates constraints"
    bl_description = (
        "Add constraints to fix Y and Z coordinates (select 1 vertex) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        vertices_list = self.selected_verts()

        if len(vertices_list) != 1:
            # TODO: add multiple constraints at once
            return self.warning(
                "I need you to select 1 vertex or I'm not able to fix a coordinate of a vertex"
            )

        point = vertices_list[0]

        k = props.ConstraintsKind.FIX_YZ_COORD
        if self.mc.exist_constraint(k, point=point) is not None:
            return self.warning("This constraint already exists...")

        self.mc.add_fix_yz_coord(point, *self.bm.verts[point].co.yz)

        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintFixXYZCoord(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_fix_xyz_coord"
    bl_label = "Add fix X, Y and Z coordinates constraints"
    bl_description = (
        "Add constraints to fix X, Y and Z coordinates (select 1 vertex) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        vertices_list = self.selected_verts()
        if not vertices_list:
            return self.warning("You must select at least 1 vertex")

        k = props.ConstraintsKind.FIX_XYZ_COORD
        added = 0
        existing = 0
        for point in vertices_list:
            if self.mc.exist_constraint(k, point=point) is not None:
                existing += 1
                continue
            self.mc.add_fix_xyz_coord(point, *self.bm.verts[point].co.xyz)
            added += 1

        if existing > 0 and added == 0:
            return self.warning(f"{existing} constraints already exist, so I did nothing...")

        if existing > 0 and added > 0:
            self.info(f"Added {added} constraints, {existing} already existing.")
        else:
            self.info(f"Added {added} constraints")
        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintParallel2Edges(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_parallel_2_edges"
    bl_label = "Parallel constraint between 2 edges"
    bl_description = (
        "Add a parallel constraint between 2 edges (select 2 edges) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        # TODO if vertex selection ?
        edges_list = self.selected_edges()

        if len(edges_list) != 2:
            # TODO: add multiple constraints at once
            return self.warning(
                "I need you to select 2 edges or I'm not able to add a parallel constraint between 2 edges"
            )

        edge0, edge1 = edges_list
        p0, p1 = [v.index for v in self.bm.edges[edge0].verts]
        p2, p3 = [v.index for v in self.bm.edges[edge1].verts]

        k = props.ConstraintsKind.PARALLEL
        if self.mc.exist_constraint(k, point0=p0, point1=p1, point2=p2, point3=p3) is not None:
            return self.warning("This constraint already exists...")

        self.mc.add_parallel(p0, p1, p2, p3)

        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintPerpendicular2Edges(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_perpendicular_2_edges"
    bl_label = "Perpendicular constraint between 2 edges"
    bl_description = (
        "Add a perpendicular constraint between 2 edges (select 4 vertices or 2 edges) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        # TODO if vertex selection ?
        edges_list = self.selected_edges()

        if len(edges_list) != 2:
            # TODO: add multiple constraints at once
            return self.warning(
                "I need you to select 2 edges or I'm not able to add a parallel constraint between 2 edges"
            )

        edge0, edge1 = edges_list
        p0, p1 = [v.index for v in self.bm.edges[edge0].verts]
        p2, p3 = [v.index for v in self.bm.edges[edge1].verts]

        k = props.ConstraintsKind.PERPENDICULAR
        if self.mc.exist_constraint(k, point0=p0, point1=p1, point2=p2, point3=p3) is not None:
            return self.warning("This constraint already exists...")

        self.mc.add_perpendicular(p0, p1, p2, p3)

        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintOnX(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_on_x"
    bl_label = "Add an On X constraint"
    bl_description = (
        "Add a constraint to make an edge parallel to X axis (select 2 vertices or 1 edge) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        # TODO: add multiple constraints at once
        if "EDGE" in self.bm.select_mode:
            edges_list = self.selected_edges()
            if len(edges_list) != 1:
                return self.warning(
                    "I need you to select 1 edge or I'm not able to add an On X constraint for an edge"
                )
            p0, p1 = [v.index for v in self.bm.edges[edges_list[0]].verts]
        else:
            vertices_list = self.selected_verts()
            if len(vertices_list) != 2:
                return self.warning(
                    "I need you to select 2 vertices or I'm not able to add an On X constraint for an edge"
                )
            p0, p1 = vertices_list

        k = props.ConstraintsKind.ON_X
        if self.mc.exist_constraint(k, point0=p0, point1=p1) is not None:
            return self.warning("This constraint already exists...")
        self.mc.add_on_x(p0, p1)
        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintOnY(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_on_y"
    bl_label = "Add an On Y constraint"
    bl_description = (
        "Add a constraint to make an edge parallel to Y axis (select 2 vertices or 1 edge) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        # TODO: add multiple constraints at once
        if "EDGE" in self.bm.select_mode:
            edges_list = self.selected_edges()
            if len(edges_list) != 1:
                return self.warning(
                    "I need you to select 1 edge or I'm not able to add an On Y constraint for an edge"
                )
            p0, p1 = [v.index for v in self.bm.edges[edges_list[0]].verts]
        else:
            vertices_list = self.selected_verts()
            if len(vertices_list) != 2:
                return self.warning(
                    "I need you to select 2 vertices or I'm not able to add an On Y constraint for an edge"
                )
            p0, p1 = vertices_list

        k = props.ConstraintsKind.ON_Y
        if self.mc.exist_constraint(k, point0=p0, point1=p1) is not None:
            return self.warning("This constraint already exists...")
        self.mc.add_on_y(p0, p1)
        return {"FINISHED"}


class MESH_CONSTRAINTS_OT_ConstraintOnZ(ConstraintOperator):
    bl_idname = "mesh_constraints.constraint_on_z"
    bl_label = "Add an On Z constraint"
    bl_description = (
        "Add a constraint to make an edge parallel to Z axis (select 2 vertices or 1 edge) (EDITMODE only)"
    )

    def constraint_execute(self, context):
        # TODO: add multiple constraints at once
        if "EDGE" in self.bm.select_mode:
            edges_list = self.selected_edges()
            if len(edges_list) != 1:
                return self.warning(
                    "I need you to select 1 edge or I'm not able to add an On Z constraint for an edge"
                )
            p0, p1 = [v.index for v in self.bm.edges[edges_list[0]].verts]
        else:
            vertices_list = self.selected_verts()
            if len(vertices_list) != 2:
                return self.warning(
                    "I need you to select 2 vertices or I'm not able to add an On Z constraint for an edge"
                )
            p0, p1 = vertices_list

        k = props.ConstraintsKind.ON_Z
        if self.mc.exist_constraint(k, point0=p0, point1=p1) is not None:
            return self.warning("This constraint already exists...")
        self.mc.add_on_z(p0, p1)
        return {"FINISHED"}
