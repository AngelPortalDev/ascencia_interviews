import { useEffect } from "react";

const usePageUnloadHandler = () => {
  useEffect(() => {
    const handleBeforeUnload = (event) => {
      sessionStorage.setItem("isPageRefreshing", "true");
      event.preventDefault();
      event.returnValue = ""; // This triggers the default browser confirmation
    };

    const handlePageLoad = () => {
      if (sessionStorage.getItem("isPageRefreshing") === "true") {
        sessionStorage.removeItem("isPageRefreshing");
        const userConfirmed = window.confirm(
          "Are you sure you want to leave this page? Your interview process will not be saved.."
        );

        if (userConfirmed) {
          window.location.href = "/interviewsubmitted";
        }
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    window.addEventListener("load", handlePageLoad);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      window.removeEventListener("load", handlePageLoad);
    };
  }, []);
};

export default usePageUnloadHandler;
