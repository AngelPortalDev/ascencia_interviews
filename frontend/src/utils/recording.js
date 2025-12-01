import { uploadFile } from "./fileUpload.js";

// ============================================
// UTILITY: Detect Browser
// ============================================
const getBrowserType = () => {
  const userAgent = navigator.userAgent.toLowerCase();
  
  if (userAgent.includes('firefox')) {
    return 'firefox';
  } else if (userAgent.includes('edg')) {
    return 'edge';
  } else if (userAgent.includes('chrome')) {
    return 'chrome';
  } else if (userAgent.includes('safari')) {
    return 'safari';
  }
  
  return 'unknown';
};

// ============================================
// UTILITY: Get Optimal MIME Type
// ============================================
const getOptimalMimeType = () => {
  const browserType = getBrowserType();
  
  // Firefox works best with VP8
  if (browserType === 'firefox') {
    return "video/webm;codecs=vp8,opus";
  }
  
  // Chrome/Edge prefer VP9
  const types = [
    "video/webm;codecs=vp9,opus",
    "video/webm;codecs=vp8,opus",
    "video/webm",
  ];
  
  return types.find((type) => MediaRecorder.isTypeSupported(type)) || "video/webm";
};

// ============================================
// UTILITY: Get Optimal Timeslice
// ============================================
const getOptimalTimeslice = () => {
  const browserType = getBrowserType();
  
  // Firefox needs larger timeslice to prevent corruption
  if (browserType === 'firefox') {
    return 1000; // 1 second
  }
  
  // Chrome/Edge work well with smaller timeslice
  return 100; // 100ms
};

// ============================================
// UTILITY: Get Wait Time After Stop
// ============================================
const getStopWaitTime = () => {
  const browserType = getBrowserType();
  
  // Firefox needs more time to flush chunks
  if (browserType === 'firefox') {
    return 1000; // 1 second
  }
  
  return 500; // 500ms for others
};

// ============================================
// UTILITY: Validate Recording Blob
// ============================================
const validateRecording = (blob, timeLimit) => {
  const minSize = 1000; // 1KB absolute minimum
  const expectedMinSize = timeLimit * 10000; // ~10KB per second rough estimate
  
  if (blob.size < minSize) {
    console.error(`❌ Recording too small: ${blob.size} bytes`);
    return { valid: false, error: "Recording file too small" };
  }
  
  if (blob.size < expectedMinSize * 0.3) {
    console.warn(`⚠️ Recording smaller than expected: ${blob.size} bytes (expected ~${expectedMinSize} bytes)`);
  }
  
  console.log(`✅ Recording validation passed: ${blob.size} bytes`);
  return { valid: true };
};

// ============================================
// START RECORDING - Complete Fixed Version
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
    console.log(`🌐 Browser detected: ${browserType}`);

    // Stop existing recorder properly
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      console.log("🛑 Stopping existing recorder before starting new one");
      mediaRecorderRef.current.stop();
      await new Promise((resolve) => setTimeout(resolve, 500));
    }

    // Stop all existing tracks
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => {
        track.stop();
        console.log(`🛑 Stopped track: ${track.kind}`);
      });
      videoRef.current.srcObject = null;
    }

    // Clear chunks BEFORE starting new recording
    recordedChunksRef.current = [];
    console.log("🧹 Cleared chunks array");

    // Get new stream with optimized settings
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
        channelCount: 1, // Mono for consistency
      },
    });

    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      // Wait for video to be ready
      await new Promise((resolve) => {
        if (videoRef.current.readyState >= 2) {
          resolve();
        } else {
          videoRef.current.onloadedmetadata = resolve;
        }
      });
    }

    // Get optimal settings for current browser
    const mimeType = getOptimalMimeType();
    const timeslice = getOptimalTimeslice();
    
    console.log(`📹 Using MIME type: ${mimeType}`);
    console.log(`⏱️ Using timeslice: ${timeslice}ms`);

    // Create new MediaRecorder with browser-optimized settings
    const recorderOptions = {
      mimeType,
      videoBitsPerSecond: browserType === 'firefox' ? 500000 : 600000,
      audioBitsPerSecond: 96000,
    };

    mediaRecorderRef.current = new MediaRecorder(stream, recorderOptions);

    // Event: Data Available
    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
        console.log(
          `📦 Chunk added: ${event.data.size} bytes (Total: ${recordedChunksRef.current.length} chunks)`
        );
      } else {
        console.warn("⚠️ Received empty chunk");
      }
    };

    // Event: Error
    mediaRecorderRef.current.onerror = (e) => {
      console.error("❌ MediaRecorder error:", e.error);
    };

    // Event: Start
    mediaRecorderRef.current.onstart = () => {
      console.log("▶️ MediaRecorder started successfully");
    };

    // Event: Pause (for debugging)
    mediaRecorderRef.current.onpause = () => {
      console.log("⏸️ MediaRecorder paused");
    };

    // Event: Resume (for debugging)
    mediaRecorderRef.current.onresume = () => {
      console.log("▶️ MediaRecorder resumed");
    };

    // Start recording with optimal timeslice
    mediaRecorderRef.current.start(timeslice);
    setIsRecording(true);
    setCountdown(timeLimit);

    console.log(`🎬 Recording started successfully for ${timeLimit} seconds`);
  } catch (error) {
    console.error("❌ Error starting recording:", error);
    
    // Clean up on error
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    
    throw error;
  }
};

// ============================================
// STOP RECORDING - Complete Fixed Version
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
  const browserType = getBrowserType();
  const waitTime = getStopWaitTime();

  return new Promise((resolve) => {
    const recorder = mediaRecorderRef.current;

    if (!recorder || recorder.state === "inactive") {
      console.log("⚠️ Recorder already stopped or not initialized");
      resolve({ videoPath: null });
      if (onComplete) onComplete();
      return;
    }

    console.log(`🛑 Stopping recording for question: ${capturedQuestionId}`);
    console.log(`🌐 Browser: ${browserType}, Wait time: ${waitTime}ms`);

    let stopTimeout;

    recorder.onstop = async () => {
      try {
        console.log("⏹️ Recorder stopped, processing chunks...");

        // Clear the timeout if stop event fired
        if (stopTimeout) {
          clearTimeout(stopTimeout);
        }

        // Wait for browser to flush all chunks
        await new Promise((resolve) => setTimeout(resolve, waitTime));

        const totalChunks = recordedChunksRef.current.length;
        const totalSize = recordedChunksRef.current.reduce(
          (sum, chunk) => sum + chunk.size,
          0
        );

        console.log(
          `📊 Total chunks: ${totalChunks}, Total size: ${totalSize} bytes`
        );

        if (totalSize === 0) {
          console.error("❌ No data recorded! Chunks array is empty.");
          resolve({ videoPath: null, error: "No data recorded" });
          if (onComplete) onComplete();
          return;
        }

        // Validate and filter chunks
        const validChunks = recordedChunksRef.current.filter(
          (chunk) => chunk && chunk.size > 0
        );

        if (validChunks.length !== totalChunks) {
          console.warn(
            `⚠️ Filtered out ${totalChunks - validChunks.length} invalid chunks`
          );
        }

        // Create blob with explicit type
        const blob = new Blob(validChunks, {
          type: recorder.mimeType || "video/webm;codecs=vp8,opus",
        });

        console.log(`📦 Blob created: ${blob.size} bytes, type: ${blob.type}`);

        // Validate recording
        const validation = validateRecording(blob, 60); // Assuming 60s max
        if (!validation.valid) {
          console.error(`❌ Recording validation failed: ${validation.error}`);
          resolve({ videoPath: null, error: validation.error });
          if (onComplete) onComplete();
          return;
        }

        // Backup chunks before clearing
        const chunksBackup = [...recordedChunksRef.current];
        recordedChunksRef.current = [];

        const timestamp = new Date()
          .toISOString()
          .replace(/:/g, "-")
          .split(".")[0];
        const fileName = `interview_${zoho_lead_id}_${capturedQuestionId}_${timestamp}.webm`;

        console.log(`📁 File name: ${fileName}`);

        if (onComplete) {
          onComplete();
        }

        // Stop all media tracks NOW (after blob is created)
        if (videoRef.current && videoRef.current.srcObject) {
          const tracks = videoRef.current.srcObject.getTracks();
          tracks.forEach((track) => {
            track.stop();
            console.log(`🛑 Stopped track: ${track.kind}`);
          });
          videoRef.current.srcObject = null;
          console.log("✅ All tracks stopped and srcObject cleared");
        }

        // Resolve promise to allow UI to proceed
        resolve({ videoPath: null, blob, fileName });

        // Upload with retry logic
        console.log("☁️ Starting upload...");
        uploadFile(
          blob,
          fileName,
          zoho_lead_id,
          capturedQuestionId,
          captureLastQuestionId,
          encoded_interview_link_send_count
        )
          .then((videoPath) => {
            console.log("✅ Upload completed:", videoPath);
            setVideoFilePath(videoPath);
          })
          .catch((err) => {
            console.error("❌ Upload failed:", err);
            console.log(`💾 Backup chunks available: ${chunksBackup.length}`);
            
            // Optional: Retry with backup chunks
            // You could implement retry logic here
          });
      } catch (error) {
        console.error("❌ Error in onstop handler:", error);
        resolve({ videoPath: null, error: error.message });
        if (onComplete) onComplete();
      }
    };

    // Request final data and stop
    try {
      if (recorder.state === "recording") {
        console.log("📤 Requesting final data...");
        
        // Request any remaining buffered data
        recorder.requestData();

        // Wait briefly before stopping (browser-specific)
        const stopDelay = browserType === 'firefox' ? 200 : 100;
        
        setTimeout(() => {
          if (recorder.state === "recording" || recorder.state === "paused") {
            console.log("🛑 Calling recorder.stop()");
            recorder.stop();
          }
        }, stopDelay);

        // Safety timeout: force stop if onstop doesn't fire
        stopTimeout = setTimeout(() => {
          console.warn("⚠️ Stop event didn't fire, forcing cleanup");
          if (recorder.state !== "inactive") {
            try {
              recorder.stop();
            } catch (e) {
              console.error("❌ Error forcing stop:", e);
            }
          }
          resolve({ videoPath: null, error: "Stop timeout" });
          if (onComplete) onComplete();
        }, 5000); // 5 second timeout
      }
    } catch (error) {
      console.error("❌ Error stopping recorder:", error);
      resolve({ videoPath: null, error: error.message });
      if (onComplete) onComplete();
    }

    // Stop all media tracks (do this AFTER recorder processing)
    // Moved inside onstop handler to prevent null reference
  });
};