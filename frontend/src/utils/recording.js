import { uploadFile } from "./fileUpload.js";
import RecordRTC from "recordrtc";
// ============================================
// UTILITY: Detect Browser
// ============================================
const getBrowserType = () => {
  const ua = navigator.userAgent.toLowerCase();

  if (ua.includes("firefox")) return "firefox";
  if (ua.includes("edg")) return "edge";
  if (ua.includes("chrome") && !ua.includes("edg")) return "chrome";
  if (ua.includes("safari") && !ua.includes("chrome")) return "safari";

  return "unknown";
};

// ============================================
// UTILITY: Get Optimal MIME Type
// ============================================
const getOptimalMimeType = () => {
  const browserType = getBrowserType();

  // Prefer VP8/Opus for cross-browser compatibility
  if (browserType === "firefox") {
    return "video/webm;codecs=vp8,opus";
  }

  const types = [
    "video/webm;codecs=vp8,opus",
    "video/webm;codecs=vp8",
    "video/webm",
  ];

  return types.find((t) => {
    try {
      return MediaRecorder.isTypeSupported(t);
    } catch (e) {
      return false;
    }
  }) || "video/webm";
};

// ============================================
// UTILITY: Get Optimal Timeslice
// ============================================
const getOptimalTimeslice = () => {
  const browserType = getBrowserType();
  if (browserType === "firefox") return 1000; 
  return 500; 
};

// ============================================
// UTILITY: Get Wait Time After Stop
// ============================================
const getStopWaitTime = () => {
  const browserType = getBrowserType();
  if (browserType === "firefox") return 1000;
  return 500;
};

// ============================================
// UTILITY: Validate Recording Blob
// ============================================
const validateRecording = (blob, timeLimit) => {
  const minSize = 1000; 
  const expectedMinSize = timeLimit * 10000; 

  if (!blob || typeof blob.size !== "number") {
    return { valid: false, error: "Invalid blob" };
  }

  if (blob.size < minSize) {
    console.error(`❌ Recording too small: ${blob.size} bytes`);
    return { valid: false, error: "Recording file too small" };
  }

  if (blob.size < expectedMinSize * 0.3) {
    console.warn(
      ` Recording smaller than expected: ${blob.size} bytes (expected ~${expectedMinSize} bytes)`
    );
  }

  console.log(`✅ Recording validation passed: ${blob.size} bytes`);
  return { valid: true };
};

// ============================================
// START RECORDING
// - Uses RecordRTC for Safari + Firefox
// - Uses MediaRecorder for Chrome + Edge
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
    const browserType = getBrowserType();
    console.log(` Browser detected: ${browserType}`);

    try {
      if (mediaRecorderRef.current) {
        // If it's RecordRTC instance
        if (typeof mediaRecorderRef.current.stopRecording === "function") {
          try {
            mediaRecorderRef.current.stopRecording();
          } catch (e) {
            
          }
        } else if (typeof mediaRecorderRef.current.stop === "function") {
          try {
            if (mediaRecorderRef.current.state !== "inactive") {
              mediaRecorderRef.current.stop();
            }
          } catch (e) {
           
          }
        }
        
        await new Promise((r) => setTimeout(r, 300));
      }
    } catch (err) {
      console.warn("Error stopping previous recorder:", err);
    }

    // Stop any active tracks and clear srcObject
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((t) => {
        try {
          t.stop();
        } catch (e) {}
      });
      videoRef.current.srcObject = null;
    }

    // Clear previous chunk buffer
    recordedChunksRef.current = [];

    // Request media (combined audio + video)
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 480 },
        height: { ideal: 360 },
        frameRate: { ideal: 24, max: 30 },
      },
      audio: {
        noiseSuppression: true,
        echoCancellation: true,
        autoGainControl: true,
        sampleRate: 48000,
        channelCount: 1,
      },
    });

    // Show preview
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      try {
        await new Promise((resolve) => {
          if (videoRef.current.readyState >= 2) resolve();
          else videoRef.current.onloadedmetadata = resolve;
        });
      } catch (e) {
        /* ignore */
      }
    }

    // Use RecordRTC for Safari & Firefox
    if (browserType === "safari" || browserType === "firefox") {
      console.log(" Using RecordRTC for", browserType);

      // Configure RecordRTC to record combined audio+video as single blob
      const recorder = new RecordRTC(stream, {
        type: "video",
        mimeType: getOptimalMimeType(), // likely webm
        bitsPerSecond: 512000,
        // ensure audio+video are captured
        // RecordRTC will manage internal recorderType selection
        video: {
          width: 480,
          height: 360,
          frameRate: 24,
        },
        // disable logs? keep for debug
        disableLogs: false,
      });

      recorder.startRecording();
      // store the recorder instance (RecordRTC exposes stopRecording/getBlob)
      mediaRecorderRef.current = recorder;

      setIsRecording(true);
      setCountdown(timeLimit);
      console.log("🎬 RecordRTC recording started");
      return;
    }

    // Otherwise use MediaRecorder for Chrome/Edge
    const mimeType = getOptimalMimeType();
    const timeslice = getOptimalTimeslice();

    console.log(`📹 Using MediaRecorder MIME type: ${mimeType}`);
    console.log(`⏱ Using timeslice: ${timeslice}ms`);

    const recorderOptions = {
      mimeType,
      // keep bits per second reasonable
      videoBitsPerSecond: 600000,
      audioBitsPerSecond: 96000,
    };

    const mediaRecorder = new MediaRecorder(stream, recorderOptions);

    mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
        console.log(
          `📦 Chunk added: ${event.data.size} bytes (chunks: ${recordedChunksRef.current.length})`
        );
      } else {
        console.warn("⚠️ Received empty chunk");
      }
    };

    mediaRecorder.onerror = (e) => {
      console.error("❌ MediaRecorder error:", e);
    };

    mediaRecorder.onstart = () => {
      console.log("▶ MediaRecorder started");
    };

    mediaRecorderRef.current = mediaRecorder;

    mediaRecorder.start(timeslice);

    setIsRecording(true);
    setCountdown(timeLimit);
    console.log(`🎬 MediaRecorder recording started for ${timeLimit} seconds`);
  } catch (error) {
    console.error("❌ Error in startRecording:", error);
    // cleanup
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((t) => {
        try {
          t.stop();
        } catch (e) {}
      });
      videoRef.current.srcObject = null;
    }
    throw error;
  }
};

// ============================================
// STOP RECORDING
// - Handles RecordRTC (Safari/Firefox) + MediaRecorder (Chrome/Edge)
// - Produces single combined file, validates and uploads
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
  const browserType = getBrowserType();
  const waitTime = getStopWaitTime();

  return new Promise((resolve) => {
    // SAFELY handle RecordRTC path (Safari + Firefox)
    if (browserType === "safari" || browserType === "firefox") {
      const recorder = mediaRecorderRef.current;
      if (!recorder || typeof recorder.stopRecording !== "function") {
        console.warn("⚠️ No RecordRTC recorder found to stop");
        resolve({ videoPath: null });
        if (onComplete) onComplete();
        return;
      }

      console.log(`🛑 Stopping RecordRTC recorder for ${browserType}`);

      try {
        recorder.stopRecording(async () => {
          try {
            const blob = await recorder.getBlob();
            console.log("📦 RecordRTC blob size:", blob ? blob.size : "no blob");

            // Validate blob
            const validation = validateRecording(blob, 60);
            if (!validation.valid) {
              console.error("❌ RecordRTC validation failed:", validation.error);
              resolve({ videoPath: null, error: validation.error });
              if (onComplete) onComplete();
              return;
            }

            // filename
            const timestamp = new Date()
              .toISOString()
              .replace(/:/g, "-")
              .split(".")[0];
            const fileName = `interview_${zoho_lead_id}_${question_id}_${timestamp}.webm`;

            // Stop camera tracks
            if (videoRef.current && videoRef.current.srcObject) {
              try {
                const tracks = videoRef.current.srcObject.getTracks();
                tracks.forEach((t) => {
                  try {
                    t.stop();
                  } catch (e) {}
                });
                videoRef.current.srcObject = null;
              } catch (e) {
                console.warn("Error stopping tracks:", e);
              }
            }

            // Resolve so UI can proceed, then upload in background
            resolve({ videoPath: null, blob, fileName });

            console.log(" Uploading RecordRTC blob...");
            uploadFile(
              blob,
              fileName,
              zoho_lead_id,
              question_id,
              last_question_id,
              encoded_interview_link_send_count
            )
              .then((videoPath) => {
                console.log("✅ Upload completed:", videoPath);
                setVideoFilePath(videoPath);
                if (onComplete) onComplete();
              })
              .catch((err) => {
                console.error("❌ Upload failed:", err);
                if (onComplete) onComplete();
              });
          } catch (err) {
            console.error("❌ Error processing RecordRTC blob:", err);
            resolve({ videoPath: null, error: err.message });
            if (onComplete) onComplete();
          }
        });
      } catch (err) {
        console.error("❌ Error stopping RecordRTC:", err);
        resolve({ videoPath: null, error: err.message });
        if (onComplete) onComplete();
      }

      return; // done for RecordRTC path
    }

    // ----------------------------------------
    // MEDIARECORDER path (Chrome + Edge)
    // ----------------------------------------
    const mediaRecorder = mediaRecorderRef.current;
    if (!mediaRecorder) {
      console.warn("⚠️ No mediaRecorder found");
      resolve({ videoPath: null });
      if (onComplete) onComplete();
      return;
    }

    // If already inactive
    if (mediaRecorder.state === "inactive") {
      console.log("⚠️ MediaRecorder already inactive");
      resolve({ videoPath: null });
      if (onComplete) onComplete();
      return;
    }

    console.log("🛑 Stopping MediaRecorder, waiting for chunks to flush...");
    let stopTimeout;

    mediaRecorder.onstop = async () => {
      try {
        if (stopTimeout) clearTimeout(stopTimeout);

        // wait for browser flush
        await new Promise((r) => setTimeout(r, waitTime));

        const totalChunks = recordedChunksRef.current.length;
        const totalSize = recordedChunksRef.current.reduce(
          (s, c) => s + (c.size || 0),
          0
        );

        console.log(`📊 Total chunks: ${totalChunks}, totalSize: ${totalSize} bytes`);

        if (totalSize === 0) {
          console.error("❌ No data recorded (MediaRecorder).");
          resolve({ videoPath: null, error: "No data recorded" });
          if (onComplete) onComplete();
          return;
        }

        const validChunks = recordedChunksRef.current.filter((c) => c && c.size > 0);
        const blob = new Blob(validChunks, {
          type: mediaRecorder.mimeType || getOptimalMimeType(),
        });

        console.log("📦 Blob created from chunks:", blob.size);

        // Validate
        const validation = validateRecording(blob, 60);
        if (!validation.valid) {
          console.error("❌ Validation failed:", validation.error);
          resolve({ videoPath: null, error: validation.error });
          if (onComplete) onComplete();
          return;
        }

        // backup and clear chunks
        const chunksBackup = [...recordedChunksRef.current];
        recordedChunksRef.current = [];

        const timestamp = new Date()
          .toISOString()
          .replace(/:/g, "-")
          .split(".")[0];
        const fileName = `interview_${zoho_lead_id}_${question_id}_${timestamp}.webm`;

        // Stop tracks
        if (videoRef.current && videoRef.current.srcObject) {
          try {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach((t) => {
              try { t.stop(); } catch (e) {}
            });
            videoRef.current.srcObject = null;
          } catch (e) {
            console.warn("Error stopping tracks:", e);
          }
        }

        // Resolve early so UI can proceed
        resolve({ videoPath: null, blob, fileName });

        // Upload blob
        console.log("☁️ Uploading MediaRecorder blob...");
        uploadFile(
          blob,
          fileName,
          zoho_lead_id,
          question_id,
          last_question_id,
          encoded_interview_link_send_count
        )
          .then((videoPath) => {
            console.log("✅ Upload completed:", videoPath);
            setVideoFilePath(videoPath);
            if (onComplete) onComplete();
          })
          .catch((err) => {
            console.error("❌ Upload failed:", err);
            // you may retry using chunksBackup
            if (onComplete) onComplete();
          });
      } catch (err) {
        console.error("❌ Error in MediaRecorder onstop:", err);
        resolve({ videoPath: null, error: err.message });
        if (onComplete) onComplete();
      }
    };

    // Request final data and stop
    try {
      if (mediaRecorder.state === "recording") {
        mediaRecorder.requestData();

        const stopDelay = browserType === "firefox" ? 200 : 100;
        setTimeout(() => {
          try {
            if (mediaRecorder.state === "recording" || mediaRecorder.state === "paused") {
              mediaRecorder.stop();
            }
          } catch (e) {
            console.warn("Error calling mediaRecorder.stop():", e);
          }
        }, stopDelay);

        // Safety timeout if onstop doesn't fire
        stopTimeout = setTimeout(() => {
          console.warn("⚠️ Stop event didn't fire, forcing cleanup");
          try {
            if (mediaRecorder.state !== "inactive") mediaRecorder.stop();
          } catch (e) {
            console.error("❌ Error forcing mediaRecorder.stop():", e);
          }
          resolve({ videoPath: null, error: "Stop timeout" });
          if (onComplete) onComplete();
        }, 5000);
      } else {
        // If not recording, resolve immediately
        resolve({ videoPath: null });
        if (onComplete) onComplete();
      }
    } catch (err) {
      console.error("❌ Error stopping recorder:", err);
      resolve({ videoPath: null, error: err.message });
      if (onComplete) onComplete();
    }
  });
};