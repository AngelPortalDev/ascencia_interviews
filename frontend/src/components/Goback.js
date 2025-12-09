import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Logo from "../assest/Logo.png";
import Axios from "axios";
const Goback = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // ✅ Get values passed via navigate
  // NDkzMjIzNTAwMDE3MDQ2NjAwMQ==
  // const encoded_zoho_lead_id = location.state?.encoded_zoho_lead_id;
  // const encoded_zoho_lead_id = "NDkzMjIzNTAwMDE3MDQ2NjAwMQ==";
  // const encoded_interview_link_send_count = location.state?.encoded_interview_link_send_count;
  // const encoded_interview_link_send_count = "MQ";
  // const location = useLocation();
   const params = new URLSearchParams(location.search);
  const encoded_zoho_lead_id = params.get("lead");
  const encoded_interview_link_send_count = params.get("link");

    console.log("Zoho Lead ID:", encoded_zoho_lead_id);
    console.log("Interview Link Count:", encoded_interview_link_send_count);
    const [branding, setBranding] = useState({
      logo: Logo,
      name: "Goback",
    });

  useEffect(() => {
  const fetchBranding = async () => {
    if (!encoded_zoho_lead_id) return;
    try {
      const response = await Axios.post(
        `${process.env.REACT_APP_API_BASE_URL}interveiw-section/get-branding-by-zoho-id/`,
        { zoho_lead_id: encoded_zoho_lead_id }
      );
      if (response.data.success) {
        setBranding({
          logo: response.data.logo_url || Logo,
          name: response.data.company_name || "Face Authentication Enrollment",
        });
      }
    } catch (err) {
      console.error("Branding fetch failed:", err);
    }
  };
  fetchBranding();
}, [encoded_zoho_lead_id]);

  useEffect(() => {
    // Replace history so back doesn't go to previous page
    navigate("/goback", { replace: true });

    // Optional: disable back button using popstate
    const handlePopState = () => {
      navigate("/goback", { replace: true });
    };

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, [navigate]);

  return (
    <div>
      <div style={{ padding: "10px 20px" }}>
        <div className="logomobile">
          <img src={branding.logo} alt="AI Software" className="h-16" />
        </div>

        <section className="dots-container">
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              padding: "10px",
            }}
          >
            <div>
              <h3 className="text-lg sm:text-xl font-semibold text-gray-800 text-center">
                You have not completed your interview. Please go and give your
                interview again within 72 hours.
              </h3>
            </div>
            <br />
          </div>
        </section>
      </div>
    </div>
  );
};

export default Goback;
