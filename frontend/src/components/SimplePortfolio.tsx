import React, { useRef, useState } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { Line } from '@react-three/drei';
import { buffer, geometry, three, vector3 } from 'maath';

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

function AnimatedDea() {
  const mesh = useRef<any>(null);

  useFrame((state, delta) => {
    if (mesh.current) {
      mesh.current.rotation.y += delta * 0.5;
    }
  });

  return (
    <mesh ref={mesh} position={[-1.5, 0.5, 0]}>
      <icosahedronGeometry args={[0.5, 0]} />
      <meshStandardMaterial color="#4a14e0" metalness={0.5} roughness={0.2} />
    </mesh>
  );
}

function AnimatedAqvi() {
  const mesh = useRef<any>(null);

  useFrame((state, delta) => {
    if (mesh.current) {
      mesh.current.rotation.y += delta * 0.5;
    }
  });

  return (
    <mesh ref={mesh} position={[1.5, 0.5, 0]}>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial 
        color="#7a6ac8" 
        metalness={0.8} 
        roughness={0.2} 
        emissive="#4a14e0"
        emissiveIntensity={0.2}
      />
    </mesh>
  );
}

function RotatingCube() {
  const mesh = useRef<any>(null);
  
  useFrame((state, delta) => {
    if (mesh.current) {
      mesh.current.rotation.x += delta * 0.5;
      mesh.current.rotation.y += delta * 0.2;
    }
  });
  
  return (
    <mesh ref={mesh} position={[0, 0, 0]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#7a6ac8" />
    </mesh>
  );
}

function SimplePortfolio() {
  return (
    <div style={{height: '500px', width: '100%'}}>
      <Canvas>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <RotatingCube />
        <ConnectionLine />
        <AnimatedDea />
        <AnimatedAqvi />
        <mesh position={[-1.5, 0.5, 0]}>
          <icosahedronGeometry args={[0.5, 0]} />
          <meshStandardMaterial color="#4a14e0" metalness={0.5} roughness={0.2} />
        </mesh>
        <mesh position={[1.5, 0.5, 0]}>
          <sphereGeometry args={[0.5, 32, 32]} />
          <meshStandardMaterial 
            color="#7a6ac8" 
            metalness={0.8} 
            roughness={0.2} 
            emissive="#4a14e0"
            emissiveIntensity={0.2}
          />
        </mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
          <circleGeometry args={[2, 32]} />
          <meshStandardMaterial color="#333" roughness={0.7} metalness={0.2} />
        </mesh>

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
        <OrbitControls />
      </Canvas>
    </div>
  );
}

export default SimplePortfolio;