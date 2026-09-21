import bpy
import math
import os

# Parametric inputs
flange_radius = 5.0
flange_thickness = 1.0
bore_radius = 2.0
bolt_hole_radius = 0.5
bolt_circle_radius = 3.5
num_bolt_holes = 6

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create flange body
bpy.ops.mesh.primitive_cylinder_add(radius=flange_radius, depth=flange_thickness, location=(0, 0, flange_thickness/2))
flange = bpy.context.object
flange.name = "Flange"

# Create bore
bpy.ops.mesh.primitive_cylinder_add(radius=bore_radius, depth=flange_thickness + 1.0, location=(0, 0, flange_thickness/2))
bore = bpy.context.object
bore.name = "Bore"

# Boolean difference for bore
mod_bore = flange.modifiers.new(type="BOOLEAN", name="BoreHole")
mod_bore.operation = 'DIFFERENCE'
mod_bore.object = bore
bpy.context.view_layer.objects.active = flange
bpy.ops.object.modifier_apply(modifier="BoreHole")

# Delete bore object
bpy.ops.object.select_all(action='DESELECT')
bore.select_set(True)
bpy.ops.object.delete()

# Create bolt holes
for i in range(num_bolt_holes):
    angle = i * (2 * math.pi / num_bolt_holes)
    x = bolt_circle_radius * math.cos(angle)
    y = bolt_circle_radius * math.sin(angle)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=bolt_hole_radius, depth=flange_thickness + 1.0, location=(x, y, flange_thickness/2))
    hole = bpy.context.object
    hole.name = f"BoltHole_{i}"
    
    mod_hole = flange.modifiers.new(type="BOOLEAN", name=f"BoltHoleMod_{i}")
    mod_hole.operation = 'DIFFERENCE'
    mod_hole.object = hole
    bpy.context.view_layer.objects.active = flange
    bpy.ops.object.modifier_apply(modifier=f"BoltHoleMod_{i}")
    
    bpy.ops.object.select_all(action='DESELECT')
    hole.select_set(True)
    bpy.ops.object.delete()

# Export to STL
output_dir = r"c:\Users\Admin\OneDrive\Desktop\text-to-cad\output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "flange.stl")

bpy.ops.object.select_all(action='DESELECT')
flange.select_set(True)
bpy.context.view_layer.objects.active = flange
bpy.ops.wm.stl_export(filepath=output_path, export_selected_objects=True)

print(f"Exported flange to {output_path}")
