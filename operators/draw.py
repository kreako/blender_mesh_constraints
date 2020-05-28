from bpy.types import Operator, SpaceView3D, WindowManager
from bpy.props import BoolProperty

from . import base
from .. import drawing



class DrawingOperator(base.MeshConstraintsOperator):
    """Contains a handle to drawing callback and 2 methods to enable/disable the drawing"""

    # Handle of the drawing callback
    _handle = None

    @classmethod
    def enable(cls, context):
        """Enable the drawing, called by execute of the operator"""
        if cls._handle is None:
            cls._handle = SpaceView3D.draw_handler_add(cls._callback, (context,), "WINDOW", "POST_PIXEL")
            setattr(context.window_manager, cls._wm_property, True)

    @classmethod
    def disable(cls, context):
        """Disable the drawing, called by execute of the operator"""
        if cls._handle is not None:
            SpaceView3D.draw_handler_remove(cls._handle, "WINDOW")
        cls._handle = None
        setattr(context.window_manager, cls._wm_property, False)

    def execute(self, context):
        """Called by blender on operator execution"""
        if context.area.type != 'VIEW_3D':
            return self.warning("View3D not found, but I need it to run drawing code !")

        if getattr(context.window_manager, self.__class__._wm_property):
            # Already drawing so disable
            self.__class__.disable(context)
        else:
            # Not drawing so enable
            self.__class__.enable(context)
        # And in any case, trigger a redraw
        context.area.tag_redraw()
        return {'FINISHED'}


class MESH_CONSTRAINTS_OT_DrawConstraintsDefinition(DrawingOperator):
    bl_idname = "mesh_constraints.draw_constraints_definition"
    bl_label = "Draw constraints definition"
    bl_description = "Draw constraints definition on top of the mesh"

    _wm_property = "mesh_constraints_draw_constraints_definition"
    _callback = drawing.draw_constraints_definition
