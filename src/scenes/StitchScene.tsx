import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Video } from "@remotion/media";
import { SceneShell } from "../components/SceneShell";
import { KineticTitle } from "../components/KineticTitle";
import { CapabilityChip } from "../components/CapabilityChip";
import { theme } from "../theme";

const clips = [
  "generated/videos/code-ide-motion.mp4",
  "generated/videos/promo-headphones.mp4",
  "generated/videos/flyover-villa.mp4",
  "generated/videos/tryon-fashion-walk.mp4",
  "generated/videos/character-alive.mp4",
];

export const StitchScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <SceneShell dim={0.55}>
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: "80px 80px 200px",
        }}
      >
        <div
          style={{
            width: "100%",
            display: "flex",
            gap: 16,
            alignItems: "center",
          }}
        >
          {clips.map((src, i) => {
            const local = Math.max(0, frame - i * 6);
            const opacity = interpolate(local, [0, 0.35 * fps], [0, 1], {
              extrapolateRight: "clamp",
            });
            const x = interpolate(local, [0, 0.45 * fps], [40, 0], {
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            });
            return (
              <div
                key={src}
                style={{
                  flex: 1,
                  height: 280,
                  borderRadius: 18,
                  overflow: "hidden",
                  opacity,
                  transform: `translateX(${x}px)`,
                  border: `1px solid ${theme.line}`,
                  boxShadow: "0 20px 50px rgba(0,0,0,0.45)",
                  position: "relative",
                }}
              >
                <Video
                  src={staticFile(src)}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  volume={0}
                />
                <div
                  style={{
                    position: "absolute",
                    left: 12,
                    top: 12,
                    width: 10,
                    height: 10,
                    borderRadius: 999,
                    background: theme.amber,
                    boxShadow: "0 0 12px rgba(245,165,36,0.8)",
                  }}
                />
              </div>
            );
          })}
        </div>
        <div
          style={{
            marginTop: 28,
            width: "92%",
            height: 8,
            borderRadius: 999,
            background: "rgba(255,255,255,0.08)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${interpolate(frame, [0, 2.2 * fps], [8, 100], {
                extrapolateRight: "clamp",
                easing: Easing.bezier(0.16, 1, 0.3, 1),
              })}%`,
              height: "100%",
              background: `linear-gradient(90deg, ${theme.amber}, #FFE0A3)`,
            }}
          />
        </div>
      </AbsoluteFill>
      <KineticTitle
        title="Then it stitches the film."
        subtitle="Image, video, and audio — one finished cut."
        align="bottom-left"
        delay={8}
        accent
      />
      <CapabilityChip
        items={["Code", "Image", "Video", "Edit", "Audio", "Flyover", "Try-on"]}
        delay={18}
      />
    </SceneShell>
  );
};
