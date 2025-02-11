// import React, { useState } from "react";
import PropTypes from "prop-types";


const InterviewQuestions = ({ questions, handleSubmit, handlePrev, handleNext, currentQuestionIndex }) => {
  return (
    <div className="flex flex-col items-center justify-center mt-20">
      <div className="text-center">
        {/* Display the current question */}
        <h2 className="text-lg font-semibold text-gray-800">
          {questions[currentQuestionIndex].question}
        </h2>
      </div>

      {/* Stepper: show current step and total steps */}
      <div className="mt-4 flex justify-center gap-x-4">
        <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
      </div>

      {/* Navigation buttons */}
      <div className="mt-6 flex gap-x-4">
        {currentQuestionIndex > 0 && (
          <button
            onClick={handlePrev}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md"
          >
            Previous
          </button>
        )}

        {currentQuestionIndex < questions.length - 1 ? (
          <button
            onClick={handleNext}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-green-600 text-white rounded-md"
          >
            Submit
          </button>
        )}
      </div>
    </div>
  );
};

InterviewQuestions.propTypes = {
    questions: PropTypes.array.isRequired,
    handleSubmit: PropTypes.func.isRequired,
    handlePrev: PropTypes.func.isRequired,
    handleNext: PropTypes.func.isRequired,
    currentQuestionIndex: PropTypes.number.isRequired,
};

export default InterviewQuestions;
