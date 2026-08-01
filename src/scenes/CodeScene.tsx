import React from "react";
import { AbsoluteFill } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { MediaFrame } from "../components/MediaFrame";
import { KineticTitle } from "../components/KineticTitle";

export const CodeScene: React.FC = () => {
  return (
    <SceneShell dim={0.35} backgroundImage="generated/images/bg-abstract.jpg">
      <MediaFrame
        kind="video"
        src="generated/videos/code-ide-motion.mp4"
        label="CODE"
        inset={90}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.15) 0%, transparent 35%, rgba(0,0,0,0.55) 100%)",
        }}
      />
      <KineticTitle
        title="It writes the code."
        subtitle="Pair programming that never gets tired."
        align="bottom-left"
        delay={8}
        accent
      />
    </SceneShell>
  );
};
