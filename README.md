# Text-to-CAD AI Generator

A conversational, **ChatGPT-style** parametric CAD generator powered by Blender. Type a natural language prompt — like *"Give me a spur gear with 32 teeth"* — and a 3D STL model is generated and rendered interactively in your browser.

## Features

- 🤖 **Natural Language Prompts** — Describe any part in plain English
- 🔩 **Parametric Generators** — Pipe Flange, CPU Heat Sink, Spur Gear
- 🎛️ **Live Parameter Editor** — Tweak dimensions and regenerate instantly
- 🌐 **3D Browser Viewer** — Orbit, zoom, and pan the model with your mouse
- ⬇️ **STL Download** — Export the model for 3D printing or CAD software
- 🤖 **CI/CD Pipeline** — GitHub Actions automatically validates all generators on push

## Project Structure

```
text-to-cad/
├── generators/
│   ├── template_cad.py       # Base template for new generators
│   ├── flange.py             # Pipe flange with bolt holes
│   ├── heat_sink.py          # CPU heat sink with cooling fins
│   └── spur_gear.py          # Industrial spur gear
├── static/
│   ├── index.html            # Frontend UI
│   ├── style.css             # Premium dark glassmorphism styling
│   └── script.js             # 3D viewer + chat logic
├── output/                   # Generated STL files (gitignored)
├── .github/workflows/
│   └── cad_build.yml         # CI/CD pipeline
├── app.py                    # Flask backend + NLP parser
├── requirements.txt
└── .gitignore
```

## Getting Started

### Prerequisites
- Python 3.10+
- [Blender 4.0+](https://www.blender.org/download/) installed on your system

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

### 3. Open the Dashboard

Navigate to **http://localhost:5000** in your browser.

## Usage

Type prompts into the chat box. Examples:

| Prompt | Generated Model |
|--------|----------------|
| `Give me a spur gear with 32 teeth and module 2` | `output/spur_gear.stl` |
| `Create a pipe flange with 8 bolt holes` | `output/flange.stl` |
| `Design a heat sink with 16 fins` | `output/heatsink.stl` |

After generation, use the **Parameters** panel on the right to fine-tune dimensions and click **Regenerate**.

## Running Generators Headlessly

Each generator can also be run directly:

```bash
# Default parameters
blender --background --python generators/spur_gear.py

# Custom parameters
blender --background --python generators/spur_gear.py -- --num_teeth 32 --module 2 --thickness 8
blender --background --python generators/flange.py -- --num_bolt_holes 8 --flange_radius 7
blender --background --python generators/heat_sink.py -- --num_fins 16 --fin_height 25
```

## CI/CD

The GitHub Actions pipeline (`.github/workflows/cad_build.yml`) automatically runs and validates all Blender generator scripts on every push to `main`.
