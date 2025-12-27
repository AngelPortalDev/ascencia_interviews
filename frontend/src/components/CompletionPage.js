import React from 'react';

export const CompletionPage = ({ completionCountdown }) => {
  return (
    <div className="relative min-h-screen bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center p-6">
      <div className="max-w-md w-full rounded-lg shadow-lg p-8 bg-white">
        <div className="text-center">
          <div className="mb-6">
            {/* Success Checkmark Animation */}
            <div className="flex justify-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center animate-bounce">
                <svg
                  className="w-8 h-8 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
            </div>
          </div>
          
          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            Interview Completed!
          </h1>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p className="text-gray-700 font-semibold">
              Thank you for completing the interview
            </p>
          </div>
          
          <p className="text-sm text-gray-600 mb-6">
            Your responses have been saved successfully.
          </p>

          {/* Countdown Display */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <p className="text-sm text-gray-600 mb-2">Your interview will end in</p>
            <div className="text-5xl font-bold text-blue-600 mb-2">
              {completionCountdown}
            </div>
            <p className="text-sm text-gray-600">
              {completionCountdown === 1 ? "second" : "seconds"}
            </p>
          </div>
          
          <p className="text-xs text-gray-500">
            Do not close this window
          </p>
        </div>
      </div>
    </div>
  );
};