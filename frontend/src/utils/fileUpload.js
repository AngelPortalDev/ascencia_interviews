// services/upload.js

import axios from "axios";

// Uplaod File
export const uploadFile = async (blob, filename,student_id,question_id) => {
  const formData = new FormData();
  formData.append("file", blob, filename);
  formData.append("student_id",student_id );
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
export const analyzeVideo = async (videoFilePath, audioFilePath,onTranscription,student_id,question_id) => {
  if (!videoFilePath || !audioFilePath) {
    throw new Error("Video or audio path is missing.");
  }
  console.log(student_id,"test student");
  console.log(question_id,"test question");
  const formData = new FormData();
  formData.append("video_path", videoFilePath);
  formData.append("audio_path", audioFilePath); 
  formData.append("student_id", student_id);
  formData.append("question_id", question_id);

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
      console.log("✅ Transcription Data:", response.data.sentiment);

      // Check if onTranscription is being called correctly
      // onTranscription(response.data.transcription);
      const formData = new FormData();
      formData.append("student_id", "123");
      formData.append("zoho_lead_id", student_id);
      formData.append("question_id", question_id);
      formData.append("answer_text", response.data.transcription);
      formData.append("sentiment_score", "90");
      formData.append("grammar_accuracy", response.data.grammar_results.grammer_accuracy);


        const responseVideoStore  = await axios.post(
          `${process.env.REACT_APP_API_BASE_URL}interveiw-section/student-interview-answers/`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

      console.log("📩 onTranscription Called with:", responseVideoStore);
    } else {
      console.warn("⚠️ Transcription response is missing expected data.");
    }
    console.log("Video analysis started successfully:", response.data);
  } catch (error) {
    console.error("Error analyzing video:", error);
  }
};
