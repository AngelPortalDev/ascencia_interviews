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
  // console.log("question_id 111",question_id)
  // console.log("last_question_id",last_question_id);
  // console.log("🔥 encoded_interview_link_send_count:", encoded_interview_link_send_count);
  // console.log("🔥 Type of last_question_id:", typeof last_question_id);
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

    // Video recording setup
//     mediaRecorderRef.current = new MediaRecorder(stream, {
//   mimeType: "video/webm;codecs=vp8,opus",  // Explicitly request vp8
//   audioBitsPerSecond: 32000,
//   videoBitsPerSecond: 1000000,
// });
const mimeType = MediaRecorder.isTypeSupported("video/webm;codecs=vp8,opus")
  ? "video/webm;codecs=vp8,opus"
  : "video/webm";

mediaRecorderRef.current = new MediaRecorder(stream, {
  mimeType,
  audioBitsPerSecond: 32000,
  videoBitsPerSecond: 500000,
});

    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) recordedChunksRef.current.push(event.data);
    };
    mediaRecorderRef.current.start();

    // Audio-only recording setup
    const audioStream = new MediaStream(stream.getAudioTracks());
    audioRecorderRef.current = new MediaRecorder(audioStream, {
      audioBitsPerSecond: 128000,
      mimeType: "audio/webm",
    });


    mediaRecorderRef.current.onerror = (e) => {
  console.error("❌ MediaRecorder error:", e.error);
};

    // audioRecorderRef.current.ondataavailable = (event) => {
    //   if (event.data.size > 0) recordedAudioChunksRef.current.push(event.data);
    // };
    // audioRecorderRef.current.start();

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
  // console.log("encoded_interview_link_send_countttt",encoded_interview_link_send_count);
  // console.log("capturedQuestionId",capturedQuestionId);
  // console.log("🔍 In stopRecording - typeof last_question_id:", typeof captureLastQuestionId, captureLastQuestionId);


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
        //  console.log("⏹️ Stopped video recording for question:", capturedQuestionId);
        //   console.log("📦 captureLastQuestionId:", captureLastQuestionId);
        // console.log("🎥 Stopping video recording...");
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

    if (audioRecorderRef.current) {
      audioRecorderRef.current.onstop = async () => {
        // console.log("⏹️ Stopped audio recording for question:", capturedQuestionId);
        // console.log("🔍 Audio section - typeof last_question_id:", typeof captureLastQuestionId, captureLastQuestionId);

        console.log("📦 Audio chunks size:", recordedAudioChunksRef.current.length);

        // console.log("🎤 Stopping audio recording...");
        const audioBlob = new Blob(recordedAudioChunksRef.current, { type: "audio/webm" });
        const fileNameAudio = `interview_audio_${zoho_lead_id}_${capturedQuestionId}_${new Date().toISOString().replace(/:/g, "-").split(".")[0]}.webm`;

        try {
          audioPath = await uploadFile(audioBlob, fileNameAudio, zoho_lead_id, capturedQuestionId, captureLastQuestionId,true);
          //   console.log('question_id in recording audio',capturedQuestionId)
          // console.log('last_question_id in recording audio',captureLastQuestionId)
          // console.log("📤 Audio uploaded. Path:", audioPath);
          setAudioFilePath(audioPath);
          audioUploaded = true;
          checkCompletion();
        } catch (error) {
          console.error("❌ Audio upload failed:", error);
          reject(error);
        }

        recordedAudioChunksRef.current = [];
      };
      audioRecorderRef.current.stop();
    } else {
      audioUploaded = true; 
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

