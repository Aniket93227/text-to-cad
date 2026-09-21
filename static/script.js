// 3D Viewer Setup
const container = document.getElementById('viewer-3d');
const downloadBtn = document.getElementById('download-btn');
const placeholder = document.querySelector('.placeholder-text');
const chatHistory = document.getElementById('chat-history');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const paramsPanel = document.getElementById('params-panel');
const paramsContainer = document.getElementById('params-container');
const updateBtn = document.getElementById('update-btn');

let scene, camera, renderer, controls, mesh;
let currentGenerator = null;
let currentParams = {};

function init3DViewer() {
    scene = new THREE.Scene();
    const ambientLight = new THREE.AmbientLight(0x404040, 1.5);
    scene.add(ambientLight);
    
    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight1.position.set(1, 1, 1).normalize();
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight2.position.set(-1, -1, -1).normalize();
    scene.add(directionalLight2);

    camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(50, 50, 50);

    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.0;

    window.addEventListener('resize', onWindowResize, false);
}

function onWindowResize() {
    if (!camera || !renderer) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function loadSTL(url) {
    if (placeholder) placeholder.style.display = 'none';
    if (!container.contains(renderer.domElement)) container.appendChild(renderer.domElement);

    if (mesh) {
        scene.remove(mesh);
        mesh.geometry.dispose();
        mesh.material.dispose();
    }

    const loader = new THREE.STLLoader();
    
    // Add cache buster to force reload
    const fetchUrl = url + "?t=" + new Date().getTime();
    
    loader.load(fetchUrl, function (geometry) {
        const material = new THREE.MeshStandardMaterial({ 
            color: 0x60a5fa, metalness: 0.5, roughness: 0.4
        });
        mesh = new THREE.Mesh(geometry, material);
        
        geometry.computeBoundingBox();
        const center = new THREE.Vector3();
        geometry.boundingBox.getCenter(center);
        mesh.position.sub(center);

        const size = new THREE.Vector3();
        geometry.boundingBox.getSize(size);
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 30 / maxDim;
        mesh.scale.set(scale, scale, scale);
        mesh.rotation.x = -Math.PI / 2;

        scene.add(mesh);
        downloadBtn.href = url;
        downloadBtn.classList.remove('disabled');
        
        addMessage("Model generated and loaded successfully!", "ai");
    }, undefined, (error) => {
        addMessage("Failed to load 3D model.", "ai");
    });
}

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `chat-msg ${sender}-msg`;
    div.innerText = text;
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function buildParamsUI(params) {
    paramsContainer.innerHTML = '';
    if (Object.keys(params).length === 0) {
        paramsPanel.classList.add('hidden');
        return;
    }
    
    for (const [key, value] of Object.entries(params)) {
        const group = document.createElement('div');
        group.className = 'param-group';
        
        const label = document.createElement('label');
        label.innerText = key;
        
        const input = document.createElement('input');
        input.type = "number";
        input.step = "any";
        input.id = `param-${key}`;
        input.value = value;
        
        group.appendChild(label);
        group.appendChild(input);
        paramsContainer.appendChild(group);
    }
    paramsPanel.classList.remove('hidden');
}

async function handleGenerate(generatorName, params) {
    try {
        const res = await fetch(`/api/generate/${generatorName}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(params)
        });
        const data = await res.json();
        if (data.success) {
            loadSTL(data.url);
        } else {
            addMessage(`Generation failed: ${data.error}`, "ai");
        }
    } catch(e) {
        addMessage("Network error during generation.", "ai");
    }
}

async function handleChat() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    chatInput.value = '';
    addMessage(text, 'user');
    
    sendBtn.disabled = true;
    addMessage("Thinking...", 'ai');
    
    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ prompt: text })
        });
        const data = await res.json();
        
        // Remove "Thinking..." message
        chatHistory.lastChild.remove();
        
        if (data.error) {
            addMessage(data.error, "ai");
        } else {
            addMessage(data.message, "ai");
            currentGenerator = data.generator;
            currentParams = data.params;
            
            buildParamsUI(currentParams);
            addMessage(`Running Blender for ${currentGenerator}...`, "ai");
            await handleGenerate(currentGenerator, currentParams);
        }
    } catch(e) {
        chatHistory.lastChild.remove();
        addMessage("Error processing chat.", "ai");
    } finally {
        sendBtn.disabled = false;
    }
}

updateBtn.addEventListener('click', () => {
    if (!currentGenerator) return;
    
    // Gather updated params
    const newParams = {};
    for (const key of Object.keys(currentParams)) {
        const val = document.getElementById(`param-${key}`).value;
        newParams[key] = parseFloat(val);
    }
    
    currentParams = newParams;
    addMessage("Regenerating with new parameters...", "ai");
    handleGenerate(currentGenerator, currentParams);
});

sendBtn.addEventListener('click', handleChat);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleChat();
});

init3DViewer();
animate();
