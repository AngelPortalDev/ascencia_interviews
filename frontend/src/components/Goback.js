import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Logo from "../assest/Logo.svg";

const Goback = () => {
  const navigate = useNavigate();

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
          <img src={Logo} alt="AI Software" className="h-16" />
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
