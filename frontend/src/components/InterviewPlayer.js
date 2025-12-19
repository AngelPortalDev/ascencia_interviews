import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import InterviewScoreModal from "./InterviewScoreModal.js";
import { startRecording, stopRecording } from "../utils/recording.js";
import { interviewAddVideoPath } from "../utils/fileUpload.js";
import useVisibilityWarning from "../hooks/useVisibilityWarning.js";


const InterviewPlayer = ({videoRef,mediaRecorderRef,audioRecorderRef,recordedChunksRef,recordedAudioChunksRef,zoho_lead_id,question_id,last_question_id,encoded_interview_link_send_count,}) => {
  const [showPopup, setShowPopup] = useState(false);
  const [answerScore, setAnswerScore] = useState(null);
  console.log("zoho_lead_idcxgxf",btoa(zoho_lead_id));
  const encoded_zoho_lead_id = btoa(zoho_lead_id)
  const navigate = useNavigate();

  const handleCloseModal = () => {
    setShowPopup(false);
  };

  // Switch Tab Warning
  // useVisibilityWarning(encoded_zoho_lead_id, encoded_interview_link_send_count);

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
