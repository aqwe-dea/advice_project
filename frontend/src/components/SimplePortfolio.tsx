import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Line } from '@react-three/drei';
import * as THREE from 'three';

function ConnectionLine() {
  const pointsRef = useRef([[-3, 0, 0], [3, 0, 0]]);
  const lineRef = useRef<any>(null);
  
  useFrame((state) => {
    if (lineRef.current) {
      const time = state.clock.getElapsedTime();
      const amplitude = 0.1;
      
      // Анимация по оси Z
      pointsRef.current[0][2] = Math.sin(time * 2) * amplitude;
      pointsRef.current[1][2] = Math.sin(time * 2) * amplitude;
      
      // Обновляем геометрию
      lineRef.current.geometry.setFromPoints(
        pointsRef.current.map(p => new THREE.Vector3(...p))
      );
    }
  });
  
  return (
    <Line
      ref={lineRef}
      points={pointsRef.current}
      color="#4a14e0"
      lineWidth={2}
    />
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
        <OrbitControls />
      </Canvas>
    </div>
  );
}

export default SimplePortfolio;