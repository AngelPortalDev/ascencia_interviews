// utils/recording.js


import { uploadFile, downloadFile } from "./fileUpload.js";
export const startRecording = async (
  videoRef,
  mediaRecorderRef,
  audioRecorderRef,
  recordedChunksRef,
  recordedAudioChunksRef,
  setIsRecording,
  setCountdown,
  setVideoFilePath,
  setAudioFilePath,
  zoho_lead_id,
  question_id,
  last_question_id,
  encoded_interview_link_send_count
) => {
  try {
  // console.log("question_id 222",question_id);
   setIsRecording(true);
   setCountdown(60);

    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: { noiseSuppression: false, echoCancellation: false },
      // audio:true
    });
    
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
    }


const types = [
  "video/webm;codecs=vp8,opus", // ✅ Preferred (broad support, safe for backend)
  "video/webm;codecs=vp9,opus", // fallback if VP8 not available
  "video/webm"                  // last-resort fallback
];

function getSupportedMimeType(types) {
  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) {
      return type;
    }
  }
  return "";
}

const mimeType = getSupportedMimeType(types);

mediaRecorderRef.current = new MediaRecorder(stream, {
  mimeType,
  audioBitsPerSecond: 32000,
  videoBitsPerSecond: 500000,
});

    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) recordedChunksRef.current.push(event.data);
    };
    mediaRecorderRef.current.start();

    mediaRecorderRef.current.onerror = (e) => {
      console.error("❌ MediaRecorder error:", e.error);
  };


    if (videoRef.current) videoRef.current.srcObject = stream;
    setIsRecording(true);
  } catch (error) {
    console.error("Error accessing camera & microphone.", error);
  }
};

export const stopRecording = (
  videoRef,
  mediaRecorderRef,
  audioRecorderRef,
  recordedChunksRef,
  recordedAudioChunksRef,
  setVideoFilePath,
  setAudioFilePath,
  zoho_lead_id,
  question_id,
  last_question_id,
  encoded_interview_link_send_count,
) => {
    const capturedQuestionId = question_id;
    const captureLastQuestionId = last_question_id


  return new Promise((resolve, reject) => { 
    let videoUploaded = false;
    let audioUploaded = false;
    let videoPath = null;
    let audioPath = null;

    const checkCompletion = () => {
      if (videoUploaded && audioUploaded) {
        resolve({ videoPath, audioPath });  
      }
    };

    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.onstop = async () => {
        const videoBlob = new Blob(recordedChunksRef.current, { type: "video/webm" });
        const fileNameVideo = `interview_video_${zoho_lead_id}_${capturedQuestionId}_${new Date().toISOString().replace(/:/g, "-").split(".")[0]}.webm`;

        try {
          videoPath = await uploadFile(videoBlob, fileNameVideo, zoho_lead_id, capturedQuestionId, captureLastQuestionId,encoded_interview_link_send_count,true);
          // console.log('question_id in recording',capturedQuestionId)
          console.log('last_question_id in recording',captureLastQuestionId)

          // console.log("📤 Video uploaded. Path:", videoPath);
          setVideoFilePath(videoPath);
          videoUploaded = true;
          checkCompletion();
        } catch (error) {
          console.error("❌ Video upload failed:", error);
          reject(error);
        }

        recordedChunksRef.current = [];
      };
      mediaRecorderRef.current.stop();
    } else {
      videoUploaded = true; 
      checkCompletion();
    }
  });
};

// utils/stopMediaStream.js

// export const stopMediaStream = (videoRef) => {
//   if (videoRef.current && videoRef.current.srcObject) {
//     console.log("videoRef.current.srcObject",videoRef.current.srcObject)
//     console.log("videoRef.current",videoRef.current);
//     console.log("videoRef",videoRef);
//     const stream = videoRef.current.srcObject;
//     const tracks = stream.getTracks();
//     console.log("stream",stream)
//     console.log("tracks",tracks)

//     tracks.forEach((track) => {
//       track.stop();  // Stop each track (video & audio)
//     });

//     videoRef.current.srcObject = null;  // Clear the video feed
//     console.log("✅ Camera & microphone stream stopped.");
//   } else {
//     console.log("No media stream found to stop.");
//   }
// };


// export const setupMediaStream = async (videoRef) => {
//   try {
//     // Step 1: Get user media stream (video and audio)
//     const stream = await navigator.mediaDevices.getUserMedia({
//       video: true,
//       audio: { noiseSuppression: false, echoCancellation: false },
//     });

//     // Step 2: Assign the stream to videoRef.srcObject
//     if (videoRef.current) {
//       videoRef.current.srcObject = stream;
//     }

//     // Step 3: Log srcObject to verify the stream assignment
//     // console.log("videoRef.current.srcObject after assignment:", videoRef.current.srcObject);

//   } catch (error) {
//     console.error("Error accessing media devices:", error);
//   }
// };




// Stop the media stream and clear srcObject from videoRef
// export const stopMediaStream = (videoRef) => {
//   console.log("before stopmedia stream",videoRef.current?.srcObject)
//   const stream = videoRef.current?.srcObject;
//   console.log("before stopmedia stream",videoRef.current?.srcObject)
//   if (stream) {
//     const tracks = stream.getTracks();
//     tracks.forEach((track) => {
//       track.stop(); // Stop each track (video & audio)
//     });
//     videoRef.current.srcObject = null; // Clear the srcObject
//     console.log("Media stream stopped.");
//   }
// };

