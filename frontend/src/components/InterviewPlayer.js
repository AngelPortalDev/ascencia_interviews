import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import InterviewScoreModal from "./InterviewScoreModal.js";
import { startRecording, stopRecording } from "../utils/recording.js";
import { interviewAddVideoPath } from "../utils/fileUpload.js";
import useVisibilityWarning from "../hooks/useVisibilityWarning.js";


const InterviewPlayer = ({videoRef,mediaRecorderRef,audioRecorderRef,recordedChunksRef,recordedAudioChunksRef,zoho_lead_id,question_id,last_question_id,encoded_interview_link_send_count,}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [answerScore, setAnswerScore] = useState(null);
  const [videoFilePath, setVideoFilePath] = useState(null);
  const [audioFilePath, setAudioFilePath] = useState(null);
  console.log("zoho_lead_idcxgxf",btoa(zoho_lead_id));
  const encoded_zoho_lead_id = btoa(zoho_lead_id)
  // const videoRef = useRef(null);
  // const mediaRecorderRef = useRef(null);gbfxc g
  // const recordedChunksRef = useRef([]);
  // const audioRecorderRef = useRef(null);
  // const recordedAudioChunksRef = useRef([]);
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

  // useEffect(() => {
  //   if (videoFilePath && audioFilePath) {
  //     console.log("video path get Interview player",last_question_id);

  //     interviewAddVideoPath(videoFilePath, audioFilePath,zoho_lead_id,question_id,last_question_id);
  //   }
  // }, [videoFilePath, audioFilePath,last_question_id,zoho_lead_id,question_id]);

  // useEffect(() => {

  //   const startNewRecording = () => {
  //     startRecording(
  //       videoRef,
  //       mediaRecorderRef,
  //       audioRecorderRef,
  //       recordedChunksRef,
  //       recordedAudioChunksRef,
  //       setIsRecording,
  //       setVideoFilePath,
  //       setAudioFilePath,
  //       zoho_lead_id,
  //       question_id,
  //       last_question_id,
  //       encoded_interview_link_send_count,
  //     );
  //   };
  
  //   startNewRecording();

  //   const stopTimeout = setTimeout(() => {
  //     stopRecording(
  //       videoRef,
  //       mediaRecorderRef,
  //       audioRecorderRef,
  //       recordedChunksRef,
  //       recordedAudioChunksRef,
  //       setVideoFilePath,
  //       setAudioFilePath,
  //       zoho_lead_id,
  //       question_id,
  //       last_question_id,
  //       encoded_interview_link_send_count,
  //     );
  //   }, 60000); // 10 seconds per question
  
  //   return () => clearTimeout(stopTimeout);
  // }, [videoRef,question_id,last_question_id,zoho_lead_id,audioRecorderRef,mediaRecorderRef,recordedAudioChunksRef,recordedChunksRef]); 
  

  const handleCloseModal = () => {
    setShowPopup(false);
  };

  // Switch Tab Warning
  useVisibilityWarning(encoded_zoho_lead_id, encoded_interview_link_send_count);

  return (
    <div>
      {/* <div  style={{   position:'absolute', bottom: 0,right: 0 }}></div> */}
      {/* <h2>Interview in Progress</h2> */}

      {/* Video Preview */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
          style={{ display:'block', margin:'0 auto', borderRadius:'10px',width:'300px', height:'250px', objectFit:'cover'}}      ></video>

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
