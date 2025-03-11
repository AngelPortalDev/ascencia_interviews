import React, { useEffect } from "react";
import axios from "axios";

const QuestionChecker = ({ transcribedText, questionId }) => {
  // Function to check the answer
  const checkAnswer = async (questionId, transcribedText) => {
    try {
      const formData = new FormData();
      formData.append("question_id", questionId);
      formData.append("answer", transcribedText);

      // console.log("📤 Sending FormData:", formData);

      const res = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}interveiw-section/check-answers/`,
        formData
      );

      console.log("✅ Response from API:", res.data); // Check the API response

      if (res.data && res.data.score !== undefined) {
        console.log("🏆 Answer Score:", res.data.score);
      } else {
        console.log("⚠️ Score not found in response!");
      }
    } catch (error) {
      console.error("❌ Error checking answer:", error);
    }
  };

  // Call checkAnswer when transcribedText or questionId changes
  useEffect(() => {
    console.log("📩 Received transcribed text:", transcribedText);
    console.log("🆔 Active question ID:", questionId);

    if (transcribedText && questionId) {
      checkAnswer(questionId, transcribedText);
    }
  }, [transcribedText, questionId]); // Run when `transcribedText` or `questionId` changes

  return (
    <div>
      <h2>Question Checker</h2>
      <p>Active Question ID: {questionId}</p>
      <p>Transcribed Text: {transcribedText || "Waiting for transcription..."}</p>
    </div>
  );
};

export default QuestionChecker;
