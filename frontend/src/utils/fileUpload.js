// services/upload.js

import axios from "axios";

// Uplaod File
export const uploadFile = async (blob, filename) => {
  const formData = new FormData();
  formData.append("file", blob, filename);

  try {
    const response = await axios.post(
      `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-video-upload/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data.file_path;
  } catch (error) {
    console.error("File upload failed:", error);
    throw error;
  }
};

// File download function
export const downloadFile = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
};

// Analyze Video
export const analyzeVideo = async (videoFilePath, audioFilePath,onTranscription) => {
  if (!videoFilePath || !audioFilePath) {
    throw new Error("Video or audio path is missing.");
  }

  const formData = new FormData();
  formData.append("video_path", videoFilePath);
  formData.append("audio_path", audioFilePath);

  try {
    const response = await axios.post(
      `${process.env.REACT_APP_API_BASE_URL}interveiw-section/analyze-video/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    if (response.data && response.data.transcription) {
      console.log("✅ Transcription Data:", response.data.transcription);

      // Check if onTranscription is being called correctly
      onTranscription(response.data.transcription);
      console.log("📩 onTranscription Called with:", response.data.transcription);
    } else {
      console.warn("⚠️ Transcription response is missing expected data.");
    }
    console.log("Video analysis started successfully:", response.data);
  } catch (error) {
    console.error("Error analyzing video:", error);
  }
};
