import React, { useEffect,useRef } from 'react'

const NotFound = () => {
  const videoRef = useRef(null);

  const stopMediaStream = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      console.log("🎤📷 Media stream stopped immediately.");
    }
  };
  useEffect(()=>{
    stopMediaStream();
  },[])
  return (
    <div className="not-found-container">
      <div className="not-found-content">
        <h1 className="not-found-title">404</h1>
        <p className="not-found-message">Oops! The page you’re looking for doesn’t exist.</p>
        <a href="/" className="bg-[rgb(219,39,131)] text-white rounded-md text-sm px-4 py-2 md:text-lg md:px-6 md:py-3">
                Go Back to Home
        </a>
      </div>
    </div>
  )
}

export default NotFound
