// import { uploadFile, downloadFile } from "./fileUpload.js";

// // ============================================
// // START RECORDING - Updated version
// // ============================================
// export const startRecording = async (
//   videoRef,
//   mediaRecorderRef,
//   audioRecorderRef,
//   recordedChunksRef,
//   recordedAudioChunksRef,
//   setIsRecording,
//   setCountdown,
//   setVideoFilePath,
//   setAudioFilePath,
//   zoho_lead_id,
//   question_id,
//   last_question_id,
//   encoded_interview_link_send_count,
//   timeLimit = 60
// ) => {
//   try {
//     setIsRecording(true);
//     setCountdown(timeLimit);

//     //  IMPORTANT: Stop any existing stream before starting new one
//     if (videoRef.current && videoRef.current.srcObject) {
//       const tracks = videoRef.current.srcObject.getTracks();
//       tracks.forEach(track => {
//         track.stop();
//         console.log("🛑 Stopped old track:", track.kind);
//       });
//       videoRef.current.srcObject = null;
//     }

//     // Get new stream
//     const stream = await navigator.mediaDevices.getUserMedia({
//       video:true,
//       audio: { noiseSuppression: false, echoCancellation: true,autoGainControl: true},
//     });

//     if (videoRef.current) {
//       videoRef.current.srcObject = stream;
//     }

//     const types = [
//       "video/webm;codecs=vp8,opus", // ✅ Preferred (broad support, safe for backend)
//       "video/webm;codecs=vp9,opus", // fallback if VP8 not available
//       "video/webm", // last-resort fallback
//     ];

//     function getSupportedMimeType(types) {
//       for (const type of types) {
//         if (MediaRecorder.isTypeSupported(type)) {
//           return type;
//         }
//       }
//       return "";
//     }

//     const mimeType = getSupportedMimeType(types);

//     //  Create new MediaRecorder
//     mediaRecorderRef.current = new MediaRecorder(stream, {
//       mimeType,
//       audioBitsPerSecond: 96000,
//       videoBitsPerSecond: 500000,
//     });

//     //  IMPORTANT: Clear chunks array for new recording
//     recordedChunksRef.current = [];
//     // setTimeout(() => { recordedChunksRef.current = []; }, 50);

//     mediaRecorderRef.current.ondataavailable = (event) => {
//       if (event.data.size > 0) {
//         recordedChunksRef.current.push(event.data);
//       }
//     };

//     mediaRecorderRef.current.onerror = (e) => {
//       console.error("❌ MediaRecorder error:", e.error);
//     };

//     // Start recording
//     mediaRecorderRef.current.start();
//     setIsRecording(true);

//     console.log("✅ Recording started for question:", question_id);
//     console.log("⏱️ Time limit:", timeLimit, "seconds");
//   } catch (error) {
//     console.error("❌ Error accessing camera & microphone:", error);
//   }
// };

// ============================================
// STOP RECORDING - Updated for background upload
// ============================================
// export const stopRecording = (
//   videoRef,
//   mediaRecorderRef,
//   audioRecorderRef,
//   recordedChunksRef,
//   recordedAudioChunksRef,
//   setVideoFilePath,
//   setAudioFilePath,
//   zoho_lead_id,
//   question_id,
//   last_question_id,
//   encoded_interview_link_send_count,
//   onComplete
// ) => {
//   const capturedQuestionId = question_id;
//   const captureLastQuestionId = last_question_id;

//   return new Promise((resolve, reject) => {
//     // Check if there's an active recording
//     if (!mediaRecorderRef.current || mediaRecorderRef.current.state === "inactive") {
//       console.warn("⚠️ No active recording to stop");
//       resolve({ videoPath: null, audioPath: null });
//       if (onComplete) onComplete();
//       return;
//     }

//     mediaRecorderRef.current.onstop = async () => {
//       try {
//         //  STEP 1: Create blob immediately from captured chunks
//         const videoBlob = new Blob(recordedChunksRef.current, {
//           type: "video/webm",
//         });

//         console.log("📹 Video blob created:", videoBlob.size, "bytes");

//         //  STEP 2: Copy chunks and clear immediately so new recording can start
//         const chunksToUpload = [...recordedChunksRef.current];
//         recordedChunksRef.current = [];
//         // setTimeout(() => { recordedChunksRef.current = []; }, 50);

//         //  STEP 3: Resolve promise immediately so UI can continue
//         resolve({ videoPath: null, audioPath: null });

//         //  STEP 4: Call onComplete to allow new recording to start
//         if (onComplete) {
//           onComplete();
//         }

//         //  STEP 5: Upload in background (don't await, don't block)
//         const fileNameVideo = `interview_video_${zoho_lead_id}_${capturedQuestionId}_${
//           new Date().toISOString().replace(/:/g, "-").split(".")[0]
//         }.webm`;

//         console.log("📤 Starting background upload for:", capturedQuestionId);

//         // Upload happens in background - we don't block here
//         uploadFile(
//           videoBlob,
//           fileNameVideo,
//           zoho_lead_id,
//           capturedQuestionId,
//           captureLastQuestionId,
//           encoded_interview_link_send_count
//         ).then((videoPath) => {
//           console.log("✅ Background upload completed:", videoPath);
//           setVideoFilePath(videoPath);
//         }).catch((error) => {
//           console.error("❌ Background upload failed:", error);
//           // TODO: Add retry logic here if needed
//           // You could store failed uploads and retry later
//         });

//       } catch (error) {
//         console.error("❌ Error creating blob:", error);
//         reject(error);
//       }
//     };

//     // Stop the recorder
//     console.log("⏸️ Stopping recording for question:", capturedQuestionId);
//     mediaRecorderRef.current.stop();
//   });
// };

// export const stopRecording = (
//   videoRef,
//   mediaRecorderRef,
//   audioRecorderRef,
//   recordedChunksRef,
//   recordedAudioChunksRef,
//   setVideoFilePath,
//   setAudioFilePath,
//   zoho_lead_id,
//   question_id,
//   last_question_id,
//   encoded_interview_link_send_count,
//   onComplete
// ) => {
//   const capturedQuestionId = question_id;
//   const captureLastQuestionId = last_question_id;

//   return new Promise((resolve) => {
//     const recorder = mediaRecorderRef.current;

//     if (!recorder || recorder.state === "inactive") {
//       resolve({ videoPath: null });
//       onComplete && onComplete();
//       return;
//     }

//     // console.log("⏸ Stopping recording…");

//     // 1️ Create placeholder so UI can move instantly
//     resolve({ videoPath: null });
//     onComplete && onComplete();

//     // 2️ After the above returns, we wait internally for final chunks
//     recorder.onstop = async () => {
//       try {
//         // Wait a tick for final dataavailable
//         await new Promise((r) => setTimeout(r, 250));

//         const blob = new Blob(recordedChunksRef.current, {
//           type: "video/webm"
//         });

//         recordedChunksRef.current = [];

//         // 3 Background upload — actual work starts only after final blob is ready
//         const fileName = `interview_${zoho_lead_id}_${capturedQuestionId}_${
//           new Date().toISOString().replace(/:/g, "-").split(".")[0]
//         }.webm`;

//         // console.log("📤 Background upload starting…");

//         uploadFile(
//           blob,
//           fileName,
//           zoho_lead_id,
//           capturedQuestionId,
//           captureLastQuestionId,
//           encoded_interview_link_send_count
//         )
//           .then((videoPath) => {
//             console.log("✅ Upload completed:", videoPath);
//             setVideoFilePath(videoPath);
//           })
//           .catch((err) => console.error("❌ Upload failed:", err));

//       } catch (e) {
//         console.error("❌ Error finalizing blob:", e);
//       }
//     };

//     // 4 Actually stop the recorder
//     recorder.stop();
//   });
// };

// recording.js - FIXED VERSION

import { uploadFile } from "./fileUpload.js";

// ============================================
// START RECORDING - Fixed version
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
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      console.log(" Stopping existing recorder before starting new one");
      mediaRecorderRef.current.stop();
      await new Promise((resolve) => setTimeout(resolve, 300));
    }

    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => {
        track.stop();
        console.log("Stopped track:", track.kind);
      });
      videoRef.current.srcObject = null;
    }

    // Clear chunks BEFORE starting new recording
    recordedChunksRef.current = [];
    console.log("Cleared chunks array");

    // Get new stream
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: 480,
        height: 360,
        frameRate: { ideal: 24, max: 24 },
      },
      audio: {
        noiseSuppression: false,
        echoCancellation: true,
        autoGainControl: true,
      },
    });

    if (videoRef.current) {
      videoRef.current.srcObject = stream;
    }

    // Get supported MIME type
    const types = [
      "video/webm;codecs=vp8,opus",
      "video/webm;codecs=vp9,opus",
      "video/webm",
    ];

    const mimeType =
      types.find((type) => MediaRecorder.isTypeSupported(type)) || types[2];

    // Create new MediaRecorder
    mediaRecorderRef.current = new MediaRecorder(stream, {
      mimeType,
      videoBitsPerSecond: 600000,
      audioBitsPerSecond: 96000,
    });

    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
        console.log(
          `Chunk added: ${event.data.size} bytes (Total chunks: ${recordedChunksRef.current.length})`
        );
      } else {
        console.warn("Received empty chunk");
      }
    };

    mediaRecorderRef.current.onerror = (e) => {
      console.error("MediaRecorder error:", e.error);
    };

    mediaRecorderRef.current.start();
    setIsRecording(true);
    setCountdown(timeLimit);

    console.log("Time limit:", timeLimit, "seconds");
  } catch (error) {
    console.error("Error starting recording:", error);
    throw error;
  }
};

// ============================================
// STOP RECORDING - Fixed version
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

  return new Promise((resolve) => {
    const recorder = mediaRecorderRef.current;

    if (!recorder || recorder.state === "inactive") {
      console.log("Recorder already stopped or not initialized");
      resolve({ videoPath: null });
      if (onComplete) onComplete();
      return;
    }

    console.log("Stopping recording for question:", capturedQuestionId);

    recorder.onstop = async () => {
      try {
        console.log("Recorder stopped, processing chunks...");

        await new Promise((resolve) => setTimeout(resolve, 500));

        const totalChunks = recordedChunksRef.current.length;
        const totalSize = recordedChunksRef.current.reduce(
          (sum, chunk) => sum + chunk.size,
          0
        );

        console.log(
          `Total chunks: ${totalChunks}, Total size: ${totalSize} bytes`
        );

        if (totalSize === 0) {
          console.error("No data recorded! Chunks array is empty.");
          resolve({ videoPath: null, error: "No data recorded" });
          if (onComplete) onComplete();
          return;
        }

        const blob = new Blob(recordedChunksRef.current, {
          type: recorder.mimeType || "video/webm",
        });

        console.log(`✅ Blob created: ${blob.size} bytes`);

        const chunksBackup = [...recordedChunksRef.current];
        recordedChunksRef.current = [];

        const timestamp = new Date()
          .toISOString()
          .replace(/:/g, "-")
          .split(".")[0];
        const fileName = `interview_${zoho_lead_id}_${capturedQuestionId}_${timestamp}.webm`;

        if (onComplete) {
          onComplete();
        }

        // Resolve promise to allow UI to proceed
        resolve({ videoPath: null, blob, fileName });

        uploadFile(
          blob,
          fileName,
          zoho_lead_id,
          capturedQuestionId,
          captureLastQuestionId,
          encoded_interview_link_send_count
        )
          .then((videoPath) => {
            console.log("Upload completed:", videoPath);
            setVideoFilePath(videoPath);
          })
          .catch((err) => {
            console.error(" Upload failed:", err);
            // Optionally retry upload with backup chunks
            console.log(" Backup chunks available:", chunksBackup.length);
          });
      } catch (error) {
        console.error("Error in onstop handler:", error);
        resolve({ videoPath: null, error: error.message });
        if (onComplete) onComplete();
      }
    };

    try {
      if (recorder.state === "recording") {
        recorder.stop();
      }
    } catch (error) {
      console.error("❌ Error stopping recorder:", error);
      resolve({ videoPath: null, error: error.message });
      if (onComplete) onComplete();
    }

    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
    }
  });
};
