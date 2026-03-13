# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""3D Fibonacci-Spirale der Simulationstheorie-Indizien -- WebGL/Three.js"""
import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from network.chroma_client import get_chroma_client

client = get_chroma_client()
coll = client.get_collection("simulation_evidence")
r = coll.get(include=["metadatas", "documents"])

entries = sorted(
    zip(r["ids"], r["metadatas"], r["documents"]),
    key=lambda x: x[0]
)

COLORS = {"L": "#4488ff", "P": "#ff4444", "I": "#44ff88", "S": "#ffcc44"}
LABELS = {"L": "Logisch", "P": "Physikalisch", "I": "Informationell", "S": "Strukturell"}
COMPLEMENTS = {"L": "I", "I": "L", "S": "P", "P": "S"}

GOLDEN_ANGLE = 137.508  # degrees

points = []
for i, (eid, meta, doc) in enumerate(entries):
    cat = meta.get("qbase", meta.get("category", "?"))[0].upper()
    angle_deg = i * GOLDEN_ANGLE
    angle_rad = math.radians(angle_deg)
    radius = math.sqrt(i + 1) * 2.0
    x = radius * math.cos(angle_rad)
    z_three = radius * math.sin(angle_rad)  # three.js z = our y
    y_three = i * 0.6  # height = iteration
    
    strength = meta.get("strength", "mittel")
    branch = meta.get("branch_count", 3)
    
    points.append({
        "idx": i,
        "id": eid,
        "cat": cat,
        "color": COLORS.get(cat, "#ffffff"),
        "label": LABELS.get(cat, "?"),
        "x": round(x, 3),
        "y": round(y_three, 3),
        "z": round(z_three, 3),
        "strength": strength,
        "branches": branch,
        "doc": doc[:120].replace('"', "'").replace("\n", " "),
        "complement": COMPLEMENTS.get(cat, "?"),
    })

VECTOR_BOUNDARIES = [
    (0, 5, "V1-V4"),
    (6, 10, "V5"),
    (11, 16, "V6"),
    (17, 22, "V7"),
    (23, 28, "V8"),
    (29, 32, "V9"),
    (33, 38, "V10"),
    (39, 54, "V11"),
]

phi_split_idx = int(len(points) * 0.618)

html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>CORE Fibonacci-Spirale — 55 Indizien, 11 Vektoren</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0a0a0f; overflow: hidden; font-family: 'Segoe UI', sans-serif; color: #ccc; }}
  #info {{
    position: fixed; top: 20px; left: 20px; z-index: 10;
    background: rgba(10,10,20,0.85); padding: 20px; border-radius: 12px;
    border: 1px solid rgba(100,100,255,0.2); max-width: 320px;
    backdrop-filter: blur(10px);
  }}
  #info h1 {{ font-size: 18px; color: #fff; margin-bottom: 8px; }}
  #info p {{ font-size: 12px; line-height: 1.5; }}
  .legend {{ display: flex; gap: 12px; margin-top: 10px; flex-wrap: wrap; }}
  .legend span {{ display: flex; align-items: center; gap: 4px; font-size: 11px; }}
  .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
  #tooltip {{
    position: fixed; display: none; z-index: 20;
    background: rgba(10,10,30,0.92); padding: 12px 16px; border-radius: 8px;
    border: 1px solid rgba(100,100,255,0.3); max-width: 360px;
    font-size: 12px; line-height: 1.5; pointer-events: none;
    backdrop-filter: blur(8px);
  }}
  #tooltip .tt-cat {{ font-weight: bold; font-size: 14px; }}
  #stats {{
    position: fixed; bottom: 20px; right: 20px; z-index: 10;
    background: rgba(10,10,20,0.85); padding: 14px 18px; border-radius: 12px;
    border: 1px solid rgba(100,100,255,0.2); font-size: 12px;
    backdrop-filter: blur(10px);
  }}
</style>
</head>
<body>
<div id="info">
  <h1>CORE — Fibonacci-Spirale</h1>
  <p><strong>55</strong> Indizien · <strong>11</strong> Vektoren · <strong>Fib(10)</strong></p>
  <p>Goldener Winkel: 137.508° · Phi-Delta: 0.049 = Ω<sub>b</sub></p>
  <div class="legend">
    <span><span class="dot" style="background:#4488ff"></span> Logisch</span>
    <span><span class="dot" style="background:#ff4444"></span> Physikalisch</span>
    <span><span class="dot" style="background:#44ff88"></span> Informationell</span>
    <span><span class="dot" style="background:#ffcc44"></span> Strukturell</span>
  </div>
</div>
<div id="tooltip"></div>
<div id="stats">
  <div>L: {sum(1 for p in points if p['cat']=='L')} · P: {sum(1 for p in points if p['cat']=='P')} · I: {sum(1 for p in points if p['cat']=='I')} · S: {sum(1 for p in points if p['cat']=='S')}</div>
  <div style="margin-top:4px;">Φ-Schnitt bei Indiz #{phi_split_idx + 1}</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const DATA = {json.dumps(points)};
const PHI_IDX = {phi_split_idx};

let scene, camera, renderer, controls, raycaster, mouse, spheres = [];
let autoRotate = true;

function init() {{
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0a0a0f, 0.008);

  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.position.set(25, 20, 25);
  camera.lookAt(0, 15, 0);

  renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  document.body.appendChild(renderer.domElement);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.target.set(0, 15, 0);

  raycaster = new THREE.Raycaster();
  raycaster.params.Points = {{ threshold: 0.8 }};
  mouse = new THREE.Vector2();

  // Ambient light
  scene.add(new THREE.AmbientLight(0x222244, 0.5));
  
  // Point lights
  const pl1 = new THREE.PointLight(0x4488ff, 1, 80);
  pl1.position.set(10, 30, 10);
  scene.add(pl1);
  const pl2 = new THREE.PointLight(0xff4444, 0.6, 80);
  pl2.position.set(-10, 10, -10);
  scene.add(pl2);

  // Spiral curve
  const spiralPts = [];
  for (let i = 0; i < DATA.length; i++) {{
    spiralPts.push(new THREE.Vector3(DATA[i].x, DATA[i].y, DATA[i].z));
  }}
  const curve = new THREE.CatmullRomCurve3(spiralPts);
  const tubeGeo = new THREE.TubeGeometry(curve, 200, 0.08, 8, false);
  const tubeMat = new THREE.MeshBasicMaterial({{ color: 0x334466, transparent: true, opacity: 0.4 }});
  scene.add(new THREE.Mesh(tubeGeo, tubeMat));

  // Data points
  DATA.forEach((p, i) => {{
    const size = 0.3 + (p.branches || 3) * 0.04;
    const geo = new THREE.SphereGeometry(size, 16, 16);
    const mat = new THREE.MeshStandardMaterial({{
      color: new THREE.Color(p.color),
      emissive: new THREE.Color(p.color),
      emissiveIntensity: 0.6,
      metalness: 0.3,
      roughness: 0.4,
    }});
    const sphere = new THREE.Mesh(geo, mat);
    sphere.position.set(p.x, p.y, p.z);
    sphere.userData = p;
    scene.add(sphere);
    spheres.push(sphere);

    // Glow sprite
    const spriteMat = new THREE.SpriteMaterial({{
      map: createGlowTexture(p.color),
      transparent: true,
      opacity: 0.35,
      depthWrite: false,
    }});
    const sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(size * 4, size * 4, 1);
    sphere.add(sprite);
  }});

  // Phi split marker
  const phiP = DATA[PHI_IDX];
  const phiGeo = new THREE.RingGeometry(1.5, 1.7, 32);
  const phiMat = new THREE.MeshBasicMaterial({{ color: 0xffffff, side: THREE.DoubleSide, transparent: true, opacity: 0.3 }});
  const phiRing = new THREE.Mesh(phiGeo, phiMat);
  phiRing.position.set(0, phiP.y, 0);
  phiRing.rotation.x = Math.PI / 2;
  phiRing.scale.set(5, 5, 1);
  scene.add(phiRing);

  // Complement lines
  for (let i = 0; i < DATA.length; i++) {{
    for (let j = i + 1; j < Math.min(i + 8, DATA.length); j++) {{
      const a = DATA[i], b = DATA[j];
      if ((a.cat === 'S' && b.cat === 'P') || (a.cat === 'P' && b.cat === 'S') ||
          (a.cat === 'L' && b.cat === 'I') || (a.cat === 'I' && b.cat === 'L')) {{
        const lineGeo = new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(a.x, a.y, a.z),
          new THREE.Vector3(b.x, b.y, b.z)
        ]);
        const lineMat = new THREE.LineBasicMaterial({{
          color: (a.cat === 'S' || a.cat === 'P') ? 0x664422 : 0x224466,
          transparent: true, opacity: 0.12
        }});
        scene.add(new THREE.Line(lineGeo, lineMat));
      }}
    }}
  }}

  // Grid
  const gridHelper = new THREE.GridHelper(40, 20, 0x111133, 0x111133);
  gridHelper.position.y = -1;
  scene.add(gridHelper);

  window.addEventListener('resize', onResize);
  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('click', () => {{ autoRotate = !autoRotate; }});
  
  animate();
}}

function createGlowTexture(color) {{
  const canvas = document.createElement('canvas');
  canvas.width = 64; canvas.height = 64;
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  gradient.addColorStop(0, color);
  gradient.addColorStop(0.4, color + '44');
  gradient.addColorStop(1, 'transparent');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(canvas);
  return tex;
}}

function onResize() {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}}

function onMouseMove(e) {{
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(spheres);
  const tt = document.getElementById('tooltip');
  
  if (intersects.length > 0) {{
    const d = intersects[0].object.userData;
    tt.innerHTML = `<div class="tt-cat" style="color:${{d.color}}">[${{d.cat}}] ${{d.label}}</div>
      <div style="margin-top:4px"><strong>#${{d.idx + 1}}</strong> · ${{d.branches}} Äste · ${{d.strength}}</div>
      <div style="margin-top:6px;opacity:0.8">${{d.doc}}</div>
      <div style="margin-top:4px;opacity:0.5;font-size:10px">${{d.id}}</div>`;
    tt.style.display = 'block';
    tt.style.left = e.clientX + 15 + 'px';
    tt.style.top = e.clientY + 15 + 'px';
  }} else {{
    tt.style.display = 'none';
  }}
}}

function animate() {{
  requestAnimationFrame(animate);
  if (autoRotate) {{
    const t = Date.now() * 0.0001;
    camera.position.x = 30 * Math.cos(t);
    camera.position.z = 30 * Math.sin(t);
    camera.position.y = 18 + 5 * Math.sin(t * 0.7);
    camera.lookAt(0, 15, 0);
  }}
  controls.update();
  renderer.render(scene, camera);
}}

init();
</script>
</body>
</html>"""

out_path = os.path.join(os.path.dirname(__file__), "..", "..", "media", "core_spiral_3d.html")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"3D Spiral saved: {os.path.abspath(out_path)}")
print(f"Points: {len(points)}")
print(f"Categories: L={sum(1 for p in points if p['cat']=='L')} P={sum(1 for p in points if p['cat']=='P')} I={sum(1 for p in points if p['cat']=='I')} S={sum(1 for p in points if p['cat']=='S')}")
