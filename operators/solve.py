import bmesh

from . import base
from .. import props
from .. import solver
from .. import log


class MESH_CONSTRAINTS_OT_Solve(base.MeshConstraintsOperator):
    bl_idname = "mesh_constraints.solve"
    bl_label = "Solve"
    bl_description = "Solve constraints definition and apply it to the mesh"

    @classmethod
    def poll(cls, context):
        # A selected mesh in edit mode : I'm in, but not for the rest
        o = context.object
        return o is not None and o.type == "MESH" and context.mode == "EDIT_MESH" and "MeshConstraintGenerator" in o and len(o.MeshConstraintGenerator[0].constraints) > 0

    def execute(self, context):
        if context.area.type != "VIEW_3D":
            return self.warning("I'm not able to find VIEW_3D, so I won't run")

        o = context.edit_object
        if "MeshConstraintGenerator" not in o:
            return self.warning("I'm not able to find constraints on this mesh")

        log.logger().debug("start")

        mesh = o.data
        bm = bmesh.from_edit_mesh(mesh)
        mc = props.MeshConstraints(o.MeshConstraintGenerator)

        mc.clear_in_errors()

        ConstraintsKind = props.ConstraintsKind

        s = solver.Solver([solver.MeshPoint(v.index, v.co) for v in bm.verts])
        for index, c in enumerate(mc):
            log.logger().debug(f"{index}: {c}")
            if c.kind == ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES:
                s.distance_2_vertices(index, c.point0, c.point1, c.distance)
            elif c.kind == ConstraintsKind.FIX_X_COORD:
                s.fix_x(index, c.point, c.x)
            elif c.kind == ConstraintsKind.FIX_Y_COORD:
                s.fix_y(index, c.point, c.y)
            elif c.kind == ConstraintsKind.FIX_Z_COORD:
                s.fix_z(index, c.point, c.z)
            elif c.kind == ConstraintsKind.FIX_XY_COORD:
                s.fix_x(index, c.point, c.x)
                s.fix_y(index, c.point, c.y)
            elif c.kind == ConstraintsKind.FIX_XZ_COORD:
                s.fix_x(index, c.point, c.x)
                s.fix_z(index, c.point, c.z)
            elif c.kind == ConstraintsKind.FIX_YZ_COORD:
                s.fix_y(index, c.point, c.y)
                s.fix_z(index, c.point, c.z)
            elif c.kind == ConstraintsKind.FIX_XYZ_COORD:
                s.fix_x(index, c.point, c.x)
                s.fix_y(index, c.point, c.y)
                s.fix_z(index, c.point, c.z)
            elif c.kind == ConstraintsKind.PARALLEL:
                s.parallel(index, c.point0, c.point1, c.point2, c.point3)
            elif c.kind == ConstraintsKind.PERPENDICULAR:
                s.perpendicular(index, c.point0, c.point1, c.point2, c.point3)
            elif c.kind == ConstraintsKind.ON_X:
                s.on_x(index, c.point0, c.point1)
            elif c.kind == ConstraintsKind.ON_Y:
                s.on_y(index, c.point0, c.point1)
            elif c.kind == ConstraintsKind.ON_Z:
                s.on_z(index, c.point0, c.point1)
            else:
                raise Exception(f"Unknown kind of constraints {c.kind}")

        solution = s.solve()
        log.logger().debug(f"solution: {solution}")

        if solution["solved"]:
            for point in solution["points"]:
                bm.verts[point.index].co = point.xyz
            bmesh.update_edit_mesh(mesh, loop_triangles=True, destructive=False)
            self.info("Solved !")
            context.area.tag_redraw()
            log.logger().debug("end ok")
            return {"FINISHED"}
        else:
            nb_in_errors = len(solution["equations_in_error"])
            for in_error in solution["equations_in_error"]:
                mc.set_in_error(in_error)
            context.area.tag_redraw()
            log.logger().debug("end nok")
            if nb_in_errors:
                return self.error(
                    f"Not Solved : Constraints did not converged, {nb_in_errors} conflicting..."
                )
            else:
                return self.error(f"Not Solved : Constraints did not converged")
