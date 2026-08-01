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

export const ColdOpen: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const logoOpacity = interpolate(frame, [0, 0.5 * fps], [0, 1], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const logoScale = interpolate(frame, [0, 0.7 * fps], [0.86, 1], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const wordOpacity = interpolate(frame, [0.45 * fps, 0.9 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const glow = interpolate(
    frame,
    [0, durationInFrames * 0.5, durationInFrames],
    [0.15, 0.35, 0.2],
    { extrapolateRight: "clamp" },
  );
  const exit = interpolate(
    frame,
    [durationInFrames - 12, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg, opacity: exit }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 45%, rgba(245,165,36,${glow}), transparent 42%)`,
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          gap: 28,
        }}
      >
        <div
          style={{
            opacity: logoOpacity,
            transform: `scale(${logoScale})`,
            width: 220,
            height: 220,
            borderRadius: 48,
            overflow: "hidden",
            boxShadow: "0 30px 90px rgba(245,165,36,0.25)",
          }}
        >
          <Img
            src={staticFile("brand/dojo-logo.png")}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </div>
        <div
          style={{
            opacity: wordOpacity,
            fontFamily: "Inter, system-ui, sans-serif",
            fontWeight: 800,
            fontSize: 88,
            letterSpacing: 8,
            color: theme.fg,
          }}
        >
          DOJO
        </div>
        <div
          style={{
            opacity: wordOpacity,
            fontFamily: "Inter, system-ui, sans-serif",
            fontWeight: 500,
            fontSize: 28,
            color: theme.muted,
            letterSpacing: 4,
            textTransform: "uppercase",
          }}
        >
          Workspace
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
