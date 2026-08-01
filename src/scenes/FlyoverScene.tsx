import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { Video } from "@remotion/media";
import { KineticTitle } from "../components/KineticTitle";
import { theme } from "../theme";

export const FlyoverScene: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg }}>
      <Video
        src={staticFile("generated/videos/flyover-villa.mp4")}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        volume={0}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.2) 0%, transparent 40%, rgba(0,0,0,0.62) 100%)",
        }}
      />
      <KineticTitle
        title="It flies the camera."
        subtitle="Drone energy from a single photo."
        align="bottom-left"
        delay={6}
        accent
      />
    </AbsoluteFill>
  );
};
