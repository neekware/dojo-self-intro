(() => {
  const video = document.querySelector(".hero-media");
  const soundButton = document.querySelector(".sound");
  const soundLabel = document.querySelector(".sound-label");
  const watchButton = document.querySelector(".watch");
  const progress = document.querySelector(".timeline-fill");

  if (!video) return;

  const setSound = (enabled) => {
    video.muted = !enabled;
    soundButton?.setAttribute("aria-pressed", String(enabled));
    if (soundLabel) soundLabel.textContent = enabled ? "Sound on" : "Sound off";
  };

  const play = () => video.play().catch(() => {});

  soundButton?.addEventListener("click", () => {
    setSound(video.muted);
    play();
  });

  watchButton?.addEventListener("click", () => {
    video.currentTime = 0;
    setSound(true);
    play();
  });

  video.addEventListener("timeupdate", () => {
    if (!progress || !Number.isFinite(video.duration) || video.duration === 0) return;
    progress.style.width = `${(video.currentTime / video.duration) * 100}%`;
  });

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    video.pause();
    video.removeAttribute("autoplay");
  }
})();
