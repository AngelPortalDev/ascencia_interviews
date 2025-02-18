import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from 'axios';
const InterviewPlayer = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showPopup, setShowPopup] = useState(false);
  const [answerScore, setAnswerScore] = useState(null);
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
    startRecording();

    // Prevent Back Button & Refresh
    const handleBackButton = (event) => {
      event.preventDefault();
      console.log("test")
      alert("You cannot go back during the interview. Please complete it.");
      window.history.pushState(null, "", window.location.href);
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
    }, 12000);

    return () => {
      clearInterval(questionInterval);
      clearTimeout(stopTimeout);
      window.removeEventListener("popstate", handleBackButton);
    };
  }, []);


  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });

      // Video recording
      mediaRecorderRef.current = new MediaRecorder(stream);
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) recordedChunksRef.current.push(event.data);
      };
      mediaRecorderRef.current.start();

      // Audio-only recording
      const audioStream = new MediaStream(stream.getAudioTracks());
      audioRecorderRef.current = new MediaRecorder(audioStream);
      audioRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) recordedAudioChunksRef.current.push(event.data);
      };
      audioRecorderRef.current.start();

      if (videoRef.current) videoRef.current.srcObject = stream;
      setIsRecording(true);
    } catch (error) {
      alert("Error accessing camera and microphone.");
    }
  };


  const stopRecording = () => {
    setIsRecording(false);

    // Stop and process video recording
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.onstop = () => {
        const videoBlob = new Blob(recordedChunksRef.current, { type: "video/webm" });
        console.log("testmnhhfdsjf")
        downloadFile(videoBlob, "interview_video.webm");
        uploadFile(videoBlob, 'interview_video.webm');
        // convertToAudio(videoBlob);
      };
    }

    // Stop and process audio recording separately
    if (audioRecorderRef.current) {
      audioRecorderRef.current.stop();
      audioRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(recordedAudioChunksRef.current, { type: "audio/mp3" });
        downloadFile(audioBlob, "interview_audio.mp3");
        uploadFile(audioBlob, 'interview_audio.mp3');

      };
    }

    // Simulate answer score calculation
    const calculatedScore = Math.floor(Math.random() * 100);
    setAnswerScore(calculatedScore);
    setShowPopup(true);
    console.log("testsdadsa")

    // Redirect to home after 5 seconds
    setTimeout(() => navigate("/home"), 5000);
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
  const uploadFile = async (blob, filename) => {
    const formData = new FormData();
    formData.append('file', blob, filename);
  
    // try {
      const response = await axios.post('https://192.168.1.9:5000/interveiw-section/interview-video-upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('File uploaded successfully:', response);
    // } catch (error) {
    //   console.error('Error uploading file:', error);
    // }
  };
  
  return (

    <div  style={{   position:'absolute', bottom: 0,right: 0 }}>

      <h2>Interview in Progress</h2>

      {/* Video Preview */}
      <video ref={videoRef} autoPlay playsInline style={{ width: "50%", borderRadius: "10px" }}></video>

      {/* Scrolling Questions */}
     

      {/* Popup Message */}
      {showPopup && (
        <div style={{ marginTop: "20px", fontSize: "18px", color: "green", fontWeight: "bold" }}>
          <p>Your interview has been submitted.</p>
          <p>Your score: {answerScore}%</p>
          <p>You will receive feedback soon.</p>
          <p>Redirecting to home...</p>
        </div>
      )}
    </div>
  );
};

export default InterviewPlayer;
