// ── DOM References ──────────────────────────────────────────────────────────
const container       = document.getElementById('viewer-3d');
const chatHistory     = document.getElementById('chat-history');
const chatInput       = document.getElementById('chat-input');
const sendBtn         = document.getElementById('send-btn');
const paramsPanel     = document.getElementById('params-panel');
const paramsContainer = document.getElementById('params-container');
const updateBtn       = document.getElementById('update-btn');
const downloadBtn     = document.getElementById('download-btn');
const loadingOverlay  = document.getElementById('loading-overlay');
const loadingText     = document.getElementById('loading-text');
const modelLabel      = document.getElementById('model-label');
const placeholderContent = container.querySelector('.placeholder-content');

// ── State ─────────────────────────────────────────────────────────────────
let scene, camera, renderer, controls, mesh;
let currentGenerator = null;
let currentParams    = {};

// ── 3D Viewer Init ────────────────────────────────────────────────────────
function init3DViewer() {
    scene = new THREE.Scene();

    // Studio-style lighting
    scene.add(new THREE.AmbientLight(0x404040, 1.2));
    const key = new THREE.DirectionalLight(0xffffff, 1.0);
    key.position.set(1, 2, 1.5);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0x8080ff, 0.4);
    fill.position.set(-1, -1, -1);
    scene.add(fill);

    camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(60, 45, 60);

    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.autoRotate    = true;
    controls.autoRotateSpeed = 0.8;
    controls.minDistance   = 10;
    controls.maxDistance   = 300;

    window.addEventListener('resize', onWindowResize);
}

function onWindowResize() {
    if (!camera || !renderer) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    if (controls) controls.update();
    if (renderer && scene && camera) renderer.render(scene, camera);
}

// ── Load STL into viewer ──────────────────────────────────────────────────
function loadSTL(url, label) {
    if (placeholderContent) placeholderContent.style.display = 'none';
    if (!container.contains(renderer.domElement)) container.appendChild(renderer.domElement);

    // Clean old mesh
    if (mesh) { scene.remove(mesh); mesh.geometry.dispose(); mesh.material.dispose(); }

    const loader = new THREE.STLLoader();
    loader.load(url + '?t=' + Date.now(), (geometry) => {
        const material = new THREE.MeshStandardMaterial({
            color: 0x60a5fa, metalness: 0.6, roughness: 0.3
        });
        mesh = new THREE.Mesh(geometry, material);

        // Center and auto-scale
        geometry.computeBoundingBox();
        const center = new THREE.Vector3();
        geometry.boundingBox.getCenter(center);
        mesh.position.sub(center);

        const size = new THREE.Vector3();
        geometry.boundingBox.getSize(size);
        const scale = 35 / Math.max(size.x, size.y, size.z);
        mesh.scale.setScalar(scale);
        mesh.rotation.x = -Math.PI / 2;

        scene.add(mesh);

        // Update UI
        downloadBtn.href = url;
        downloadBtn.setAttribute('download', label + '.stl');
        downloadBtn.classList.remove('disabled');
        modelLabel.textContent = `Loaded: ${label}`;

        hideLoading();
        addMessage('✅ Model generated and loaded! Use the Parameters panel to tweak and regenerate.', 'ai');
    }, undefined, () => {
        hideLoading();
        addMessage('❌ Failed to load the 3D model. Check server logs.', 'ai');
    });
}

// ── Chat helpers ──────────────────────────────────────────────────────────
function addMessage(text, sender) {
    const wrap = document.createElement('div');
    wrap.className = `chat-msg ${sender}-msg`;

    if (sender === 'ai') {
        const icon = document.createElement('div');
        icon.className = 'msg-icon';
        icon.textContent = '🤖';
        const body = document.createElement('div');
        body.className = 'msg-text';
        body.textContent = text;
        wrap.appendChild(icon);
        wrap.appendChild(body);
    } else {
        const body = document.createElement('div');
        body.className = 'msg-text';
        body.textContent = text;
        wrap.appendChild(body);
    }

    chatHistory.appendChild(wrap);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return wrap;
}

function addTyping() {
    const wrap = document.createElement('div');
    wrap.className = 'chat-msg ai-msg';
    wrap.id = 'typing-msg';
    wrap.innerHTML = `<div class="msg-icon">🤖</div><div class="msg-text"><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
    chatHistory.appendChild(wrap);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function removeTyping() {
    document.getElementById('typing-msg')?.remove();
}

// ── Loading overlay ───────────────────────────────────────────────────────
function showLoading(text = 'Running Blender headlessly...') {
    loadingText.textContent = text;
    loadingOverlay.classList.remove('hidden');
}
function hideLoading() { loadingOverlay.classList.add('hidden'); }

// ── Parameters UI ─────────────────────────────────────────────────────────
const PARAM_LABELS = {
    num_teeth: 'Number of Teeth', module: 'Module', thickness: 'Thickness (mm)',
    bore_radius: 'Bore Radius (mm)', flange_radius: 'Flange Radius (mm)',
    flange_thickness: 'Flange Thickness (mm)', bolt_hole_radius: 'Bolt Hole Radius (mm)',
    bolt_circle_radius: 'Bolt Circle Radius (mm)', num_bolt_holes: 'Number of Bolt Holes',
    base_width: 'Base Width (mm)', base_depth: 'Base Depth (mm)',
    base_height: 'Base Height (mm)', num_fins: 'Number of Fins',
    fin_height: 'Fin Height (mm)', fin_thickness: 'Fin Thickness (mm)'
};

function buildParamsUI(params) {
    paramsContainer.innerHTML = '';
    if (!params || Object.keys(params).length === 0) {
        paramsPanel.classList.add('hidden');
        return;
    }
    for (const [key, value] of Object.entries(params)) {
        const group = document.createElement('div');
        group.className = 'param-group';
        const label = document.createElement('label');
        label.textContent = PARAM_LABELS[key] || key;
        label.htmlFor = `param-${key}`;
        const input = document.createElement('input');
        input.type = 'number';
        input.step = 'any';
        input.min = '0.1';
        input.id = `param-${key}`;
        input.value = value;
        group.appendChild(label);
        group.appendChild(input);
        paramsContainer.appendChild(group);
    }
    paramsPanel.classList.remove('hidden');
}

// ── API calls ─────────────────────────────────────────────────────────────
async function runGenerate(generatorName, params) {
    const label = generatorName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    showLoading(`Generating ${label}... (may take ~15s)`);
    try {
        const res  = await fetch(`/api/generate/${generatorName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        const data = await res.json();
        if (data.success) {
            loadSTL(data.url, label);
        } else {
            hideLoading();
            addMessage(`❌ Generation failed: ${data.error}`, 'ai');
        }
    } catch (e) {
        hideLoading();
        addMessage('❌ Network error. Is the Flask server running?', 'ai');
    }
}

async function handleChat(prompt) {
    addMessage(prompt, 'user');
    chatInput.value = '';
    sendBtn.disabled = true;
    addTyping();

    try {
        const res  = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        const data = await res.json();
        removeTyping();

        if (data.error) {
            addMessage(data.error, 'ai');
            return;
        }

        addMessage(data.message, 'ai');
        currentGenerator = data.generator;
        currentParams    = data.params;
        buildParamsUI(currentParams);
        await runGenerate(currentGenerator, currentParams);
    } catch (e) {
        removeTyping();
        addMessage('❌ Error talking to the server.', 'ai');
    } finally {
        sendBtn.disabled = false;
    }
}

// ── Event Listeners ───────────────────────────────────────────────────────
sendBtn.addEventListener('click', () => {
    const text = chatInput.value.trim();
    if (text) handleChat(text);
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const text = chatInput.value.trim();
        if (text) handleChat(text);
    }
});

// Suggestion chips
document.querySelectorAll('.suggestion-chip').forEach(chip => {
    chip.addEventListener('click', () => handleChat(chip.dataset.prompt));
});

// Regenerate button
updateBtn.addEventListener('click', () => {
    if (!currentGenerator) return;
    const newParams = {};
    for (const key of Object.keys(currentParams)) {
        const el = document.getElementById(`param-${key}`);
        if (el) newParams[key] = parseFloat(el.value) || currentParams[key];
    }
    currentParams = newParams;
    addMessage('Regenerating with updated parameters...', 'ai');
    runGenerate(currentGenerator, currentParams);
});

// ── Start ─────────────────────────────────────────────────────────────────
init3DViewer();
animate();
