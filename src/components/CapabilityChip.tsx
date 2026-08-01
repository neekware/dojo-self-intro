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
  items: string[];
  delay?: number;
};

export const CapabilityChip: React.FC<Props> = ({ items, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 70,
        pointerEvents: "none",
      }}
    >
      <div style={{ display: "flex", gap: 14, flexWrap: "wrap", justifyContent: "center", maxWidth: 1500 }}>
        {items.map((item, i) => {
          const local = Math.max(0, frame - delay - i * 4);
          const opacity = interpolate(local, [0, 0.35 * fps], [0, 1], {
            extrapolateRight: "clamp",
          });
          const y = interpolate(local, [0, 0.4 * fps], [18, 0], {
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          });
          return (
            <div
              key={item}
              style={{
                opacity,
                transform: `translateY(${y}px)`,
                padding: "12px 18px",
                borderRadius: 999,
                border: `1px solid ${theme.line}`,
                background: "rgba(20,20,22,0.72)",
                color: theme.fg,
                fontFamily: "Inter, system-ui, sans-serif",
                fontSize: 22,
                fontWeight: 600,
                backdropFilter: "blur(12px)",
              }}
            >
              <span style={{ color: theme.amber, marginRight: 8 }}>●</span>
              {item}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
