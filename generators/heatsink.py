import bpy
import math
import os

# Parametric inputs
base_width = 40.0
base_depth = 40.0
base_height = 5.0

num_fins = 12
fin_height = 20.0
fin_thickness = 1.0

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create base plate
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, base_height / 2))
base = bpy.context.object
base.scale = (base_width, base_depth, base_height)
base.name = "HeatSink_Base"

# Create fins
fin_spacing = (base_width - fin_thickness) / (num_fins - 1)
fin_start_x = -base_width / 2 + fin_thickness / 2

for i in range(num_fins):
    x = fin_start_x + i * fin_spacing
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, base_height + fin_height / 2))
    fin = bpy.context.object
    fin.scale = (fin_thickness, base_depth, fin_height)
    fin.name = f"Fin_{i}"

# Select all and join them into one object
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active = base
bpy.ops.object.join()
heatsink = bpy.context.object
heatsink.name = "HeatSink"

# Export to STL
output_dir = r"c:\Users\Admin\OneDrive\Desktop\text-to-cad\output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "heatsink.stl")

bpy.ops.object.select_all(action='DESELECT')
heatsink.select_set(True)
bpy.context.view_layer.objects.active = heatsink
bpy.ops.wm.stl_export(filepath=output_path, export_selected_objects=True)

print(f"Exported heatsink to {output_path}")
