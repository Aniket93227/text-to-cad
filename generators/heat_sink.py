import bpy
import sys
import os

def clear_scene():
    """Removes default cube, light, and camera."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_parametric_part(base_width=40.0, base_depth=40.0, base_height=5.0, num_fins=12, fin_height=20.0, fin_thickness=1.0):
    # 1. Base Plate
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, base_height / 2))
    base_obj = bpy.context.active_object
    base_obj.scale = (base_width, base_depth, base_height)
    base_obj.name = "BasePlate"

    # 2. Fins
    fin_spacing = (base_width - fin_thickness) / max(1, (num_fins - 1))
    fin_start_x = -base_width / 2 + fin_thickness / 2

    for i in range(num_fins):
        x = fin_start_x + i * fin_spacing
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, base_height + fin_height / 2))
        fin = bpy.context.active_object
        fin.scale = (fin_thickness, base_depth, fin_height)
        fin.name = f"Fin_{i}"
        fin.select_set(True)

    # Ensure all are selected and join
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = base_obj
    bpy.ops.object.join()

    joined_obj = bpy.context.active_object
    joined_obj.name = "HeatSink"
    
    # 3. Add Bevel Modifier for clean CAD edges
    bevel_mod = joined_obj.modifiers.new(name="BevelEdges", type='BEVEL')
    bevel_mod.width = 0.05
    bevel_mod.segments = 3
    
    # Ensure it is selected for export
    bpy.ops.object.select_all(action='DESELECT')
    joined_obj.select_set(True)
    bpy.context.view_layer.objects.active = joined_obj

def export_stl(output_filepath):
    """Exports active geometry to STL format."""
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    bpy.ops.wm.stl_export(filepath=output_filepath, export_selected_objects=True)
    print(f"Successfully exported CAD model to: {output_filepath}")

if __name__ == "__main__":
    clear_scene()
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_width", type=float, default=40.0)
    parser.add_argument("--base_depth", type=float, default=40.0)
    parser.add_argument("--base_height", type=float, default=5.0)
    parser.add_argument("--num_fins", type=int, default=12)
    parser.add_argument("--fin_height", type=float, default=20.0)
    parser.add_argument("--fin_thickness", type=float, default=1.0)
    
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
        args, _ = parser.parse_known_args(argv)
        create_parametric_part(
            base_width=args.base_width,
            base_depth=args.base_depth,
            base_height=args.base_height,
            num_fins=args.num_fins,
            fin_height=args.fin_height,
            fin_thickness=args.fin_thickness
        )
    else:
        create_parametric_part()
    
    
    # Use absolute path for output to ensure it saves in the correct location
    output_dir = os.path.join(os.getcwd(), "output")
    output_file = os.path.join(output_dir, "heatsink.stl")
    export_stl(output_file)
