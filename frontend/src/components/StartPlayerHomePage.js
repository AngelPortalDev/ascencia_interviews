// import React from 'react'
import PropTypes from "prop-types";
import { NavLink } from "react-router-dom";

const StartPlayerHomePage = ({ handleStartInterview }) => {
  return (
    <div>
      <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
        <div className="hidden sm:mb-8 sm:flex sm:justify-center">
          <div className="relative rounded-full px-3 py-1 text-sm/6 text-gray-600 ring-1 ring-gray-900/10 hover:ring-gray-900/20">
          New features are coming soon to help you ace your job interviews.{" "}
            <a href="#" className="font-semibold text-indigo-600">
              <span aria-hidden="true" className="absolute inset-0" />
              Read more <span aria-hidden="true">&rarr;</span>
            </a>
          </div>
        </div>

        <div className="text-center">
          <h1 className="text-balance text-3xl font-semibold tracking-tight text-gray-900 sm:text-4xl">
            AI Powered Interview Assistance
          </h1>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <NavLink
              to=""
              onClick={handleStartInterview}
              className="rounded-md bg-pink-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Start Interview
            </NavLink>
          </div>
        </div>
      </div>
    </div>
  );
};

StartPlayerHomePage.propTypes = {
  handleStartInterview: PropTypes.func.isRequired,
};

export default StartPlayerHomePage;
