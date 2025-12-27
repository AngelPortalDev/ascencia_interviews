export const initDaily = async ({
  tokenData,
  videoContainerRef,
  dailyRef,
  setCallJoined,
  setLoading,
}) => {
  const { default: DailyIframe } = await import("@daily-co/daily-js");

  const callObject = DailyIframe.createCallObject({
    videoSource: true,
    audioSource: true,
  });

  dailyRef.current = callObject;

  callObject.on("joined-meeting", async () => {
    try {
      await callObject.setInputDevicesAsync({ video: true, audio: true });

      callObject.updateSendSettings({
        video: {
          maxQuality: "low",
          encodings: {
            low: {
              maxBitrate: 1500000,
              maxFramerate: 25,
              scaleResolutionDownBy: 4,
            },
          },
        },
      });

      setCallJoined(true);
    } catch (err) {
      console.error("Joined-meeting error:", err);
    }
  });

  callObject.on("track-started", (e) => {
    if (e.participant?.local && e.track.kind === "video") {
      const video = document.createElement("video");
      video.srcObject = new MediaStream([e.track]);
      video.autoplay = true;
      video.muted = true;
      video.playsInline = true;
      video.style.width = "100%";
      video.style.height = "100%";
      video.style.objectFit = "cover";
      video.style.borderRadius = "0.75rem";

      if (videoContainerRef.current) {
        videoContainerRef.current.innerHTML = "";
        videoContainerRef.current.appendChild(video);
        setLoading(false);
      }
    }
  });

  callObject.on("error", (e) => {
    console.error("Daily error:", e);
    setLoading(false);
  });

  const timeoutId = setTimeout(() => {
    setLoading(false);
  }, 10000);

  try {
    await callObject.join({
      url: tokenData.room_url,
      token: tokenData.token,
    });
    clearTimeout(timeoutId);
  } catch (err) {
    clearTimeout(timeoutId);
    throw err;
  }
};
