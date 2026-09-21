import os
import subprocess
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder='static')
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return app.send_static_file('index.html')

import re
from flask import request

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '').lower()
    
    response_data = {
        'generator': None,
        'params': {},
        'message': ''
    }
    
    # 1. Identify generator
    if 'gear' in prompt:
        response_data['generator'] = 'spur_gear'
        response_data['message'] = "Got it! Generating a Spur Gear."
        # Extract params
        teeth_match = re.search(r'(\d+)\s*teeth', prompt)
        if teeth_match: response_data['params']['num_teeth'] = int(teeth_match.group(1))
        
        module_match = re.search(r'module\s*(\d+(\.\d+)?)', prompt)
        if module_match: response_data['params']['module'] = float(module_match.group(1))
            
    elif 'flange' in prompt:
        response_data['generator'] = 'flange'
        response_data['message'] = "Alright, I'll design a Flange for you."
        holes_match = re.search(r'(\d+)\s*holes', prompt)
        if holes_match: response_data['params']['num_bolt_holes'] = int(holes_match.group(1))
            
    elif 'heat' in prompt or 'sink' in prompt:
        response_data['generator'] = 'heat_sink'
        response_data['message'] = "Designing a Heat Sink with cooling fins."
        fins_match = re.search(r'(\d+)\s*fins', prompt)
        if fins_match: response_data['params']['num_fins'] = int(fins_match.group(1))
            
    else:
        return jsonify({'error': "I'm sorry, I don't know how to generate that. Try asking for a gear, flange, or heatsink!"}), 400
        
    return jsonify(response_data)

@app.route('/api/generate/<generator_name>', methods=['POST'])
def generate(generator_name):
    script_path = os.path.join(PROJECT_DIR, 'generators', f'{generator_name}.py')
    
    if not os.path.exists(script_path):
        return jsonify({'error': f'Generator {generator_name} not found.'}), 404
        
    # Get dynamic parameters from JSON body
    params = request.json or {}
    
    # Build blender command
    cmd = [BLENDER_PATH, '--background', '--python', script_path]
    if params:
        cmd.append('--')
        for key, value in params.items():
            cmd.extend([f"--{key}", str(value)])
            
    try:
        # Run Blender headlessly to execute the generator
        result = subprocess.run(
            cmd,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Blender Error Output:", result.stderr)
            return jsonify({'error': 'Blender execution failed.'}), 500
            
        # Standardize expected output file names
        if generator_name == "heat_sink":
            stl_filename = "heatsink.stl"
        elif generator_name == "flange":
            stl_filename = "flange.stl"
        elif generator_name == "spur_gear":
            stl_filename = "spur_gear.stl"
        else:
            stl_filename = f"{generator_name}.stl"
            
        output_url = f"/output/{stl_filename}"
        return jsonify({'success': True, 'url': output_url})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/output/<path:filename>')
def serve_output(filename):
    output_dir = os.path.join(PROJECT_DIR, 'output')
    return send_from_directory(output_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
