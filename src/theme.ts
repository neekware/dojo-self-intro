export const theme = {
  bg: "#0B0B0C",
  bgElevated: "#141416",
  fg: "#F5F5F4",
  muted: "rgba(245, 245, 244, 0.72)",
  amber: "#F5A524",
  amberSoft: "rgba(245, 165, 36, 0.18)",
  line: "rgba(245, 245, 244, 0.12)",
  black: "#000000",
} as const;

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

/** Total film length — VO + breathing room for outro hold */
export const DURATION_SECONDS = 78;
export const DURATION_FRAMES = DURATION_SECONDS * FPS;
