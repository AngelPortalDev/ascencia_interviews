import React, { useEffect, useRef, useState } from "react";
import Logo from "../assest/Logo.png";
import Axios from "axios";

const NotFound = () => {
  const videoRef = useRef(null);
  const [branding, setBranding] = useState({
    logo: Logo,
    name: "AI Interview System",
  });

  const stopMediaStream = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      console.log("🎤📷 Media stream stopped immediately.");
    }
  };
  useEffect(() => {
    stopMediaStream();
  }, []);

  useEffect(() => {
  const encoded_zoho_lead_id = sessionStorage.getItem("encoded_zoho_lead_id");
  if (!encoded_zoho_lead_id) {
    console.log("⚠️ No encoded Zoho lead ID found — skipping branding fetch.");
    return;
  }

  const fetchBranding = async () => {
    try {
  if (!encoded_zoho_lead_id) return;

  const response = await Axios.post(
    `${process.env.REACT_APP_API_BASE_URL}interveiw-section/get-branding-by-zoho-id/`,
    { zoho_lead_id: encoded_zoho_lead_id }
  );

  if (response.data.success) {
    setBranding({
      logo: response.data.logo_url || Logo,
      name: response.data.company_name || "AI Interview System",
    });
  }
} catch (err) {
  console.error("Branding fetch failed:", err);
}
  };

  fetchBranding();
}, []);



  return (
    // <>
    //   <div className="logomobile d-flex justify-content-center" style={{background:'#f0f0f0', padding:'10px 20px'}} >
    //     <img src={branding.logo} alt="AI Software" className="h-16" />
    //   </div>
    //   <div className="not-found-container">
    //     <div className="not-found-content">
    //       <h1 className="not-found-title">404</h1>
    //       <p className="not-found-message">
    //       Oops! The page you’re looking for doesn’t exist.
    //     </p>
    //       {/* <a href="/" className="bg-[rgb(219,39,131)] text-white rounded-md text-sm px-4 py-2 md:text-lg md:px-6 md:py-3">
    //             Go Back to Home
    //     </a> */}
    //     </div>
    //   </div>
    // </>
     <>
    {/* Top Logo Section */}
    <div
      className="logomobile d-flex justify-content-center align-items-center shadow-sm"
      style={{
        background: "#ffffff",
        padding: "14px 20px",
        borderBottom: "1px solid #eee",
      }}
    >
      <img
        src={branding.logo}
        alt="Logo"
        style={{ height: "60px", objectFit: "contain" }}
      />
    </div>

    {/* Main 404 Section */}
    <div className="notfound-wrapper">
      <div className="notfound-card">
        <h1 className="notfound-title">404</h1>
        <p className="notfound-text">
        Oops! The page you’re looking for doesn’t exist.
        </p>

        {/* <a href="/" className="notfound-btn">
          Go Back Home
        </a> */}
      </div>
    </div>
  </>
  );
};

export default NotFound;
