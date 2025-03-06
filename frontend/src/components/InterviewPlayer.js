import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import InterviewScoreModal from "./InterviewScoreModal.js";
import { startRecording, stopRecording } from "../utils/recording.js";
import { interviewAddVideoPath } from "../utils/fileUpload.js";
import useVisibilityWarning from "../hooks/useVisibilityWarning.js";


const InterviewPlayer = ({ onTranscription,zoho_lead_id,question_id,last_question_id}) => {
  const [isRecording, setIsRecording] = useState(false);
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



  // useEffect(() => {
  //   const startNewRecording = () => {
  //     startRecording(
  //       videoRef,
  //       mediaRecorderRef,
  //       audioRecorderRef,
  //       recordedChunksRef,
  //       recordedAudioChunksRef,
  //       () => {},
  //       setIsRecording,
  //       setVideoFilePath,
  //       setAudioFilePath,
  //       student_id,
  //       question_id
  //     );
  //   }
  //   startNewRecording();

  //   if (localStorage.getItem("interviewExited") === "true") {
  //     const stopTimeout = setTimeout(() => {
  //       stopRecording(
  //         videoRef,
  //         mediaRecorderRef,
  //         audioRecorderRef,
  //         recordedChunksRef,
  //         recordedAudioChunksRef,
  //         setVideoFilePath,
  //         setAudioFilePath,
  //         student_id,
  //         question_id,
  //         startNewRecording 
  //       );
  //       // stopMediaStreams();
  //       // navigate("/");
       
  //     },60000)
     
  //   }

  //   // Prevent Back Button & Refresh
  //   const handleBackButton = (event) => {
  //     event.preventDefault();

  //     const confirmLeave = window.confirm(
  //       "You will lose your progress if you go back. Do you want to continue?"
  //     );
  //     if (confirmLeave) {
  //       localStorage.setItem("interviewExited", "true");
  //       navigate("/");
  //     } else {
  //       window.history.pushState(null, "", window.location.href);
  //     }
  //     // alert("You cannot go back during the interview. Please complete it.");
  //   };
  //   window.history.pushState(null, "", window.location.href);
  //   window.addEventListener("popstate", handleBackButton);

  //   // Stop recording after 2 minutes
  //   // const stopTimeout = setTimeout(() => {
  //   //   stopRecording(
  //   //     videoRef,
  //   //     mediaRecorderRef,
  //   //     audioRecorderRef,
  //   //     recordedChunksRef,
  //   //     recordedAudioChunksRef,
  //   //     setVideoFilePath,
  //   //     setAudioFilePath,
  //   //     student_id,
  //   //     question_id
  //   //   );
  //   //   // stopMediaStreams();
  //   //   // showSuccessToast("Interview Submitted Successfully...")
  //   //   // navigate("/");
  //   // },10000);

  //   return () => {
  //     // clearInterval(questionInterval);
  //     clearTimeout(stopTimeout);
  //     window.removeEventListener("popstate", handleBackButton);
  //   };
  // }, []);

  // Analayze Video

  useEffect(() => {
    if (videoFilePath && audioFilePath) {
      console.log("video path get Interview player",last_question_id);

      interviewAddVideoPath(videoFilePath, audioFilePath,zoho_lead_id,question_id,last_question_id);
    }
  }, [videoFilePath, audioFilePath,last_question_id,zoho_lead_id,question_id]);

  useEffect(() => {

  //   if (!question_id) {
  //     console.error('question_id is not defined');
  //     return;
  //   }
  // console.log("Inyterview Player start recording",last_question_id);


    const startNewRecording = () => {
      startRecording(
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
      );
    };
  
    startNewRecording();

    const stopTimeout = setTimeout(() => {

        // console.log("Inyterview Player stop recording",last_question_id);
      
      stopRecording(
        videoRef,
        mediaRecorderRef,
        audioRecorderRef,
        recordedChunksRef,
        recordedAudioChunksRef,
        setVideoFilePath,
        setAudioFilePath,
        zoho_lead_id,
        question_id,
        startNewRecording,
        last_question_id
      );
    }, 60000); // 10 seconds per question
  
    return () => clearTimeout(stopTimeout);
  }, [question_id,last_question_id,zoho_lead_id]); 
  

  const handleCloseModal = () => {
    setShowPopup(false);
  };

  // Switch Tab Warning
  useVisibilityWarning();

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
