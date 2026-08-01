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
import { Video } from "@remotion/media";
import { theme } from "../theme";
import { KineticTitle } from "../components/KineticTitle";

export const TryOnScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const stripOpacity = interpolate(frame, [0.2 * fps, 0.6 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const stripY = interpolate(frame, [0.2 * fps, 0.7 * fps], [24, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg }}>
      <Video
        src={staticFile("generated/videos/tryon-fashion-walk.mp4")}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        volume={0}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(90deg, rgba(0,0,0,0.55) 0%, transparent 50%, rgba(0,0,0,0.35) 100%)",
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: "flex-start",
          alignItems: "flex-end",
          padding: 70,
          opacity: stripOpacity,
          transform: `translateY(${stripY}px)`,
        }}
      >
        <div style={{ display: "flex", gap: 14 }}>
          {[
            { src: "generated/images/tryon-person.jpg", label: "Person" },
            { src: "generated/images/tryon-garment.jpg", label: "Garment" },
            { src: "generated/images/tryon-result.png", label: "Try-on" },
          ].map((item) => (
            <div
              key={item.label}
              style={{
                width: 168,
                height: 110,
                borderRadius: 16,
                overflow: "hidden",
                border: `1px solid ${theme.line}`,
                boxShadow: "0 16px 40px rgba(0,0,0,0.4)",
                position: "relative",
              }}
            >
              <Img
                src={staticFile(item.src)}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
              <div
                style={{
                  position: "absolute",
                  left: 10,
                  bottom: 8,
                  color: theme.fg,
                  fontFamily: "Inter, system-ui, sans-serif",
                  fontSize: 14,
                  fontWeight: 700,
                  textShadow: "0 4px 12px rgba(0,0,0,0.7)",
                }}
              >
                {item.label}
              </div>
            </div>
          ))}
        </div>
      </AbsoluteFill>
      <KineticTitle
        title="It fits the look."
        subtitle="Virtual try-on that feels real."
        align="bottom-left"
        delay={8}
        accent
      />
    </AbsoluteFill>
  );
};
