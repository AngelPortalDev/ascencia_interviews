// recording.js - Complete updated file

import { uploadFile, downloadFile } from "./fileUpload.js";

// ============================================
// START RECORDING - Updated version
// ============================================
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
  encoded_interview_link_send_count,
  timeLimit = 60
) => {
  try {
    setIsRecording(true);
    setCountdown(timeLimit);

    //  IMPORTANT: Stop any existing stream before starting new one
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => {
        track.stop();
        console.log("🛑 Stopped old track:", track.kind);
      });
      videoRef.current.srcObject = null;
    }

    // Get new stream
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: { noiseSuppression: true, echoCancellation: true,autoGainControl: true, },
    });

    if (videoRef.current) {
      videoRef.current.srcObject = stream;
    }

    const types = [
      "video/webm;codecs=vp8,opus", // ✅ Preferred (broad support, safe for backend)
      "video/webm;codecs=vp9,opus", // fallback if VP8 not available
      "video/webm", // last-resort fallback
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

    //  Create new MediaRecorder
    mediaRecorderRef.current = new MediaRecorder(stream, {
      mimeType,
      audioBitsPerSecond: 32000,
      videoBitsPerSecond: 500000,
    });

    //  IMPORTANT: Clear chunks array for new recording
    recordedChunksRef.current = [];

    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
      }
    };

    mediaRecorderRef.current.onerror = (e) => {
      console.error("❌ MediaRecorder error:", e.error);
    };

    // Start recording
    mediaRecorderRef.current.start();
    setIsRecording(true);

    console.log("✅ Recording started for question:", question_id);
    console.log("⏱️ Time limit:", timeLimit, "seconds");
  } catch (error) {
    console.error("❌ Error accessing camera & microphone:", error);
  }
};

// ============================================
// STOP RECORDING - Updated for background upload
// ============================================
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
  onComplete
) => {
  const capturedQuestionId = question_id;
  const captureLastQuestionId = last_question_id;

  return new Promise((resolve, reject) => {
    // Check if there's an active recording
    if (!mediaRecorderRef.current || mediaRecorderRef.current.state === "inactive") {
      console.warn("⚠️ No active recording to stop");
      resolve({ videoPath: null, audioPath: null });
      if (onComplete) onComplete();
      return;
    }

    mediaRecorderRef.current.onstop = async () => {
      try {
        //  STEP 1: Create blob immediately from captured chunks
        const videoBlob = new Blob(recordedChunksRef.current, {
          type: "video/webm",
        });
        
        console.log("📹 Video blob created:", videoBlob.size, "bytes");

        //  STEP 2: Copy chunks and clear immediately so new recording can start
        const chunksToUpload = [...recordedChunksRef.current];
        recordedChunksRef.current = [];

        //  STEP 3: Resolve promise immediately so UI can continue
        resolve({ videoPath: null, audioPath: null });
        
        //  STEP 4: Call onComplete to allow new recording to start
        if (onComplete) {
          onComplete();
        }

        //  STEP 5: Upload in background (don't await, don't block)
        const fileNameVideo = `interview_video_${zoho_lead_id}_${capturedQuestionId}_${
          new Date().toISOString().replace(/:/g, "-").split(".")[0]
        }.webm`;

        console.log("📤 Starting background upload for:", capturedQuestionId);

        // Upload happens in background - we don't block here
        uploadFile(
          videoBlob,
          fileNameVideo,
          zoho_lead_id,
          capturedQuestionId,
          captureLastQuestionId,
          encoded_interview_link_send_count
        ).then((videoPath) => {
          console.log("✅ Background upload completed:", videoPath);
          setVideoFilePath(videoPath);
        }).catch((error) => {
          console.error("❌ Background upload failed:", error);
          // TODO: Add retry logic here if needed
          // You could store failed uploads and retry later
        });

      } catch (error) {
        console.error("❌ Error creating blob:", error);
        reject(error);
      }
    };

    // Stop the recorder
    console.log("⏸️ Stopping recording for question:", capturedQuestionId);
    mediaRecorderRef.current.stop();
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
