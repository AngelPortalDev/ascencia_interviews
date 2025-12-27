/* eslint-disable react-hooks/exhaustive-deps */
// hooks/useInterviewExit.js
import { useRef, useCallback } from 'react';

export const useInterviewExit = (
  encoded_zoho_lead_id,
  encoded_interview_link_send_count,
  currentQuestionIdRef  // This is a Ref, not a state
) => {
  const isInterviewCompletedRef = useRef(false);
  const isTabSwitchExceededRef = useRef(false);
  const isNavigatingAwayRef = useRef(false);

  // Remove currentQuestionIdRef from dependency array
  // because it's a Ref object, not a value that changes
  const reportInterviewExit = useCallback((reason) => {
    const zoho_lead_id =
      sessionStorage.getItem("zoho_lead_id") || encoded_zoho_lead_id;

    const interview_link_count =
      sessionStorage.getItem("interview_link_count") ||
      encoded_interview_link_send_count;

    console.log("Exit Report:", {
      question_id: currentQuestionIdRef?.current,
      reason: reason
    });

    const payload = {
      zoho_lead_id: atob(zoho_lead_id),
      interview_link_count,
      exit_question_id: currentQuestionIdRef?.current,  // Access the ref's current value
      exit_reason: reason,
    };

    if (!zoho_lead_id || !interview_link_count) {
      console.warn(" Missing interview identifiers, exit not reported");
      return;
    }

    navigator.sendBeacon(
      `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-exit/`,
      JSON.stringify(payload)
    );
  }, [encoded_zoho_lead_id, encoded_interview_link_send_count]);  // Remove currentQuestionIdRef

  return {
    isInterviewCompletedRef,
    isTabSwitchExceededRef,
    isNavigatingAwayRef,
    reportInterviewExit,
  };
};