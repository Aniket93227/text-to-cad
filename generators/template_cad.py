import bpy
import sys

def clear_scene():
    """Removes default cube, light, and camera."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_parametric_part(radius=2.0, height=1.0, hole_radius=0.5):
    # 1. Base Cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, 
        depth=height, 
        location=(0, 0, 0)
    )
    base_obj = bpy.context.active_object
    base_obj.name = "BasePart"

    # 2. Central Bore (Hole Cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=hole_radius, 
        depth=height + 0.2, 
        location=(0, 0, 0)
    )
    cutter = bpy.context.active_object
    cutter.name = "Cutter"

    # 3. Apply CSG Boolean Difference
    bool_mod = base_obj.modifiers.new(name="CentralBore", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter
    
    bpy.context.view_layer.objects.active = base_obj
    bpy.ops.object.modifier_apply(modifier="CentralBore")

    # Clean up cutter geometry
    bpy.data.objects.remove(cutter, do_unlink=True)

    # 4. Add Bevel Modifier for clean CAD edges
    bevel_mod = base_obj.modifiers.new(name="BevelEdges", type='BEVEL')
    bevel_mod.width = 0.05
    bevel_mod.segments = 3

def export_stl(output_filepath):
    """Exports active geometry to STL format."""
    bpy.ops.wm.stl_export(filepath=output_filepath)
    print(f"Successfully exported CAD model to: {output_filepath}")

if __name__ == "__main__":
    clear_scene()
    create_parametric_part(radius=3.0, height=1.5, hole_radius=0.8)
    export_stl("output/part_preview.stl")