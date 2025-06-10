import { useEffect,useRef } from "react";
import { useNavigate } from "react-router-dom";

const InterviewSubmitted = () => {
  const navigate = useNavigate();
 const videoRef = useRef(null);
  useEffect(() => {


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

  useEffect(() => {
    // Check if the page has already reloaded once
    if (!sessionStorage.getItem("hasPageReloadedOnce")) {
      sessionStorage.setItem("hasPageReloadedOnce", "true"); 
      setTimeout(() => {
        window.location.reload(); 
      }, 0); 
    }
  }, []);


  return (
    <div className="submitted-container">
      <div className="submitted-content">
        <h1 className="submitted-title">✔</h1>
        <p className="submitted-message">Thank you for your submission!</p>
        {/* <p className="submitted-subtext">Redirecting you shortly...</p> */}
        {/* <a href="/" className="bg-[rgb(219,39,131)] text-white rounded-md text-sm px-4 py-2 md:text-lg md:px-6 md:py-3">
                Go Back to Home
        </a> */}
      </div>
  </div>
  );
};

export default InterviewSubmitted;
