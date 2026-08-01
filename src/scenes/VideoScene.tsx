import React from "react";
import { AbsoluteFill } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { MediaFrame } from "../components/MediaFrame";
import { KineticTitle } from "../components/KineticTitle";

export const VideoScene: React.FC = () => {
  return (
    <SceneShell dim={0.3}>
      <MediaFrame
        kind="video"
        src="generated/videos/promo-headphones.mp4"
        label="VIDEO · PROMO"
        inset={80}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.1) 0%, transparent 40%, rgba(0,0,0,0.6) 100%)",
        }}
      />
      <KineticTitle
        title="Stills become motion."
        subtitle="Promos that look expensive."
        align="bottom-left"
        delay={8}
        accent
      />
    </SceneShell>
  );
};
