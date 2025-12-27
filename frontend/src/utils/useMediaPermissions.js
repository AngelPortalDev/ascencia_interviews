export const useMediaPermissions = () => {
  const checkMediaPermissions = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      stream.getTracks().forEach((track) => track.stop());
      return true;
    } catch (err) {
      console.error("Permission error:", err);
      throw new Error(
        "Camera/microphone access denied. Please enable permissions and refresh."
      );
    }
  };

  return { checkMediaPermissions };
};