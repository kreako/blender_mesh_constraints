from . import base


class MESH_CONSTRAINTS_OT_Solve(base.MeshConstraintsOperator):
    bl_idname = "mesh_constraints.solve"
    bl_label = "Solve"
    bl_description = "Solve constraints definition and apply it to the mesh"
