import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { theme } from "../theme";

type Props = {
  children: React.ReactNode;
  dim?: number;
  showGrain?: boolean;
  backgroundImage?: string;
};

export const SceneShell: React.FC<Props> = ({
  children,
  dim = 0.45,
  backgroundImage = "generated/images/bg-abstract.jpg",
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg, overflow: "hidden" }}>
      <AbsoluteFill>
        <Img
          src={staticFile(backgroundImage)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: "scale(1.08)",
            filter: "saturate(0.9) brightness(0.55)",
          }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, rgba(0,0,0,${dim * 0.55}) 0%, rgba(11,11,12,${dim}) 45%, rgba(0,0,0,${Math.min(0.85, dim + 0.2)}) 100%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at 50% 20%, rgba(245,165,36,0.12), transparent 55%)",
        }}
      />
      {children}
    </AbsoluteFill>
  );
};
