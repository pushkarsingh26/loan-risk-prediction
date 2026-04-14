import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const BAR_DATA = [
  { label: "Full-time", value: 0.06, color: 0x2dd4bf },
  { label: "Self-Employed", value: 0.14, color: 0xf59e0b },
  { label: "Part-Time", value: 0.11, color: 0x3b82f6 },
  { label: "Unemployed", value: 0.28, color: 0xef4444 },
];

const BarChart3D = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const w = container.clientWidth;
    const h = container.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
    camera.position.set(5, 4, 7);
    camera.lookAt(0, 1, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableZoom = false;
    controls.enablePan = false;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.2;
    controls.maxPolarAngle = Math.PI / 2.2;
    controls.minPolarAngle = Math.PI / 6;

    // Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambient);
    const dir = new THREE.DirectionalLight(0xffffff, 0.8);
    dir.position.set(5, 8, 5);
    scene.add(dir);

    // Floor grid
    const gridHelper = new THREE.GridHelper(10, 10, 0x1e1b4b, 0x1e1b4b);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    // Bars
    const barWidth = 1;
    const gap = 0.8;
    const totalWidth = BAR_DATA.length * barWidth + (BAR_DATA.length - 1) * gap;
    const startX = -totalWidth / 2 + barWidth / 2;

    interface BarAnim {
      mesh: THREE.Mesh;
      targetHeight: number;
    }

    const bars: BarAnim[] = [];

    BAR_DATA.forEach((d, i) => {
      const maxBarHeight = 5;
      const targetH = d.value * maxBarHeight / 0.3; // normalize so 0.3 = maxBarHeight
      const geo = new THREE.BoxGeometry(barWidth, 0.01, barWidth);
      const mat = new THREE.MeshStandardMaterial({
        color: d.color,
        transparent: true,
        opacity: 0.85,
        roughness: 0.3,
        metalness: 0.2,
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(startX + i * (barWidth + gap), 0, 0);
      scene.add(mesh);
      bars.push({ mesh, targetHeight: targetH });

      // Edge glow
      const edgeGeo = new THREE.BoxGeometry(barWidth + 0.04, 0.01, barWidth + 0.04);
      const edgeMat = new THREE.MeshBasicMaterial({
        color: d.color,
        transparent: true,
        opacity: 0.15,
        wireframe: true,
      });
      const edge = new THREE.Mesh(edgeGeo, edgeMat);
      mesh.add(edge);
    });

    const clock = new THREE.Clock();
    let animId: number;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();
      controls.update();

      // Animate bar growth over first 1.5s
      const growProgress = Math.min(t / 1.5, 1);
      const eased = 1 - Math.pow(1 - growProgress, 3);

      bars.forEach((b) => {
        const h = Math.max(0.01, b.targetHeight * eased);
        b.mesh.scale.y = h / 0.01;
        b.mesh.position.y = h / 2;
      });

      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!container) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      controls.dispose();
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
      <h3 className="text-lg font-semibold text-foreground mb-2">Default Rate by Employment Type</h3>
      <div ref={containerRef} className="w-full h-[340px]" />
      <div className="flex justify-center gap-5 mt-3 flex-wrap">
        {BAR_DATA.map((d) => (
          <div key={d.label} className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: `#${d.color.toString(16).padStart(6, "0")}` }} />
            {d.label} ({(d.value * 100).toFixed(0)}%)
          </div>
        ))}
      </div>
    </div>
  );
};

export default BarChart3D;
