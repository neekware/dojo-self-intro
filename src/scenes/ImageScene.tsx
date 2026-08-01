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
import { SceneShell } from "../components/SceneShell";
import { KineticTitle } from "../components/KineticTitle";
import { theme } from "../theme";

const tiles = [
  { src: "generated/images/product-headphones.jpg", label: "Product" },
  { src: "generated/images/arch-villa.jpg", label: "Architecture" },
  { src: "generated/images/character-portrait.jpg", label: "Portrait" },
  { src: "generated/images/tryon-result.png", label: "Fashion" },
];

export const ImageScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <SceneShell dim={0.5}>
      <AbsoluteFill
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gridTemplateRows: "1fr 1fr",
          gap: 22,
          padding: "90px 120px 180px 120px",
        }}
      >
        {tiles.map((tile, i) => {
          const local = Math.max(0, frame - i * 5);
          const opacity = interpolate(local, [0, 0.4 * fps], [0, 1], {
            extrapolateRight: "clamp",
          });
          const y = interpolate(local, [0, 0.45 * fps], [30, 0], {
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          });
          return (
            <div
              key={tile.src}
              style={{
                opacity,
                transform: `translateY(${y}px)`,
                borderRadius: 22,
                overflow: "hidden",
                position: "relative",
                boxShadow: "0 24px 70px rgba(0,0,0,0.45)",
                border: `1px solid ${theme.line}`,
              }}
            >
              <Img
                src={staticFile(tile.src)}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
              <div
                style={{
                  position: "absolute",
                  left: 18,
                  bottom: 16,
                  color: theme.fg,
                  fontFamily: "Inter, system-ui, sans-serif",
                  fontWeight: 700,
                  fontSize: 20,
                  textShadow: "0 6px 18px rgba(0,0,0,0.6)",
                }}
              >
                {tile.label}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
      <KineticTitle
        title="It designs the image."
        subtitle="Hero shots ready for launch."
        align="bottom-left"
        delay={10}
        accent
      />
    </SceneShell>
  );
};
