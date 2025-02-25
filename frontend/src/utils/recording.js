// utils/recording.js
import {uploadFile,downloadFile} from './fileUpload.js';

export const startRecording = async (videoRef, mediaRecorderRef, audioRecorderRef, recordedChunksRef, recordedAudioChunksRef, setIsRecording, setVideoFilePath, setAudioFilePath) => {
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
  
  export const stopRecording = (videoRef, mediaRecorderRef, audioRecorderRef, recordedChunksRef, recordedAudioChunksRef, setVideoFilePath, setAudioFilePath) => {
    // Stop video and audio recording, process the files, and upload them
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.onstop = () => {
        const videoBlob = new Blob(recordedChunksRef.current, { type: "video/webm" });
        const fileNameVideo = `interview_video_${new Date().toISOString().replace(/:/g, "-").split(".")[0]}.webm`;
        downloadFile(videoBlob, fileNameVideo);
        uploadFile(videoBlob, fileNameVideo).then(setVideoFilePath);
      };
    }
  
    if (audioRecorderRef.current) {
      audioRecorderRef.current.stop();
      audioRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(recordedAudioChunksRef.current, { type: "audio/mp3" });
        const fileNameAudio = `interview_audio_${new Date().toISOString().replace(/:/g, "-").split(".")[0]}.mp3`;
        downloadFile(audioBlob, fileNameAudio);
        uploadFile(audioBlob, fileNameAudio).then(setAudioFilePath);
      };
    }
  
    // Stop media tracks
    const tracks = videoRef.current.srcObject.getTracks();
    tracks.forEach((track) => track.stop());
    videoRef.current.srcObject = null;
  };


  