import { useEffect, useRef } from 'react';

export const usePageNavigation = (
  reportInterviewExit,
  isInterviewCompletedRef
) => {
  const popstateHandlerRef = useRef(false);
  const isHandlingNavRef = useRef(false);
  const exitReportedRef = useRef(false); 

  // Handle back button
  useEffect(() => {
    if (popstateHandlerRef.current) return;
    popstateHandlerRef.current = true;

    window.history.pushState(null, null, window.location.href);

    const handlePopState = () => {
      if (isInterviewCompletedRef.current) {
        return;
      }

      // Prevent duplicate handling
      if (isHandlingNavRef.current) {
        return;
      }

      isHandlingNavRef.current = true;
      exitReportedRef.current = true;

      const userConfirmed = window.confirm(
        "Are you sure you want to leave this page? Your interview process will not be saved."
      );

      if (userConfirmed) {
      
        reportInterviewExit("NAVIGATION_LEFT");
        window.location.replace("/frontend/goback");
      } else {
        isHandlingNavRef.current = false;
        exitReportedRef.current = false;
        window.history.pushState(null, null, window.location.href);
      }
    };

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
      popstateHandlerRef.current = false;
    };
  }, [reportInterviewExit, isInterviewCompletedRef]);

  // Handle page reload
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (isInterviewCompletedRef.current) {
        return;
      }

      // Only prevent reload if user hasn't clicked back button
      if (!isHandlingNavRef.current) {
        //  localStorage.clear();
        // sessionStorage.clear();
        exitReportedRef.current = true;
        sessionStorage.setItem("INTERVIEW_RELOADED", "true");
       
        reportInterviewExit("PAGE_RELOAD");
        window.location.replace("/frontend/goback");

        e.preventDefault();
        e.returnValue = "";
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [reportInterviewExit, isInterviewCompletedRef]);

  // Handle reload detection
  useEffect(() => {
    const reloaded = sessionStorage.getItem("INTERVIEW_RELOADED");

    if (reloaded && !isInterviewCompletedRef.current) {
      window.location.replace("/frontend/goback");
    }
  }, [isInterviewCompletedRef]);

  return popstateHandlerRef;
};