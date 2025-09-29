import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Line } from '@react-three/drei';
import { useSpring, a } from '@react-spring/three';
import * as THREE from 'three';
import { buffer, geometry, three, vector3 } from 'maath';

// Компонент для 3D-представления ДЕА
function DeaModel({ position }: { position: [number, number, number] }) {
  const [hovered, setHovered] = useState(false);

  const props = useSpring({
    scale: hovered ? [1.2, 1.2, 1.2] : [1, 1, 1],
    config: { mass: 5, tension: 500, friction: 80 }
  });

  const group = useRef<THREE.Group>(null!);

  useFrame((state, delta) => {
    if (group.current) {
      group.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <a.group 
      ref={group} 
      position={position}
      scale={props.scale as any}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <mesh>
        <icosahedronGeometry args={[1, 0]} />
        <meshStandardMaterial color="#4a14e0" metalness={0.5} roughness={0.2} />
      </mesh>
    </a.group>
  );
}

// Компонент для 3D-представления Советницы АКВИ
function AqviSphere({ position }: { position: [number, number, number] }) {
  const group = useRef<THREE.Group>(null!);
  const [hovered, setHovered] = useState(false);
  
  useFrame((state, delta) => {
    if (group.current) {
      group.current.rotation.y += delta * 0.2;
    }
  });
  
  const props = useSpring({
    scale: hovered ? [1.2, 1.2, 1.2] : [1, 1, 1],
    config: { mass: 5, tension: 500, friction: 80 }
  });
  
  return (
    <a.group 
      ref={group} 
      position={position}
      scale={props.scale as any}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <mesh>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial 
          color="#7a6ac8" 
          metalness={0.8} 
          roughness={0.2} 
          emissive="#4a14e0"
          emissiveIntensity={0.2}
        />
      </mesh>
    </a.group>
  );
}

function ConnectionLine() {
  const points = [
    new THREE.Vector3(-3, 0, 0),
    new THREE.Vector3(3, 0, 0)
  ];
  const [pulsePosition, setPulsePosition] = useState(0);

  useFrame(() => {
    setPulsePosition((prev) => (prev + 0.01) % 1);
  });

  const pulseX = -3 + 6 * pulsePosition;

  return (
    <>
      <Line points={points} color="#4a14e0" lineWidth={2} transparent opacity={0.7} />
      <mesh position={[pulseX, 0, 0]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshBasicMaterial color="#ff6b6b" transparent opacity={0.8} />
      </mesh>
    </>
  );
}

// Основной компонент изометрического портфолио
function IsometricPortfolio() {
  return (
    <div style={{height: '500px', width: '100%', position: 'relative'}}>
      <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />
        <pointLight position={[-10, -10, -10]} color="#7a6ac8" />
        <DeaModel position={[-3, 0, 0]} />
        <AqviSphere position={[3, 0, 0]} />
        <ConnectionLine />
        
        {/* Платформа под моделями */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.5, 0]}>
          <circleGeometry args={[5, 64]} />
          <meshStandardMaterial color="#333" roughness={0.7} metalness={0.2} />
        </mesh>
        
        {/* Проекты вокруг */}
        {[...Array(5)].map((_, i) => {
          const angle = (i / 5) * Math.PI * 2;
          const x = Math.cos(angle) * 7;
          const z = Math.sin(angle) * 7;
          
          return (
            <mesh key={i} position={[x, 0, z]}>
              <boxGeometry args={[1.5, 1.5, 1.5]} />
              <meshStandardMaterial color="#7a6ac8" metalness={0.8} roughness={0.2} />
            </mesh>
          );
        })}
        <OrbitControls autoRotate autoRotateSpeed={0.5} />
      </Canvas>
      
      <div style={{
        position: 'absolute',
        bottom: '1rem',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        color: 'white',
        padding: '0.5rem 1rem',
        borderRadius: '20px',
        fontSize: '0.9rem'
      }}>
        Наведите курсор на объекты для взаимодействия
      </div>
    </div>
  );
}

export default IsometricPortfolio;