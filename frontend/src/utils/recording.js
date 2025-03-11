// utils/recording.js

import { uploadFile, downloadFile } from "./fileUpload.js";
export const startRecording = async (
  videoRef,
  mediaRecorderRef,
  audioRecorderRef,
  recordedChunksRef,
  recordedAudioChunksRef,
  setIsRecording,
  setVideoFilePath,
  setAudioFilePath,
  zoho_lead_id,
  question_id,
  last_question_id
) => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: { noiseSuppression: false, echoCancellation: false },
    });

    // Video recording setup
    mediaRecorderRef.current = new MediaRecorder(stream, {
      audioBitsPerSecond: 128000,
      videoBitsPerSecond: 2500000,
      type: "video/webm;codecs=vp8,opus",
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

    audioRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) recordedAudioChunksRef.current.push(event.data);
    };
    audioRecorderRef.current.start();

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
  onRecordingComplete,
  last_question_id
) => {
  // Stop video and audio recording, process the files, and upload them

  if (mediaRecorderRef.current) {
    mediaRecorderRef.current.stop();
    mediaRecorderRef.current.onstop = () => {
      const videoBlob = new Blob(recordedChunksRef.current, {
        type: "video/webm",
      });
      const fileNameVideo = `interview_video_${zoho_lead_id}_${question_id}_${
        new Date().toISOString().replace(/:/g, "-").split(".")[0]
      }.webm`;
      // downloadFile(videoBlob, fileNameVideo);

      // console.log("stopRecording",last_question_id);

      uploadFile(
        videoBlob,
        fileNameVideo,
        zoho_lead_id,
        question_id,
        last_question_id
      ).then(setVideoFilePath);
      recordedChunksRef.current = [];
    };
  }

  if (audioRecorderRef.current) {
    audioRecorderRef.current.stop();
    audioRecorderRef.current.onstop = () => {
      const audioBlob = new Blob(recordedAudioChunksRef.current, {
        type: "audio/mp3",
      });
      const fileNameAudio = `interview_audio_${zoho_lead_id}_${question_id}_${
        new Date().toISOString().replace(/:/g, "-").split(".")[0]
      }.mp3`;
      // downloadFile(audioBlob, fileNameAudio);
      uploadFile(audioBlob, fileNameAudio, zoho_lead_id, question_id).then(
        setAudioFilePath
      );
      recordedAudioChunksRef.current = [];
    };
  }

  // Stop media tracks
  // const tracks = videoRef.current.srcObject.getTracks();
  // tracks.forEach((track) => track.stop());
  // videoRef.current.srcObject = null;

  // ✅ Stop all media tracks before starting new recording
  if (videoRef.current && videoRef.current.srcObject) {
    // console.log("srcObject Video", videoRef.current.srcObject);
    // console.log("srcObject current", videoRef.current);

    const tracks = videoRef.current.srcObject.getTracks();
    tracks.forEach((track) => {
      track.stop();
    });
    videoRef.current.srcObject = null;
  }
  setTimeout(() => {
    // onRecordingComplete();
    if (typeof onRecordingComplete === "function") {
      onRecordingComplete();
    } else {
      console.warn("onRecordingComplete is not a function.");
    }
  }, 500);
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

