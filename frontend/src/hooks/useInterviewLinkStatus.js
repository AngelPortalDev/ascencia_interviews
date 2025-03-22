import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const useInterviewLinkStatus = (encoded_zoho_lead_id) => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkInterviewStatus = async () => {
      if (!encoded_zoho_lead_id) return;

      const formData = new FormData();
      formData.append("zoho_lead_id", encoded_zoho_lead_id);

      try {
        const response = await axios.post(
          `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-attend-status/`,
          formData
        );

        if (response.status === 200) {
          console.log("Interview link is valid. Proceeding...");
        }
      } catch (error) {
        if (error.response && error.response.status === 410) {
          console.log("Interview link has expired. Redirecting to expired page...");
          navigate("/expired");
        } else {
          console.error("An error occurred while checking the interview link status:", error);
        }
      } finally {
        setIsLoading(false); // Finish loading
      }
    };

    checkInterviewStatus();
  }, [encoded_zoho_lead_id, navigate]);

  return isLoading; // Return loading state
};

export default useInterviewLinkStatus;
