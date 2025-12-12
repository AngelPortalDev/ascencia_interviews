import { useEffect,useRef } from "react";
import { useNavigate,useLocation } from "react-router-dom";
import axios from "axios";

const InterviewSubmitted = () => {
  const navigate = useNavigate();
    const { search } = useLocation();
  const params = new URLSearchParams(search);
  // const zoho_lead_id = params.get("lead");
  // const interview_link_count  = params.get("link");
  const zoho_lead_id = params.get("lead") || sessionStorage.getItem("zoho_lead_id");
  const interview_link_count  = params.get("link") || sessionStorage.getItem("interview_link_count");
  const reason = params.get("reason") || "NORMAL_SUBMISSION";

  console.log("zoho_lead_id",zoho_lead_id)
  console.log("interview_link_count",interview_link_count)
 const videoRef = useRef(null);
  useEffect(() => {


    // Disable back button
    const blockBackNavigation = () => {
      window.history.pushState(null, "", window.location.href);
    };

    blockBackNavigation(); // Call once
    window.addEventListener("popstate", blockBackNavigation);

    return () => {
      window.removeEventListener("popstate", blockBackNavigation);
    };
  }, [navigate,videoRef]);

  useEffect(() => {
    // Check if the page has already reloaded once
    if (!sessionStorage.getItem("hasPageReloadedOnce")) {
      sessionStorage.setItem("hasPageReloadedOnce", "true"); 
      setTimeout(() => {
        window.location.reload(); 
      }, 0); 
    }
  }, []);

//   useEffect(() => {
//   const wasAutoSubmitted = localStorage.getItem("interviewSubmitted") === "true";
//   console.log("📝 Was auto-submitted due to tab switching?", wasAutoSubmitted);
// }, []);


 useEffect(() => {
    const sendFinalInterviewSubmission = async () => {
      if (!zoho_lead_id) {
        console.warn("❌ No zoho_lead_id found");
        return;
      }

      try {
        const response = await axios.post(
          `${process.env.REACT_APP_API_BASE_URL}submit_interview/`,
          {
            zoho_lead_id,
            interview_link_count: interview_link_count || "",
            is_interview_submitted: true, 
            submission_reason: reason, 
          },
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        console.log("✅ Interview submitted:", response.data);
        localStorage.clear();
      sessionStorage.clear();

      } catch (error) {
        console.error("❌ API submission failed:", error);
      }
    };

    sendFinalInterviewSubmission();
  }, [zoho_lead_id, interview_link_count]);

  return (
    <div className="submitted-container">
      <div className="submitted-content">
        <h1 className="submitted-title">✔</h1>
        <p className="submitted-message">Thank you for your submission!</p>
        <p className="submitted-subtext">Thank you for completing the interview. Your result will be provided within 48 hours.</p>
        {/* <a href="/" className="bg-[rgb(219,39,131)] text-white rounded-md text-sm px-4 py-2 md:text-lg md:px-6 md:py-3">
                Go Back to Home
        </a> */}
      </div>
  </div>
  );
};

export default InterviewSubmitted;
