#  exec(open("/home/noumir/rust/blender-constraints/mesh_constraints/__init__.py").read(), {"__file__": "/home/noumir/rust/blender-constraints/mesh_constraints/__init__.py"})

bl_info = {
    "name": "Mesh Constraints",
    "version": (0, 0, 1),
    "author": "Kreako",
    "blender": (2, 82, 0),
    "description": "Mesh constraints solver for auto-positionning of vertices",
    "location": "View3D > Sidebar > Constraints Tab",
    "wiki_url": "TODO",
    "category": "Mesh"}


# import os.path
# directory = os.path.dirname(os.path.abspath(__file__))
# import sys
# sys.path.append(directory)


reload = False
if "props" in locals():
    reload = True


import bpy
from bpy.props import CollectionProperty, BoolProperty
from bpy.utils import register_class, unregister_class
from bpy.types import WindowManager

from . import props
from . import drawing
from . import operators
from . import panels

if reload:
    # When using script.reload in blender
    # For development...
    import importlib
    importlib.reload(props)
    importlib.reload(drawing)
    importlib.reload(operators)
    operators.reload()
    importlib.reload(panels)


def register():
    # Properties
    WindowManager.mesh_constraints_draw_constraints_definition = BoolProperty(default=False)
    WindowManager.mesh_constraints_draw_constraints_violation = BoolProperty(default=False)

    register_class(props.MeshConstraintProperties)
    register_class(props.MeshConstraintsContainer)
    bpy.types.Object.MeshConstraintGenerator = CollectionProperty(type=props.MeshConstraintsContainer)

    # Operators
    register_class(operators.MESH_CONSTRAINTS_OT_DrawConstraintsDefinition)
    register_class(operators.MESH_CONSTRAINTS_OT_DrawConstraintsViolation)
    register_class(operators.MESH_CONSTRAINTS_OT_Solve)
    register_class(operators.MESH_CONSTRAINTS_OT_ConstraintDistance2Vertices)
    register_class(operators.MESH_CONSTRAINTS_OT_DeleteConstraint)

    # Panels
    register_class(panels.MeshConstraintsPanelMain)
    register_class(panels.MeshConstraintsPanelAdd)
    register_class(panels.MeshConstraintsPanelItems)

    print("register", props.ConstraintsKind.DISTANCE_BETWEEN_2_VERTICES)


def unregister():
    # Panels
    unregister_class(panels.MeshConstraintsPanelAdd)
    unregister_class(panels.MeshConstraintsPanelItems)
    unregister_class(panels.MeshConstraintsPanelMain)

    # Operators
    unregister_class(operators.MESH_CONSTRAINTS_OT_DrawConstraintsDefinition)
    unregister_class(operators.MESH_CONSTRAINTS_OT_DrawConstraintsViolation)
    unregister_class(operators.MESH_CONSTRAINTS_OT_Solve)
    unregister_class(operators.MESH_CONSTRAINTS_OT_ConstraintDistance2Vertices)
    unregister_class(operators.MESH_CONSTRAINTS_OT_DeleteConstraint)

    # Properties
    unregister_class(props.MeshConstraintsContainer)
    unregister_class(props.MeshConstraintProperties)
    print("unregister")
