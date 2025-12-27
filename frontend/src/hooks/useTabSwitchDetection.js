import { useEffect, useRef } from 'react';
import { toast } from 'react-toastify';

export const useTabSwitchDetection = (onExceeded, isInterviewCompleted) => {
  const tabSwitchCountRef = useRef(0);
  const lastVisibilityStateRef = useRef(document.visibilityState);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (isInterviewCompleted) return;

      if (document.visibilityState === "hidden") {
        lastVisibilityStateRef.current = "hidden";
        return;
      }

      if (document.visibilityState === "visible") {
        if (lastVisibilityStateRef.current === "hidden") {
          tabSwitchCountRef.current += 1;

          console.log(` Tab switch detected - Count: ${tabSwitchCountRef.current}`);

          if (tabSwitchCountRef.current === 1) {
            toast.warning(
              " Warning 1: Please focus on the interview. Tab switching is not allowed.",
              { autoClose: 3000 }
            );
          } else if (tabSwitchCountRef.current === 2) {
            toast.warning(
              " Warning 2: This is your final warning. One more tab switch will end the interview.",
              { autoClose: 3000 }
            );
          } else if (tabSwitchCountRef.current >= 3) {
            onExceeded();  // Call the callback
          }
        }
        lastVisibilityStateRef.current = "visible";
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [isInterviewCompleted, onExceeded]);

  return tabSwitchCountRef;
};