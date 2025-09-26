import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

function RotatingCube() {
  const mesh = useRef<THREE.Mesh>(null!);
  useFrame((state, delta) => {
    mesh.current.rotation.x += delta * 0.5;
    mesh.current.rotation.y += delta * 0.2;
  });
  return (
    <mesh ref={mesh} position={[0, 0, 0]}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="#7a6ac8" />
    </mesh>
  );
}

function IsometricPortfolio() {
  return (
    <div style={{height: '500px', width: '100%'}}>
      <Canvas>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <RotatingCube />
        <OrbitControls />
        <PerspectiveCamera makeDefault position={[5, 5, 5]} />
      </Canvas>
    </div>
  );
}

export default IsometricPortfolio;