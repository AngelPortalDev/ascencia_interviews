import React, { useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import timeExpired from "../assest/icons/time-expired.svg";

const ExpiredPage = () => {
  const { zohoLeadId } = useParams();    // <-- FIX 1: get from URL

  const decodedId = atob(zohoLeadId);    // <-- FIX 2: decode
  console.log("Decoded ID:", decodedId);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  console.log("useParams() output:", useParams());
  const handleExtendLink = async () => {
  if (!zohoLeadId) {
    setMessage("Student ID not found.");
    return;
  }

  setLoading(true);
  setMessage("");

  try {
    const csrftoken = document.cookie
      .split("; ")
      .find(row => row.startsWith("csrftoken="))
      ?.split("=")[1];

    const response = await axios.post(`${process.env.REACT_APP_API_BASE_URL}extend-first-interview/${decodedId}/`);





    console.log("Extend link response:", response);

    if (response.data.success) {
      setMessage("✅ Interview link extended successfully.");
    } else {
      setMessage(`⚠️ ${response.data.message}`);
    }
  } catch (error) {
    console.error(error);
    setMessage("❌ Failed to extend link. Try again later.");
  } finally {
    setLoading(false);
  }
};

  const styles = {
    container: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      minHeight: "100vh",
      backgroundColor: "#f4f4f4",
      padding: "20px"
    },
    content: {
      background: "#fff",
      maxWidth: "600px",
      width: "100%",
      padding: "30px 25px",
      borderRadius: "10px",
      boxShadow: "0px 4px 12px rgba(0,0,0,0.1)",
      border: "1px solid #ddd",
      textAlign: "center"
    },
    titleImg: { height: "80px", width: "auto", marginBottom: "20px" },
    message: { fontSize: "20px", fontWeight: "bold", color: "#333", marginBottom: "10px" },
    subtext: { fontSize: "16px", color: "#555", marginBottom: "20px" },
    button: { marginTop: "20px", padding: "12px 20px", backgroundColor: "#db2777", color: "#fff", border: "none", borderRadius: "5px", fontWeight: "bold", cursor: "pointer" },
    msgBelow: { marginTop: "10px", fontSize: "14px" }
  };

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1>
          <div style={{ display: 'flex', justifyContent: 'center' }}>
  <img src={timeExpired} alt="expired title link" style={styles.titleImg} />
</div>
        </h1>
        <p style={styles.message}>The given link has expired.</p>
        <p style={styles.subtext}>You can request to extend your interview link.</p>

        <button style={styles.button} onClick={handleExtendLink} disabled={loading}>
          {loading ? "Extending..." : "Extend Interview Link"}
        </button>

        {message && <p style={styles.msgBelow}>{message}</p>}
      </div>
    </div>
  );
};

export default ExpiredPage;
