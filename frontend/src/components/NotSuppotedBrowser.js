import React, { useEffect, useState } from "react";
import Logo from '../assest/Logo.png';
import { useParams } from "react-router-dom";
import Axios from "axios";
const NotSuppotedBrowser = () => {
  const { encoded_zoho_lead_id } = useParams();
  const [branding, setBranding] = useState({
    logo: Logo,
    name: "AI Interview System",
  });



   useEffect(() => {
    const fetchBranding = async () => {
      if (!encoded_zoho_lead_id) return;
      try {
        // 🔹 Decode if your ID is Base64 encoded
        const zoho_lead_id = atob(encoded_zoho_lead_id);

        const response = await Axios.post(
          `${process.env.REACT_APP_API_BASE_URL}interveiw-section/get-branding-by-zoho-id/`,
          { zoho_lead_id }
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
  }, [encoded_zoho_lead_id]);

  return (
    <>

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
                    This browser is not supported.
                  </h3>
                  <p className="w-full text-center mt-2">
                    Please open this site in Chrome, Firefox, or another modern browser.
                  </p>
                </div>
                <br />
              </div>
            </section>
          </div>
    </>
  );
};
export default NotSuppotedBrowser;
