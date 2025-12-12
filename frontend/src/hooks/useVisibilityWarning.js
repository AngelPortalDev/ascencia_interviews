import { useEffect } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import {showWarningToast} from '../utils/toastNotifications.js';

const useVisibilityWarning = (encoded_zoho_lead_id, encoded_interview_link_send_count) => {
  const navigate = useNavigate();
  
  useEffect(() => {
    

    const handleChangeVisibility = () => {
      if (document.hidden) {
        let warningCount = localStorage.getItem("tabSwitchWarning") || 0;
        const currentIndex = parseInt(sessionStorage.getItem("currentQuestionIndex"), 10);
        warningCount++;
        localStorage.setItem("tabSwitchWarning", warningCount);

        if(warningCount<3){
          showWarningToast(`Warning ${warningCount}/2: Tab switch detected.`, {
                  position: "top-center",
                  autoClose: 3000,
                  hideProgressBar: true,
          });
        }
        if (warningCount > 2) {
          toast.error("Interview auto-submitted due to rule violation.", {
            position: "top-center",
            autoClose: 3000,
            hideProgressBar: true,
            onClose: () =>{
              if (currentIndex === 0 || isNaN(currentIndex)) {
                navigate('/goback');
              }else{
                localStorage.clear();
                sessionStorage.clear();
                navigate(`/interviewsubmitted?lead=${encoded_zoho_lead_id}&link=${encoded_interview_link_send_count}&reason=TAB_SWITCH_EXCEEDED`);
              }
            } 
          });
        }
      }
    };

    document.addEventListener("visibilitychange", handleChangeVisibility);
    return () => {
      document.removeEventListener("visibilitychange", handleChangeVisibility);
    };
  }, [navigate, encoded_zoho_lead_id, encoded_interview_link_send_count]);
};

export default useVisibilityWarning;
