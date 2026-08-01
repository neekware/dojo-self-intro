import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";

export const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 0.5 * fps], [0, 1], {
    extrapolateRight: "clamp",
  });
  const y = interpolate(frame, [0, 0.6 * fps], [24, 0], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const ctaOpacity = interpolate(frame, [0.7 * fps, 1.2 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg }}>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 50% 40%, rgba(245,165,36,0.18), transparent 42%)",
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          opacity,
          transform: `translateY(${y}px)`,
          gap: 28,
        }}
      >
        <div
          style={{
            width: 120,
            height: 120,
            borderRadius: 32,
            overflow: "hidden",
            boxShadow: "0 20px 60px rgba(245,165,36,0.28)",
          }}
        >
          <Img
            src={staticFile("brand/dojo-logo.png")}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </div>
        <div
          style={{
            fontFamily: "Inter, system-ui, sans-serif",
            fontWeight: 800,
            fontSize: 72,
            color: theme.fg,
            textAlign: "center",
            lineHeight: 1.1,
            letterSpacing: -1.2,
          }}
        >
          Anyone can code.
          <br />
          Anyone can create.
        </div>
        <div
          style={{
            opacity: ctaOpacity,
            marginTop: 8,
            fontFamily: "Inter, system-ui, sans-serif",
            fontWeight: 600,
            fontSize: 34,
            color: theme.amber,
            letterSpacing: 0.4,
          }}
        >
          dojoworkspace.io
        </div>
        <div
          style={{
            opacity: ctaOpacity,
            fontFamily: "Inter, system-ui, sans-serif",
            fontWeight: 500,
            fontSize: 24,
            color: theme.muted,
          }}
        >
          Dojo Workspace
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
