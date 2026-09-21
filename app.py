import os
import re
import subprocess
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='static')

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Default parameters for each generator (shown in UI even if not specified in prompt)
GENERATOR_DEFAULTS = {
    'spur_gear': {
        'num_teeth': 24,
        'module': 1.5,
        'thickness': 6.0,
        'bore_radius': 5.0
    },
    'flange': {
        'flange_radius': 5.0,
        'flange_thickness': 1.0,
        'bore_radius': 2.0,
        'bolt_hole_radius': 0.5,
        'bolt_circle_radius': 3.5,
        'num_bolt_holes': 6
    },
    'heat_sink': {
        'base_width': 40.0,
        'base_depth': 40.0,
        'base_height': 5.0,
        'num_fins': 12,
        'fin_height': 20.0,
        'fin_thickness': 1.0
    }
}

# Output STL filenames per generator
STL_NAMES = {
    'heat_sink': 'heatsink.stl',
    'flange': 'flange.stl',
    'spur_gear': 'spur_gear.stl'
}


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '').lower()

    generator = None
    extracted = {}
    message = ''

    # --- Identify generator ---
    if any(w in prompt for w in ['gear', 'spur']):
        generator = 'spur_gear'
        message = "Got it! I'll generate a Spur Gear for you."
        m = re.search(r'(\d+)\s*teeth', prompt)
        if m: extracted['num_teeth'] = int(m.group(1))
        m = re.search(r'module\s*[=:of]?\s*(\d+(?:\.\d+)?)', prompt)
        if m: extracted['module'] = float(m.group(1))
        m = re.search(r'thickness\s*[=:of]?\s*(\d+(?:\.\d+)?)', prompt)
        if m: extracted['thickness'] = float(m.group(1))
        m = re.search(r'bore\s*[=:of]?\s*(\d+(?:\.\d+)?)', prompt)
        if m: extracted['bore_radius'] = float(m.group(1))

    elif 'flange' in prompt:
        generator = 'flange'
        message = "Alright! Designing a Pipe Flange."
        m = re.search(r'(\d+)\s*(?:bolt\s*)?holes', prompt)
        if m: extracted['num_bolt_holes'] = int(m.group(1))
        m = re.search(r'radius\s*[=:of]?\s*(\d+(?:\.\d+)?)', prompt)
        if m: extracted['flange_radius'] = float(m.group(1))
        m = re.search(r'thickness\s*[=:of]?\s*(\d+(?:\.\d+)?)', prompt)
        if m: extracted['flange_thickness'] = float(m.group(1))
        m = re.search(r'bore\s*[=:of]?\s*(\d+(?:\.\d+)?)', prompt)
        if m: extracted['bore_radius'] = float(m.group(1))

    elif any(w in prompt for w in ['heat', 'sink', 'heatsink', 'cooler', 'fin']):
        generator = 'heat_sink'
        message = "Sure! Building a CPU Heat Sink with cooling fins."
        m = re.search(r'(\d+)\s*fins', prompt)
        if m: extracted['num_fins'] = int(m.group(1))
        m = re.search(r'fin\s*height\s*[=:of]?\s*(\d+(?:\.\d+)?)', prompt)
        if m: extracted['fin_height'] = float(m.group(1))
        m = re.search(r'(?:base\s*)?width\s*[=:of]?\s*(\d+(?:\.\d+)?)', prompt)
        if m: extracted['base_width'] = float(m.group(1))
        m = re.search(r'(?:base\s*)?height\s*[=:of]?\s*(\d+(?:\.\d+)?)', prompt)
        if m: extracted['base_height'] = float(m.group(1))
    else:
        return jsonify({'error': "I don't know how to make that yet. Try: gear, flange, or heat sink!"}), 400

    # Merge defaults with extracted values so ALL params are shown in the UI
    params = dict(GENERATOR_DEFAULTS[generator])
    params.update(extracted)

    return jsonify({'generator': generator, 'params': params, 'message': message})


@app.route('/api/generate/<generator_name>', methods=['POST'])
def generate(generator_name):
    script_path = os.path.join(PROJECT_DIR, 'generators', f'{generator_name}.py')

    if not os.path.exists(script_path):
        return jsonify({'error': f'Generator "{generator_name}" not found.'}), 404

    params = request.json or {}

    # Build headless Blender command with dynamic params
    cmd = [BLENDER_PATH, '--background', '--python', script_path]
    if params:
        cmd.append('--')
        for key, value in params.items():
            cmd.extend([f'--{key}', str(value)])

    try:
        result = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True)

        if result.returncode != 0:
            print("BLENDER STDERR:", result.stderr)
            return jsonify({'error': 'Blender execution failed. Check server logs.'}), 500

        stl_filename = STL_NAMES.get(generator_name, f'{generator_name}.stl')
        return jsonify({'success': True, 'url': f'/output/{stl_filename}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/output/<path:filename>')
def serve_output(filename):
    output_dir = os.path.join(PROJECT_DIR, 'output')
    return send_from_directory(output_dir, filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
