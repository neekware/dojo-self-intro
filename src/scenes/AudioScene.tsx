import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from "remotion";
import { Video } from "@remotion/media";
import { SceneShell } from "../components/SceneShell";
import { KineticTitle } from "../components/KineticTitle";
import { theme } from "../theme";

export const AudioScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bars = Array.from({ length: 42 }, (_, i) => i);

  return (
    <SceneShell dim={0.6}>
      <AbsoluteFill style={{ opacity: 0.28 }}>
        <Video
          src={staticFile("generated/videos/character-alive.mp4")}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
          volume={0}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          paddingBottom: 40,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            gap: 8,
            height: 180,
            marginBottom: 40,
          }}
        >
          {bars.map((i) => {
            const phase = Math.sin(frame * 0.22 + i * 0.45);
            const h = 28 + Math.abs(phase) * (70 + (i % 5) * 10);
            const opacity = interpolate(frame, [0, 0.4 * fps], [0, 1], {
              extrapolateRight: "clamp",
            });
            return (
              <div
                key={i}
                style={{
                  width: 10,
                  height: h,
                  borderRadius: 999,
                  opacity,
                  background:
                    i % 3 === 0
                      ? theme.amber
                      : "linear-gradient(180deg, #F5A524, #F5F5F4)",
                  transform: `scaleY(${interpolate(
                    frame,
                    [0, 0.5 * fps],
                    [0.2, 1],
                    {
                      extrapolateRight: "clamp",
                      easing: Easing.bezier(0.16, 1, 0.3, 1),
                    },
                  )})`,
                }}
              />
            );
          })}
        </div>
      </AbsoluteFill>
      <KineticTitle
        title="It speaks."
        subtitle="Natural voice — and it hears you back."
        align="bottom-left"
        delay={6}
        accent
      />
    </SceneShell>
  );
};
