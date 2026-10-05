import React, { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { Canvas, useFrame } from "@react-three/fiber";
import { EffectComposer, Bloom } from "@react-three/postprocessing";

function SwitchOrb({ state }) {
  const pointsRef = useRef(null);
  const time = useRef(0);
  const exitProgress = useRef(0);

  const geometry = useMemo(() => {
    const count = 6000;
    const positions = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;

      const radius = 2.2 + Math.random() * 0.7;

      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      positions[i3] =
        radius * Math.sin(phi) * Math.cos(theta);

      positions[i3 + 1] =
        radius * Math.sin(phi) * Math.sin(theta);

      positions[i3 + 2] =
        radius * Math.cos(phi);
    }

    const geo = new THREE.BufferGeometry();

    geo.setAttribute(
      "position",
      new THREE.BufferAttribute(positions, 3)
    );

    return geo;
  }, []);

  const originalPositions = useMemo(() => {
    return geometry.attributes.position.array.slice();
  }, [geometry]);

  useFrame((_, delta) => {
    if (!pointsRef.current) {
      return;
    }

    time.current += delta;

    const positionAttribute =
      geometry.attributes.position;

    const positions =
      positionAttribute.array;

    const targetScale =
      state === "sleeping"
        ? 0.72
        : 1;

    pointsRef.current.scale.lerp(
      new THREE.Vector3(
        targetScale,
        targetScale,
        targetScale
      ),
      delta * 5
    );

    if (
      state !== "speaking" &&
      state !== "exiting"
    ) {
      pointsRef.current.rotation.y +=
        delta * 0.08;

      pointsRef.current.rotation.x +=
        delta * 0.015;
    }

    if (state === "exiting") {
      exitProgress.current += delta;

      const progress = Math.min(
        exitProgress.current / 2.8,
        1
      );

      const eased =
        progress *
        progress *
        progress;

      for (
        let i = 0;
        i < positions.length;
        i += 3
      ) {
        const x = originalPositions[i];
        const y = originalPositions[i + 1];
        const z = originalPositions[i + 2];

        const length =
          Math.sqrt(
            x * x +
            y * y +
            z * z
          );

        const nx = x / length;
        const ny = y / length;
        const nz = z / length;

        const variation =
          0.75 +
          Math.sin(i * 0.17) * 0.25;

        const spread =
          eased *
          14 *
          variation;

        positions[i] =
          x + nx * spread;

        positions[i + 1] =
          y + ny * spread;

        positions[i + 2] =
          z + nz * spread;
      }

      positionAttribute.needsUpdate = true;

      const material =
        pointsRef.current.material;

      if (material) {
        material.opacity =
          0.9 *
          (1 - progress);
      }

      return;
    }

    for (
      let i = 0;
      i < positions.length;
      i += 3
    ) {
      const x = originalPositions[i];
      const y = originalPositions[i + 1];
      const z = originalPositions[i + 2];

      const radius =
        Math.sqrt(
          x * x +
          y * y +
          z * z
        );

      const nx = x / radius;
      const ny = y / radius;
      const nz = z / radius;

      let wave = 0;

      if (state === "speaking") {
        const longitude =
          Math.atan2(z, x);

        const latitude =
          Math.asin(ny);

        const movingWave =
          Math.sin(
            longitude * 7 +
            latitude * 3 -
            time.current * 5
          );

        const secondWave =
          Math.sin(
            latitude * 9 -
            time.current * 4
          );

        wave =
          movingWave * 0.24 +
          secondWave * 0.09;

        wave *= 1.35;
      }

      positions[i] =
        x + nx * wave;

      positions[i + 1] =
        y + ny * wave;

      positions[i + 2] =
        z + nz * wave;
    }

    positionAttribute.needsUpdate = true;

    const material =
      pointsRef.current.material;

    if (material) {
      const targetOpacity =
        state === "sleeping"
          ? 0.35
          : 0.9;

      material.opacity +=
        (
          targetOpacity -
          material.opacity
        ) *
        delta *
        5;
    }
  });

  return (
    <points
      ref={pointsRef}
      geometry={geometry}
    >
      <pointsMaterial
        size={0.025}
        sizeAttenuation
        transparent
        opacity={0.9}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

export default function App() {
  const [state, setState] =
    useState("idle");

  useEffect(() => {
    let alive = true;

    const updateState = async () => {
      try {
        const response =
          await fetch(
            "http://127.0.0.1:5000/state",
            {
              cache: "no-store"
            }
          );

        const data =
          await response.json();

        if (
          alive &&
          data.state
        ) {
          setState(data.state);
        }
      } catch {
        // Backend is not available yet.
      }
    };

    updateState();

    const interval =
      setInterval(
        updateState,
        80
      );

    return () => {
      alive = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: "transparent",
        overflow: "hidden",
        WebkitAppRegion: "drag"
      }}
    >
      <Canvas
        camera={{
          position: [0, 0, 7],
          fov: 60
        }}
        gl={{
          antialias: true,
          alpha: true,
          preserveDrawingBuffer: false
        }}
        style={{
          width: "100%",
          height: "100%",
          background: "transparent"
        }}
      >
        <SwitchOrb state={state} />

        <EffectComposer>
          <Bloom
            intensity={
              state === "sleeping"
                ? 0.4
                : state === "speaking"
                ? 1.2
                : 1.0
            }
            luminanceThreshold={0.1}
            luminanceSmoothing={0.9}
          />
        </EffectComposer>
      </Canvas>
    </div>
  );
}