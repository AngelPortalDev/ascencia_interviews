import { useEffect,useRef } from "react";
import { useNavigate } from "react-router-dom";

const InterviewSubmitted = () => {
  const navigate = useNavigate();
 const videoRef = useRef(null);
  useEffect(() => {

    if (videoRef?.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      console.log("🎤📷 Media stream stopped immediately on Interview Submitted Page.");
    }

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


  return (
    <div>
      <h3>Interview Submitted</h3>
      <p>Thank you for your submission! Redirecting you shortly...</p>
    </div>
  );
};

export default InterviewSubmitted;
