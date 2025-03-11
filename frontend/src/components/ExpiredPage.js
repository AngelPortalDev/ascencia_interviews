import React from "react";
import timeExpired from '../assest/icons/time-expired.svg'

const ExpiredPage = () => {
  return (
    <div className="expired-container">
      <div className="expired-content">
        <h1 className="expired-title"><img src={timeExpired} alt="expired title link"/></h1>
        <p className="expired-message">The given link has expired.</p>
        <p className="expired-subtext">Please contact the administrator for further assistance.</p>
      </div>
    </div>
  );
};

export default ExpiredPage;
