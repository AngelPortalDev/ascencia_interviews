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
    <div className="submitted-container">
      <div className="submitted-content">
        <h1 className="submitted-title">✔</h1>
        <p className="submitted-message">Thank you for your submission!</p>
        <p className="submitted-subtext">Redirecting you shortly...</p>
        <a href="/" className="bg-[rgb(219,39,131)] text-white rounded-md text-sm px-4 py-2 md:text-lg md:px-6 md:py-3">
                Go Back to Home
        </a>
      </div>
  </div>
  );
};

export default InterviewSubmitted;
