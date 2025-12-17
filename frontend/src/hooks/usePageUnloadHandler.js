/* eslint-disable react-hooks/exhaustive-deps */
// import { useEffect } from "react";
// import { usePermission } from "../context/PermissionContext.js";
// import { useNavigate } from "react-router-dom";

// const usePageUnloadHandler = (encoded_zoho_lead_id, encoded_interview_link_send_count) => {
//   const { submitExam } = usePermission();
//   const navigate = useNavigate();

//   // ✅ Save info during unload
//   useEffect(() => {
//     const handleBeforeUnload = (event) => {

//       if (encoded_zoho_lead_id && encoded_interview_link_send_count) {
//         sessionStorage.setItem("zoho_lead_id", encoded_zoho_lead_id);
//         sessionStorage.setItem("interview_link_count", encoded_interview_link_send_count);
//         sessionStorage.setItem("isPageRefreshing", "true");
//       }

//       event.preventDefault();
//       event.returnValue = "";
//     };

//     window.addEventListener("beforeunload", handleBeforeUnload);

//     return () => {
//       window.removeEventListener("beforeunload", handleBeforeUnload);
//     };
//   }, [encoded_zoho_lead_id, encoded_interview_link_send_count]);

//   // ✅ On reload, get values directly from sessionStorage
//   useEffect(() => {
//     const isRefresh = sessionStorage.getItem("isPageRefreshing") === "true";
//     const lead = sessionStorage.getItem("zoho_lead_id");
//     const link = sessionStorage.getItem("interview_link_count");
//     // const firstEncodeId = sessionStorage.getItem('first_encoded_id');
//     const currentIndex = parseInt(sessionStorage.getItem("currentQuestionIndex"), 10);

//     if (isRefresh && lead && link) {
//       sessionStorage.removeItem("isPageRefreshing");
//       sessionStorage.removeItem("timeSpent");
//       sessionStorage.removeItem("currentQuestionIndex");

//        if (currentIndex === 0 || isNaN(currentIndex)) {
//             navigate('/goback');
//           } else {
//             submitExam();
//             navigate(`/interviewsubmitted?lead=${lead}&link=${link}&reason=PAGE_RELOADED`);
//           }
   
//       // sessionStorage.removeItem("interviewSubmitted");
//       // localStorage.clear()
//       // sessionStorage.clear()
//     }
//   }, [submitExam, navigate]);
// };

// export default usePageUnloadHandler;


import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

const usePageUnloadHandler = (
  encoded_zoho_lead_id,
  encoded_interview_link_send_count,
  getQuestions,
  currentQuestionIndex,
  countdown
) => {
  const navigate = useNavigate();
  const hasReportedExitRef = useRef(false);

  //  REPORT EXIT USING sendBeacon (reliable on reload/close)
  const reportExitOnUnload = (reason) => {
    if (hasReportedExitRef.current) return;
    hasReportedExitRef.current = true;

    const question = getQuestions?.[currentQuestionIndex];

    const payload = {
      zoho_lead_id: atob(encoded_zoho_lead_id),
      interview_link_count: encoded_interview_link_send_count,
      exit_question_index: currentQuestionIndex + 1,
      exit_question_id: question?.encoded_id || null,
      exit_reason: reason,
    };

    navigator.sendBeacon(
      `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-exit/`,
      JSON.stringify(payload)
    );
  };

  // Handle refresh / tab close
  useEffect(() => {
    const handleBeforeUnload = (event) => {
      if (encoded_zoho_lead_id && encoded_interview_link_send_count) {
        sessionStorage.setItem("zoho_lead_id", encoded_zoho_lead_id);
        sessionStorage.setItem("interview_link_count", encoded_interview_link_send_count);
        sessionStorage.setItem("isPageRefreshing", "true");

        //  IMPORTANT
        reportExitOnUnload("PAGE_RELOADED");
      }

      event.preventDefault();
      event.returnValue = "";
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [encoded_zoho_lead_id, encoded_interview_link_send_count, currentQuestionIndex]);

  // After reload → redirect user (NO submit)
  useEffect(() => {
    const isRefresh = sessionStorage.getItem("isPageRefreshing") === "true";
    const lead = sessionStorage.getItem("zoho_lead_id");
    const link = sessionStorage.getItem("interview_link_count");

    if (isRefresh && lead && link) {
      sessionStorage.removeItem("isPageRefreshing");
      sessionStorage.removeItem("timeSpent");
      sessionStorage.removeItem("currentQuestionIndex");

      navigate(
        `/interviewsubmitted?lead=${lead}&link=${link}&reason=PAGE_RELOADED`
      );
    }
  }, [navigate]);
};

export default usePageUnloadHandler;

