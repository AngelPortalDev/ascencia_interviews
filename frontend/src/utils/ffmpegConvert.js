import { FFmpeg } from "@ffmpeg/ffmpeg";
import { fetchFile } from "@ffmpeg/util";

let ffmpeg = null;

export const convertWebMtoMP4 = async (webmBlob) => {
  if (!ffmpeg) {
    ffmpeg = new FFmpeg();
    await ffmpeg.load();
  }

  // Input file
  ffmpeg.writeFile("input.webm", await fetchFile(webmBlob));

  // Convert WebM -> MP4 (H264 + AAC)
  await ffmpeg.exec([
    "-i", "input.webm",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-c:a", "aac",
    "-movflags", "faststart",
    "output.mp4"
  ]);

  const data = await ffmpeg.readFile("output.mp4");

  return new Blob([data.buffer], { type: "video/mp4" });
};
