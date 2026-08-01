import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Video } from "@remotion/media";
import { staticFile } from "remotion";
import { theme } from "../theme";

type Props = {
  src: string;
  kind: "image" | "video";
  label?: string;
  inset?: number;
  delay?: number;
  volume?: number;
};

export const MediaFrame: React.FC<Props> = ({
  src,
  kind,
  label,
  inset = 110,
  delay = 0,
  volume = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delay);

  const opacity = interpolate(local, [0, 0.45 * fps], [0, 1], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const scale = interpolate(local, [0, 0.7 * fps], [1.06, 1], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const y = interpolate(local, [0, 0.6 * fps], [24, 0], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: inset,
        opacity,
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          borderRadius: 28,
          overflow: "hidden",
          boxShadow:
            "0 40px 120px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.08)",
          transform: `translateY(${y}px) scale(${scale})`,
          background: theme.bgElevated,
          position: "relative",
        }}
      >
        {kind === "video" ? (
          <Video
            src={staticFile(src)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            volume={volume}
          />
        ) : (
          <Img
            src={staticFile(src)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        )}
        <div
          style={{
            position: "absolute",
            inset: 0,
            boxShadow: "inset 0 0 80px rgba(0,0,0,0.25)",
            pointerEvents: "none",
          }}
        />
        {label ? (
          <div
            style={{
              position: "absolute",
              left: 28,
              bottom: 24,
              padding: "10px 16px",
              borderRadius: 999,
              background: "rgba(0,0,0,0.55)",
              border: `1px solid ${theme.line}`,
              color: theme.fg,
              fontFamily: "Inter, system-ui, sans-serif",
              fontSize: 20,
              fontWeight: 600,
              letterSpacing: 0.2,
              backdropFilter: "blur(10px)",
            }}
          >
            {label}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
