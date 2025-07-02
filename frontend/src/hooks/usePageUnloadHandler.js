// import { useEffect } from "react";
// import { usePermission } from "../context/PermissionContext.js";

// const usePageUnloadHandler = (encoded_zoho_lead_id, encoded_interview_link_send_count) => {
//   const { submitExam } = usePermission();



//   console.log("zoho_lead_id",encoded_zoho_lead_id)
//   console.log("encoded_interview_link_send_count",encoded_interview_link_send_count)
//   useEffect(() => {
//     const handleBeforeUnload = (event) => {
//       sessionStorage.setItem("isPageRefreshing", "true");

//       // ✅ Store values for access after reload
//       sessionStorage.setItem("zoho_lead_id", encoded_zoho_lead_id || "");
//       sessionStorage.setItem("interview_link_count", encoded_interview_link_send_count || "");


//       // ❌ Avoid async in beforeunload — browser will ignore it
//       console.log("🔄 Before unload triggered");
//       event.preventDefault();
//       event.returnValue = "";
//     };

//     const handlePageLoad = () => {
//       if (sessionStorage.getItem("isPageRefreshing") === "true") {
//         sessionStorage.removeItem("isPageRefreshing");

//         // ✅ Safely submit now after reload
//         submitExam();

//         // Clear saved state
//         localStorage.clear();
//         sessionStorage.removeItem("timeSpent");
//         sessionStorage.removeItem("currentQuestionIndex");

//         const lead = sessionStorage.getItem("zoho_lead_id");
//         const link = sessionStorage.getItem("interview_link_count");

//         // ✅ Redirect with stored query params
//         window.location.href = `/frontend/interviewsubmitted?lead=${lead}&link=${link}`;
//       }
//     };

//     window.addEventListener("beforeunload", handleBeforeUnload);
//     window.addEventListener("load", handlePageLoad);

//     return () => {
//       window.removeEventListener("beforeunload", handleBeforeUnload);
//       window.removeEventListener("load", handlePageLoad);
//     };
//   }, [encoded_zoho_lead_id, encoded_interview_link_send_count, submitExam]);
// };

import { useEffect } from "react";
import { usePermission } from "../context/PermissionContext.js";
import { useNavigate } from "react-router-dom";

const usePageUnloadHandler = (encoded_zoho_lead_id, encoded_interview_link_send_count) => {
  const { submitExam } = usePermission();
  const navigate = useNavigate();

  // ✅ Save info during unload
  useEffect(() => {
    const handleBeforeUnload = (event) => {
      if (encoded_zoho_lead_id && encoded_interview_link_send_count) {
        sessionStorage.setItem("zoho_lead_id", encoded_zoho_lead_id);
        sessionStorage.setItem("interview_link_count", encoded_interview_link_send_count);
        sessionStorage.setItem("isPageRefreshing", "true");
      }

      event.preventDefault();
      event.returnValue = "";
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [encoded_zoho_lead_id, encoded_interview_link_send_count]);

  // ✅ On reload, get values directly from sessionStorage
  useEffect(() => {
    const isRefresh = sessionStorage.getItem("isPageRefreshing") === "true";
    const lead = sessionStorage.getItem("zoho_lead_id");
    const link = sessionStorage.getItem("interview_link_count");

    if (isRefresh && lead && link) {
      sessionStorage.removeItem("isPageRefreshing");
      sessionStorage.removeItem("timeSpent");
      sessionStorage.removeItem("currentQuestionIndex");

      submitExam(); // This will submit using the stored IDs
      navigate(`/frontend/interviewsubmitted?lead=${lead}&link=${link}`);
      // sessionStorage.removeItem("interviewSubmitted");
      // localStorage.clear()
      // sessionStorage.clear()
    }
  }, [submitExam, navigate]);
};

export default usePageUnloadHandler;
