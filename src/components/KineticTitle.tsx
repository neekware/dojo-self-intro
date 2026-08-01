import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";

type Props = {
  title: string;
  subtitle?: string;
  align?: "center" | "left" | "bottom-left";
  delay?: number;
  accent?: boolean;
};

export const KineticTitle: React.FC<Props> = ({
  title,
  subtitle,
  align = "center",
  delay = 0,
  accent = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delay);

  const opacity = interpolate(local, [0, 0.4 * fps], [0, 1], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const y = interpolate(local, [0, 0.5 * fps], [28, 0], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const subOpacity = interpolate(local, [0.25 * fps, 0.7 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const placement =
    align === "left"
      ? {
          justifyContent: "center" as const,
          alignItems: "flex-start" as const,
          paddingLeft: 120,
          textAlign: "left" as const,
        }
      : align === "bottom-left"
        ? {
            justifyContent: "flex-end" as const,
            alignItems: "flex-start" as const,
            paddingLeft: 100,
            paddingBottom: 90,
            textAlign: "left" as const,
          }
        : {
            justifyContent: "center" as const,
            alignItems: "center" as const,
            textAlign: "center" as const,
          };

  return (
    <AbsoluteFill
      style={{
        ...placement,
        opacity,
        transform: `translateY(${y}px)`,
        pointerEvents: "none",
      }}
    >
      <div style={{ maxWidth: 1400 }}>
        {accent ? (
          <div
            style={{
              width: 56,
              height: 4,
              background: theme.amber,
              borderRadius: 999,
              marginBottom: 22,
              opacity: subOpacity,
            }}
          />
        ) : null}
        <div
          style={{
            fontFamily: "Inter, system-ui, sans-serif",
            fontWeight: 700,
            fontSize: align === "center" ? 92 : 78,
            letterSpacing: -1.6,
            lineHeight: 1.05,
            color: theme.fg,
            textShadow: "0 12px 40px rgba(0,0,0,0.45)",
          }}
        >
          {title}
        </div>
        {subtitle ? (
          <div
            style={{
              marginTop: 18,
              fontFamily: "Inter, system-ui, sans-serif",
              fontWeight: 500,
              fontSize: 34,
              lineHeight: 1.3,
              color: theme.muted,
              opacity: subOpacity,
              maxWidth: 900,
            }}
          >
            {subtitle}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
