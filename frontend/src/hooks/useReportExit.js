// hooks/useReportExit.js
import { useRef, useEffect } from "react";

const useReportExit = (
  encoded_zoho_lead_id,
  encoded_interview_link_send_count,
  getQuestions,
  currentQuestionIndex
) => {
  const hasReportedExitRef = useRef(false);
  const questionsRef = useRef([]);
  const indexRef = useRef(0);

  useEffect(() => {
    questionsRef.current = getQuestions || [];
    indexRef.current = currentQuestionIndex ?? 0;
  }, [getQuestions, currentQuestionIndex]);

  const reportExit = (reason) => {
    if (hasReportedExitRef.current) return;
    hasReportedExitRef.current = true;

    // 1️⃣ Try live refs
    let index = indexRef.current;
    let questions = questionsRef.current;
    let question = questions[index];
    let exit_question_id = question?.encoded_id || null;

    // 2️⃣ Fallback to sessionStorage if refs are empty
    if (!question) {
      index = Number(sessionStorage.getItem("currentQuestionIndex")) || 0;
      exit_question_id = sessionStorage.getItem("currentQuestionId") || null;
    }

    const payload = {
      zoho_lead_id: atob(encoded_zoho_lead_id),
      interview_link_count: encoded_interview_link_send_count,
      exit_question_index: index + 1,
      exit_question_id: exit_question_id, // ✅ ADD THIS
      exit_reason: reason,
    };

    console.log("📤 Reporting Exit:", payload);

    navigator.sendBeacon(
      `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-exit/`,
      JSON.stringify(payload)
    );
  };

  return reportExit;
};

export default useReportExit;