import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { loadFont } from "@remotion/google-fonts/Inter";
import { ColdOpen } from "./scenes/ColdOpen";
import { Hook } from "./scenes/Hook";
import { CodeScene } from "./scenes/CodeScene";
import { ImageScene } from "./scenes/ImageScene";
import { VideoScene } from "./scenes/VideoScene";
import { FlyoverScene } from "./scenes/FlyoverScene";
import { TryOnScene } from "./scenes/TryOnScene";
import { AudioScene } from "./scenes/AudioScene";
import { StitchScene } from "./scenes/StitchScene";
import { Outro } from "./scenes/Outro";
import { theme } from "./theme";

loadFont("normal", {
  weights: ["500", "600", "700", "800"],
  subsets: ["latin"],
});

const t = (frames: number) =>
  linearTiming({ durationInFrames: frames });

export const PowerShowcase: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg }}>
      <Audio src={staticFile("generated/audio/narrator-v2.mp3")} volume={1} />
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={100}>
          <ColdOpen />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={t(12)} />

        <TransitionSeries.Sequence durationInFrames={150}>
          <Hook />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={t(12)} />

        <TransitionSeries.Sequence durationInFrames={200}>
          <CodeScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={t(12)} />

        <TransitionSeries.Sequence durationInFrames={200}>
          <ImageScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={t(12)} />

        <TransitionSeries.Sequence durationInFrames={200}>
          <VideoScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={t(12)} />

        <TransitionSeries.Sequence durationInFrames={200}>
          <FlyoverScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={t(12)} />

        <TransitionSeries.Sequence durationInFrames={200}>
          <TryOnScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={t(12)} />

        <TransitionSeries.Sequence durationInFrames={160}>
          <AudioScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={t(12)} />

        <TransitionSeries.Sequence durationInFrames={200}>
          <StitchScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={t(14)} />

        <TransitionSeries.Sequence durationInFrames={240}>
          <Outro />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};

/**
 * Sequence durations sum to 1850.
 * 9 fade transitions remove 12+12+12+12+12+12+12+12+14 = 110 frames.
 * Final composition length = 1740 frames @ 30fps ≈ 58.0s
 */
export const POWER_SHOWCASE_FRAMES = 1740;
export const POWER_SHOWCASE_FPS = 30;
export const POWER_SHOWCASE_WIDTH = 1920;
export const POWER_SHOWCASE_HEIGHT = 1080;
