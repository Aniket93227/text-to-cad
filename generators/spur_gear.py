import bpy
import sys
import os
import math

def clear_scene():
    """Removes default cube, light, and camera."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_parametric_part(num_teeth=24, module=1.5, thickness=6.0, bore_radius=5.0):
    # Parametric gear calculations
    pitch_radius = (num_teeth * module) / 2.0
    outer_radius = pitch_radius + module
    root_radius = pitch_radius - (1.25 * module)
    
    # 1. Base Cylinder (Outer diameter of the gear)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=num_teeth * 4,
        radius=outer_radius, 
        depth=thickness, 
        location=(0, 0, thickness / 2)
    )
    gear_obj = bpy.context.active_object
    gear_obj.name = "SpurGear"

    # 2. Cut teeth using boolean difference
    cutters = []
    gap_depth = thickness + 1.0
    
    # Simple circular cutter for tooth gaps to maintain solid modeling CSG style
    gap_radius = (outer_radius - root_radius)
    
    for i in range(num_teeth):
        angle = i * (2 * math.pi / num_teeth)
        
        # Place cutter outside to form the teeth
        x = (root_radius + gap_radius) * math.cos(angle)
        y = (root_radius + gap_radius) * math.sin(angle)
        
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=gap_radius * 0.8, # Adjust size to make the teeth look right 
            depth=gap_depth, 
            location=(x, y, thickness / 2)
        )
        cutter = bpy.context.active_object
        cutters.append(cutter)
        
        bool_mod = gear_obj.modifiers.new(name=f"CutTooth_{i}", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cutter
        
    bpy.context.view_layer.objects.active = gear_obj
    for i in range(num_teeth):
        bpy.ops.object.modifier_apply(modifier=f"CutTooth_{i}")

    # Clean up tooth cutters
    for cutter in cutters:
        bpy.data.objects.remove(cutter, do_unlink=True)

    # 3. Central Bore (Hole Cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=bore_radius, 
        depth=thickness + 1.0, 
        location=(0, 0, thickness / 2)
    )
    bore = bpy.context.active_object
    bore.name = "BoreCutter"

    bool_mod_bore = gear_obj.modifiers.new(name="CentralBore", type='BOOLEAN')
    bool_mod_bore.operation = 'DIFFERENCE'
    bool_mod_bore.object = bore
    
    bpy.context.view_layer.objects.active = gear_obj
    bpy.ops.object.modifier_apply(modifier="CentralBore")
    bpy.data.objects.remove(bore, do_unlink=True)

    # 4. Add Bevel Modifier for clean CAD edges
    bevel_mod = gear_obj.modifiers.new(name="BevelEdges", type='BEVEL')
    bevel_mod.width = 0.05
    bevel_mod.segments = 3

def export_stl(output_filepath):
    """Exports active geometry to STL format."""
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    bpy.ops.wm.stl_export(filepath=output_filepath, export_selected_objects=True)
    print(f"Successfully exported CAD model to: {output_filepath}")

if __name__ == "__main__":
    clear_scene()
    create_parametric_part(num_teeth=24, module=1.5, thickness=6.0, bore_radius=5.0)
    
    # Use absolute path for output to ensure it saves in the correct location
    output_dir = os.path.join(os.getcwd(), "output")
    output_file = os.path.join(output_dir, "spur_gear.stl")
    
    bpy.ops.object.select_all(action='DESELECT')
    if "SpurGear" in bpy.data.objects:
        bpy.data.objects["SpurGear"].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects["SpurGear"]
        export_stl(output_file)
    else:
        print("Failed to find SpurGear object for export.")
