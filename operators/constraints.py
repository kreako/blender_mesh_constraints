import bpy
import bmesh

from . import base
from .. import props


class ConstraintOperator(base.MeshConstraintsOperator):
    @classmethod
    def poll(cls, context):
        # A selected mesh in edit mode : I'm in, but not for the rest
        o = context.object
        return o is not None and o.type == "MESH" and bpy.context.mode == "EDIT_MESH"

    def execute(self, context):
        if context.area.type != "VIEW_3D":
            return self.warning("I'm not able to find VIEW_3D, so I won't run")

        # object accessor
        self.o = context.object

        # Build the mesh
        self.bm = bmesh.from_edit_mesh(self.o.data)

        if "MeshConstraintGenerator" not in self.o:
            # Nothing yet in this object so add the main collection
            self.o.MeshConstraintGenerator.add()

        # Accessor for the main collection
        self.mc = props.MeshConstraints(self.o.MeshConstraintGenerator)

        # Call the child execute
        return self.constraint_execute(context)

    def selected_verts(self):
        """Return list of selected vertex indices"""
        return [v.index for v in self.bm.verts if v.select is True]

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
        # Get selected vertices
        vertices_list = self.selected_verts()

        if len(vertices_list) != 2:
            # I need 2 vertices !
            # TODO: add multiple constraints at once
            return self.warning(
                "I need you to select 2 vertices or I'm not able to add a distance constraint between 2 vertices"
            )

        point0, point1 = vertices_list

        k = props.ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES
        if self.mc.exist_constraint(k, point0=point0, point1=point1):
            return self.warning(
                "This constraint already exists, so I won't add it again"
            )

        self.mc.add_distance_between_2_vertices(
            point0, point1, self.distance(point0, point1)
        )

        # redraw
        context.area.tag_redraw()
        return {"FINISHED"}
