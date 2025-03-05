import React from "react";

const ExpiredPage = () => {
  return (
    <div>
      <div className="expired-container">
        <div className="expired-content">
          <h1 className="expired-title">⏳</h1>
          <p className="expired-message">Session Expired</p>
          <p className="expired-subtext">Redirecting you shortly...</p>
          {/* <a href="/" className="go-home-btn">
            Go Back to Home
          </a> */}
        <a href="/" className="bg-[rgb(219,39,131)] text-white rounded-md text-sm px-4 py-2 md:text-lg md:px-6 md:py-3">
                Go Back to Home
        </a>

        </div>
      </div>
    </div>
  );
};

export default ExpiredPage;
