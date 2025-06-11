import { useEffect } from "react";
import {usePermission } from '../context/PermissionContext.js';

const usePageUnloadHandler = () => {

  const { submitExam } = usePermission();

  useEffect(() => {


    const handleBeforeUnload = (event) => {
      // Set a flag indicating the page is about to refresh or navigate
      sessionStorage.setItem("isPageRefreshing", "true");
      // console.log("beforeunload triggered");
      submitExam();
      event.preventDefault();
      event.returnValue = ""; 
    };

    const handlePageLoad = () => {
      if (sessionStorage.getItem("isPageRefreshing") === "true") {
        sessionStorage.removeItem("isPageRefreshing");
        submitExam();
        // sessionStorage.setItem("isInterviewSubmitted", "true");
        localStorage.clear();
        // sessionStorage.clear();
        sessionStorage.removeItem("timeSpent");
        sessionStorage.removeItem("currentQuestionIndex");
        window.location.href = "/frontend/interviewsubmitted";
      }
    };

    if (sessionStorage.getItem("isPageRefreshing") === "true") {
      sessionStorage.removeItem("isPageRefreshing");
      // sessionStorage.setItem("isInterviewSubmitted", "true");
      submitExam();
      localStorage.clear();
      // sessionStorage.clear();
      sessionStorage.removeItem("timeSpent");
      sessionStorage.removeItem("currentQuestionIndex");
      window.location.href = "/frontend/interviewsubmitted";
    }

    // if (window.location.pathname === "/interviewsubmitted") {
    //   sessionStorage.setItem("isInterviewSubmitted", "true");
    // }
    // console.log("current path",window.location.pathname);

    // Add event listeners
    window.addEventListener("beforeunload", handleBeforeUnload);
    window.addEventListener("load", handlePageLoad);

    // Cleanup listeners on component unmount
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      window.removeEventListener("load", handlePageLoad);
    };
  }, []);
};

export default usePageUnloadHandler;
