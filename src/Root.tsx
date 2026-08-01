import React from "react";
import { Composition } from "remotion";
import "./index.css";
import {
  PowerShowcase,
  POWER_SHOWCASE_FRAMES,
  POWER_SHOWCASE_FPS,
  POWER_SHOWCASE_HEIGHT,
  POWER_SHOWCASE_WIDTH,
} from "./PowerShowcase";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PowerShowcase"
        component={PowerShowcase}
        durationInFrames={POWER_SHOWCASE_FRAMES}
        fps={POWER_SHOWCASE_FPS}
        width={POWER_SHOWCASE_WIDTH}
        height={POWER_SHOWCASE_HEIGHT}
      />
    </>
  );
};
