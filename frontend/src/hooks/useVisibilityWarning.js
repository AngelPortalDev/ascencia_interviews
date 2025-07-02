import { useEffect } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import {showWarningToast, showErrorToast} from '../utils/toastNotifications.js';

const useVisibilityWarning = (encoded_zoho_lead_id, encoded_interview_link_send_count) => {
  const navigate = useNavigate();
  
  useEffect(() => {
    let warningCount = localStorage.getItem("tabSwitchWarning") || 0;

    const handleChangeVisibility = () => {
      if (document.hidden) {
        warningCount++;
        localStorage.setItem("tabSwitchWarning", warningCount);

        showWarningToast(`Warning ${warningCount}/3: Tab switch detected.`, {
          position: "top-center",
          autoClose: 3000,
          hideProgressBar: true,
        });

        if (warningCount >= 3) {
          toast.error("Interview auto-submitted due to rule violation.", {
            position: "top-center",
            autoClose: 3000,
            hideProgressBar: true,
            onClose: () =>{
              localStorage.clear();
              // localStorage.setItem("interviewSubmitted", "true"); 
              sessionStorage.clear();
              navigate(`/interviewsubmitted?lead=${encoded_zoho_lead_id}&link=${encoded_interview_link_send_count}`);
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
