import React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame, interpolate, useVideoConfig, Easing } from "remotion";
import { Video } from "@remotion/media";
import { SceneShell } from "../components/SceneShell";
import { KineticTitle } from "../components/KineticTitle";
import { theme } from "../theme";

export const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cardOpacity = interpolate(frame, [0.3 * fps, 0.8 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return (
    <SceneShell dim={0.55}>
      <AbsoluteFill style={{ opacity: 0.35 }}>
        <Video
          src={staticFile("generated/videos/character-alive.mp4")}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
          volume={0}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(90deg, rgba(11,11,12,0.88) 0%, rgba(11,11,12,0.55) 48%, rgba(11,11,12,0.25) 100%)",
        }}
      />
      <KineticTitle
        title="Not a chatbot."
        subtitle="A creative studio that actually ships."
        align="left"
        accent
      />
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "flex-end",
          padding: 90,
          opacity: cardOpacity,
        }}
      >
        <div
          style={{
            padding: "18px 22px",
            borderRadius: 18,
            background: "rgba(20,20,22,0.78)",
            border: `1px solid ${theme.line}`,
            color: theme.muted,
            fontFamily: "Inter, system-ui, sans-serif",
            fontSize: 22,
            fontWeight: 600,
            backdropFilter: "blur(12px)",
          }}
        >
          Code · Image · Video · Audio · Stitch
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
