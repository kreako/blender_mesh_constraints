# Mesh Constraints addon for blender

## What is it ?

An unfinished/unpolished/but usable blender addon.

The idea is to use constraints and a numerical solver to produce precise mesh.
Like we do on FreeCAD, on 2D sketch, but directly inside blender and on the 3D mesh.

The current very-early version can be used like this :

1. produce a mesh closely approximating the result you want
2. Set constraints (distances, angles, parallell, perpendicular, on X/Y/Z axis…)
3. Click “Solve” and the solver will position vertices where they need to be, to respect all constraints.

Here is a quick (~3 minutes) overview/introduction video to give you an idea : https://youtu.be/XsSR0tYMbCc

## Installation

Checkout the repository in your addon directory (something like `~/.config/blender/<version>/scripts/addons`)

Install sympy (tested with version 1.5.1), in your blender python package or elsewere.
You can, if necessary, add the path in solver.py, line 12 : `sys.path.append("<your-sympy-install-path>")`

## Drawbacks

For this early version, drawbacks exist :

1. The numerical solver is written in python so it is quite slow, you can see it in action, in realtime in the video around 0:29 1.
2. Only a few constraints exist right now.


## Future - todo list

- A faster solver means as well a real-time solver effect (Add constraints, and see immediately the result of it).
- The solver is already parametric but the UI do not support it, maybe a panel with a list of variables to be used in equations ?
- Add more constraints like distance between 1 vertex and a line (extended)


## Testing

With pytest, you can test the heart (and a little bit of the blender interface) of it with :

```
$ PYTHONPATH=tests/mock/ py.test --capture=no
```
