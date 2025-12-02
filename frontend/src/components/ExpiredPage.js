import React, { useState, useEffect } from "react"; // ✅ add useEffect
import { useParams } from "react-router-dom";
import axios from "axios";
import timeExpired from "../assest/icons/time-expired.svg"; // check path


const ExpiredPage = () => {
  const { zohoLeadId } = useParams();
  const decodedId = atob(zohoLeadId);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [showPopup, setShowPopup] = useState(false);
  const [interviewUrl, setInterviewUrl] = useState("");
   const [hideExtendButton, setHideExtendButton] = useState(false);   // ✅ HERE
   const [hideCheakdone, setHideCheakdone] = useState(false);   


     useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await axios.post(
          `${process.env.REACT_APP_API_BASE_URL}extend-first-interview/${decodedId}/?check_only=true`
        );

        // If backend says cannot extend, hide the button and show message
        if (!res.data.success) {
          setHideExtendButton(true);
          setMessage(res.data.message);
        }
      } catch (err) {
        console.error(err);
      }finally{
        setHideCheakdone(true);
      }
    };

    checkStatus();
  }, [decodedId]);

  const styles = {
    container: { display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", backgroundColor: "#f4f4f4", padding: "20px" },
    content: { background: "#fff", maxWidth: "600px", width: "100%", padding: "30px 25px", borderRadius: "10px", boxShadow: "0px 4px 12px rgba(0,0,0,0.1)", border: "1px solid #ddd", textAlign: "center" },
    titleImg: { height: "80px", width: "auto", marginBottom: "20px" },
    message: { fontSize: "20px", fontWeight: "bold", color: "#333", marginBottom: "10px" },
    subtext: { fontSize: "16px", color: "#555", marginBottom: "20px" },
    button: { marginTop: "20px", padding: "12px 20px", backgroundColor: "#db2777", color: "#fff", border: "none", borderRadius: "5px", fontWeight: "bold", cursor: "pointer" },
    msgBelow: { marginTop: "10px", fontSize: "14px" },
    popupOverlay: { position: "fixed", top: 0, left: 0, width: "100%", height: "100%", backgroundColor: "rgba(0,0,0,0.5)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 1000 },
    popupContent: { background: "#fff", padding: "30px", borderRadius: "10px", textAlign: "center", maxWidth: "400px", width: "100%", boxShadow: "0px 4px 12px rgba(0,0,0,0.2)" },
    popupButton: { padding: "12px 20px", margin: "10px", borderRadius: "5px", fontWeight: "bold", border: "none", cursor: "pointer" },
    startBtn: { backgroundColor: "#16a34a", color: "#fff" },
    laterBtn: { backgroundColor: "#6b7280", color: "#fff" },
  };

  // Only show popup, don't call API yet
  const handleShowPopup = () => {
    setShowPopup(true);
    setMessage("");
  };

  // Called when user clicks "Start Interview"
const handleStartInterview = async () => {
  setLoading(true);
  setMessage("");

  try {
    const response = await axios.post(
      `${process.env.REACT_APP_API_BASE_URL}extend-first-interview/${decodedId}/`
    );

    if (response.data.success) {
      const startLink = response.data.interview_link;
      if (startLink) {
        window.location.href = startLink;
      } else {
        setMessage(response.data.message || "Link already extended.");
        setShowPopup(false);
      }
    } else {
      const msg = response.data.message || "Link cannot be extended.";
      setMessage(msg);

      // 🔥 Hide button ONLY when backend returns this exact message
      if (msg === "You have already attended the interview. To extend the link, please contact us.") {
        setHideExtendButton(true);
      }

      setShowPopup(false);
    }
  } catch (error) {
    console.error(error);
    setMessage("❌ Failed to extend link. Try again later.");
    setShowPopup(false);
  } finally {
    setLoading(false);
  }
};

  const handleDoLater = () => {
    setShowPopup(false);
    setMessage("You chose to do it later. The link is not extended.");
  };

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <img src={timeExpired} alt="expired title link" style={styles.titleImg} />
          </div>
        </h1>
        <p style={styles.message}>The given link has expired.</p>
        <p style={styles.subtext}>You can request to extend your interview link.</p>

       {!hideExtendButton && hideCheakdone && (
          <button style={styles.button} onClick={handleShowPopup} disabled={loading}>
            Extend Interview Link
          </button>
        )}



        {message && <p style={styles.msgBelow}>{message}</p>}
      </div>

      {showPopup && (
        <div style={styles.popupOverlay}>
          <div style={styles.popupContent}>
            <h2>Interview Link Extend</h2>
            <p>Do you want to start your interview now or later?</p>
            <button
              style={{ ...styles.popupButton, ...styles.startBtn }}
              onClick={handleStartInterview}
              disabled={loading}
            >
              {loading ? "Starting..." : "Start Interview"}
            </button>
            <button
              style={{ ...styles.popupButton, ...styles.laterBtn }}
              onClick={handleDoLater}
            >
              Do Later
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpiredPage;
