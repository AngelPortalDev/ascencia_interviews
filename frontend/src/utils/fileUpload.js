// services/upload.js

import axios from "axios";

// Uplaod File


let isUploading = false;

export const uploadFile = async (blob, filename,zoho_lead_id,question_id,last_question_id,encoded_interview_link_send_count) => {
  console.log("last_question_id test upload file" ,last_question_id);
  if (isUploading) return;  //  Duplicate Execution
  isUploading = true;


  const isInterviewSubmitted = question_id === last_question_id;
  console.log('question_id',question_id);
  
  console.log('last_question_id',last_question_id);
  console.log('isInterviewSubmitted',isInterviewSubmitted);

  const formData = new FormData();
  formData.append("file", blob, filename);
  formData.append("zoho_lead_id",btoa(zoho_lead_id));
  formData.append("last_question_id",last_question_id);
  formData.append("is_interview_submitted", isInterviewSubmitted);
  console.log("isInterviewSubmitted",isInterviewSubmitted);
  
  try {
    const response = await axios.post(
      `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-video-upload/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          console.log(`Upload progress: ${percentCompleted}%`);
        }
      }
    );
     console.log("✅ Upload Success Response:", response.data);
    if (response.data.file_path) {
      const videoFilePath = response.data.file_path;
      const audioFilePath = response.data.audio_path || videoFilePath; // If no separate audio, use video path

      console.log("Video uploaded successfully. File Path:", videoFilePath);

      // Call analyzeVideo function after upload is complete
      await interviewAddVideoPath(videoFilePath, audioFilePath, zoho_lead_id, question_id,last_question_id,isInterviewSubmitted,encoded_interview_link_send_count);
    } else {
      console.warn("⚠️ File path is missing in response.");
    }
    return response.data.file_path;
  } catch (error) {
    console.error("File upload failed:", error);
  }finally{
    isUploading = false;
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
let isAnalyzing = false; 
export const interviewAddVideoPath = async (videoFilePath, audioFilePath,zoho_lead_id,question_id,last_question_id,isInterviewSubmitted,encoded_interview_link_send_count) => {
  // if (!videoFilePath || !audioFilePath) {
  //   throw new Error("Video or audio path is missing.");
  if (isAnalyzing) {
    return;  
  }
  isAnalyzing = true;
  // }
  // console.log(zoho_lead_id,"test student");
  // console.log(question_id,"test question........................");
  // console.log("isInterviewSubmitted add video path",isInterviewSubmitted)
  const formData = new FormData();
  formData.append("video_path", videoFilePath);
  formData.append("audio_path", audioFilePath); 
  formData.append("zoho_lead_id", btoa(zoho_lead_id));
  formData.append("question_id", btoa(question_id));
  formData.append("last_question_id", btoa(last_question_id));
  formData.append("is_interview_submitted", isInterviewSubmitted);
  formData.append("encoded_interview_link_send_count",encoded_interview_link_send_count);
  // console.log('encoded_interview_link_send_count 11111111111',encoded_interview_link_send_count)
  try {
    const response = await axios.post(
      `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-add-video-path/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

     console.log("Video path upload started successfully:", response.data);



    // if (response.data && response.data.transcription) {
    //   console.log("New Transcription Data:", response.data);
    //   console.log("✅ Transcription Data:", response.data.sentiment);
    //   console.log("✅ Transcription Data:", response.data.grammar_results);



    //   // Check if onTranscription is being called correctly
    //   // onTranscription(response.data.transcription);
    //   const formData = new FormData();
    //   // formData.append("student_id", "123");
    //   formData.append("zoho_lead_id", btoa(zoho_lead_id));
    //   formData.append("question_id", btoa(question_id));
    //   formData.append("answer_text", response.data.transcription);
    //   formData.append("sentiment_score",response.data.sentiment.sentiment_score);
    //   formData.append("confidence_level",response.data.sentiment.confidence_level);
    //   formData.append("sent_subj",response.data.sentiment.subjectivity);
    //   formData.append("grammar_accuracy", response.data.grammar_results.grammar_accuracy);


    //     const responseVideoStore  = await axios.post(
    //       `${process.env.REACT_APP_API_BASE_URL}interveiw-section/student-interview-answers/`,
    //       formData,
    //       {
    //         headers: {
    //           "Content-Type": "multipart/form-data",
    //         },
    //       }
    //     );

    //   console.log("📩 onTranscription Called with:", responseVideoStore);
    // } 
    console.log("Video analysis started successfully:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error analyzing video:", error);
  }finally {
    isAnalyzing = false; // ✅ Reset flag after execution
  }
};
