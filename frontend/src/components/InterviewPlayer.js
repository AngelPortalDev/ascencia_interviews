import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import InterviewScoreModal from "./InterviewScoreModal.js";

const InterviewPlayer = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showPopup, setShowPopup] = useState(false);
  const [answerScore, setAnswerScore] = useState(null);
  const [videoFilePath, setVideoFilePath] = useState(null);
  const [audioFilePath, setAudioFilePath] = useState(null);
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const audioRecorderRef = useRef(null);
  const recordedAudioChunksRef = useRef([]);
  const navigate = useNavigate();

  const questions = [
    "Tell me about yourself.",
    "What are your strengths and weaknesses?",
    "Why do you want this job?",
    "Where do you see yourself in 5 years?",
    "What are your biggest achievements?",
  ];

  useEffect(() => {
    if (localStorage.getItem("interviewExited") === "true") {
      stopMediaStreams();
      navigate("/");
      return;
    }

    startRecording();

    // Prevent Back Button & Refresh
    const handleBackButton = (event) => {
      event.preventDefault();

      const confirmLeave = window.confirm(
        "You will lose your progress if you go back. Do you want to continue?"
      );
      if (confirmLeave) {
        localStorage.setItem("interviewExited", "true");
        navigate("/");
      } else {
        window.history.pushState(null, "", window.location.href);
      }
      // alert("You cannot go back during the interview. Please complete it.");
    };
    window.history.pushState(null, "", window.location.href);
    window.addEventListener("popstate", handleBackButton);

    // Auto-scroll questions every 20 seconds
    const questionInterval = setInterval(() => {
      setCurrentQuestionIndex((prevIndex) =>
        prevIndex < questions.length - 1 ? prevIndex + 1 : prevIndex
      );
    }, 20000);

    // Stop recording after 2 minutes
    const stopTimeout = setTimeout(() => {
      stopRecording();
    }, 17000);

    return () => {
      clearInterval(questionInterval);
      clearTimeout(stopTimeout);
      window.removeEventListener("popstate", handleBackButton);
    };
  }, []);

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: { noiseSuppression: false, echoCancellation: false },
      });

      // Video recording
      mediaRecorderRef.current = new MediaRecorder(stream, {
        audioBitsPerSecond: 128000,
        videoBitsPerSecond: 2500000,
        type: "video/webm;codecs=vp8,opus",
      });
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) recordedChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.start();

      // Audio-only recording
      const audioStream = new MediaStream(stream.getAudioTracks());
      audioRecorderRef.current = new MediaRecorder(audioStream, {
        audioBitsPerSecond: 128000,
        mimeType: "audio/webm",
      });
      audioRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0)
          recordedAudioChunksRef.current.push(event.data);
      };
      audioRecorderRef.current.start();

      if (videoRef.current) videoRef.current.srcObject = stream;
      setIsRecording(true);
    } catch (error) {
      alert("Error accessing camera and microphone.");
    }
  };

  // Stop Recording

  const stopRecording = () => {
    setIsRecording(false);

    // Stop and process video recording
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.onstop = () => {
        const videoBlob = new Blob(recordedChunksRef.current, {
          type: "video/webm",
        });
        const now = new Date().toISOString().replace(/:/g, "-").split(".")[0]; // Format the timestamp
        const fileNameVideo = `interview_video_${now}.webm`; // Use formatted time in filename
        // const videoPath = uploadFile(videoBlob, fileNameVideo);

        const handleFileUpload = async () => {
          try {
            const videoPath = await uploadFile(videoBlob, fileNameVideo);
            console.log("Audio file path:", videoPath);
            setVideoFilePath(videoPath);

            // You can now use audioPath as needed
          } catch (error) {
            console.error("Failed to upload audio file:", error);
          }
        };
        
        // Ensure that handleFileUpload is called in an appropriate context

   


        handleFileUpload();

        // console.log(videoPath,"sdssd video file")

        // downloadFile(videoBlob, fileNameVideo);
        // convertToAudio(videoBlob);
        console.log("test audio path  sdnasjsajdsmsm");

        // Video Stop After Time Complete
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
        videoRef.current.srcObject = null;
      };
    }

    // Stop and process audio recording separately
    if (audioRecorderRef.current) {
      audioRecorderRef.current.stop();
      audioRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(recordedAudioChunksRef.current, {
          type: "audio/mp3",
        });
        const now = new Date().toISOString().replace(/:/g, "-").split(".")[0]; // Format the timestamp
        const fileNameAudio = `interview_audio_${now}.mp3`; // Use formatted time in filename
        // downloadFile(audioBlob, fileNameAudio);
        // const audioPath = uploadFile(audioBlob, fileNameAudio);

        // console.log(audioPath,"sdssd audio file")
        //  console.log("test audio path");

        // setAudioFilePath(audioPath);

        const handleFileUploadAudio = async () => {
          try {
            const audioPath = await uploadFile(audioBlob, fileNameAudio);
            console.log("Audio file path:", audioPath);
            setAudioFilePath(audioPath);

            // You can now use audioPath as needed
          } catch (error) {
            console.error("Failed to upload audio file:", error);
          }
        };
        handleFileUploadAudio()

      };
    }
    // Simulate answer score calculation
    const calculatedScore = Math.floor(Math.random() * 100);
    setAnswerScore(calculatedScore);
    setShowPopup(true);
    console.log("testsdadsa");

    // Redirect to home after 5 seconds
    // setTimeout(() => navigate("/home"), 5000);
  };

  // Stop and process audio recording once go Home Page
  const stopMediaStreams = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }

    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }

    if (audioRecorderRef.current) {
      audioRecorderRef.current.stop();
    }

    console.log("Camera & microphone stopped.");
  };

  // const convertToAudio = (videoBlob) => {
  //   const audioContext = new AudioContext();
  //   const reader = new FileReader();

  //   reader.readAsArrayBuffer(videoBlob);
  //   reader.onloadend = async () => {
  //     const audioBuffer = await audioContext.decodeAudioData(reader.result);
  //     const wavBlob = await encodeWAV(audioBuffer);
  //     downloadFile(wavBlob, "interview_audio.mp3");
  //   };
  // };

  // const encodeWAV = async (audioBuffer) => {
  //   const numOfChannels = audioBuffer.numberOfChannels;
  //   const sampleRate = audioBuffer.sampleRate;
  //   const length = audioBuffer.length * numOfChannels * 2 + 44;
  //   const buffer = new ArrayBuffer(length);
  //   const view = new DataView(buffer);

  //   // WAV Header
  //   writeString(view, 0, "RIFF");
  //   view.setUint32(4, 36 + audioBuffer.length * 2, true);
  //   writeString(view, 8, "WAVE");
  //   writeString(view, 12, "fmt ");
  //   view.setUint32(16, 16, true);
  //   view.setUint16(20, 1, true);
  //   view.setUint16(22, numOfChannels, true);
  //   view.setUint32(24, sampleRate, true);
  //   view.setUint32(28, sampleRate * numOfChannels * 2, true);
  //   view.setUint16(32, numOfChannels * 2, true);
  //   view.setUint16(34, 16, true);
  //   writeString(view, 36, "data");
  //   view.setUint32(40, audioBuffer.length * 2, true);

  //   // PCM Data
  //   const offset = 44;
  //   for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
  //     const channelData = audioBuffer.getChannelData(i);
  //     for (let j = 0; j < channelData.length; j++) {
  //       view.setInt16(offset + (j * 2), channelData[j] * 0x7FFF, true);
  //     }
  //   }

  //   return new Blob([buffer], { type: "audio/mp3" });
  // };

  // const writeString = (view, offset, string) => {
  //   for (let i = 0; i < string.length; i++) {
  //     view.setUint8(offset + i, string.charCodeAt(i));
  //   }
  // };



  // Download the File

  const downloadFile = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Upload the File In the Server
  const uploadFile = async (blob, filename) => {
    const formData = new FormData();
    formData.append("file", blob, filename);

    // try {
    const response = await axios.post(
      "https://192.168.1.63:5000/interveiw-section/interview-video-upload/",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data.file_path;
  };

  useEffect(() => {
    if (videoFilePath && audioFilePath) {
      console.log("test video path");
      console.log(videoFilePath);
      console.log(audioFilePath,"AUdioFile Path....");

      analyzeVideo();
    }
  }, [videoFilePath, audioFilePath]);

  const analyzeVideo = async () => {
    if (!videoFilePath || !audioFilePath) {
      console.error("Video or audio path is missing.");
      return;
    }

    const formData = new FormData();
    formData.append("video_path", videoFilePath);
    formData.append("audio_path", audioFilePath);

    try {
      const response = await axios.post(
        "https://192.168.1.63:5000/interveiw-section/analyze-video/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log("Video analysis started successfully:", response.data);
    } catch (error) {
      console.error("Error analyzing video:", error);
    }
  };

  const handleCloseModal = () => {
    setShowPopup(false);
  };

  return (
    <div>
      {/* <div  style={{   position:'absolute', bottom: 0,right: 0 }}></div> */}
      {/* <h2>Interview in Progress</h2> */}

      {/* Video Preview */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{ width: "100%", borderRadius: "10px" }}
      ></video>

      {/* Scrolling Questions */}

      {/* Popup Message */}
      {showPopup && (
        <InterviewScoreModal
          showPopup={showPopup}
          answerScore={answerScore}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default InterviewPlayer;
