import { useEffect, useState } from "react";
import { useNavigate, useParams, useLocation, NavLink } from "react-router-dom";
import PropTypes from "prop-types";
import { usePermission } from "../context/PermissionContext.js";
import GDPR from "../assest/GDPRPolicy.pdf";

const TermsAndCondition = () => {
  const location = useLocation();
  const [isAgreed, setIsAgreed] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [isPolicyAgreed, setIsPolicyAgreed] = useState(false);
  const [errorMessagePolicy, setErrorMessagePolicy] = useState("");
  const navigate = useNavigate();

  const { acceptTerms } = usePermission();

  const encoded_zoho_lead_id = location.state?.encoded_zoho_lead_id || null;
  const encoded_interview_link_send_count =
    location.state?.encoded_interview_link_send_count || null;

  const handleCheckboxChange = () => {
    setIsAgreed(!isAgreed);
    if (errorMessage) {
      setErrorMessage("");
    }
  };
  const handleCheckboxPolicy = () => {
    setIsPolicyAgreed(!isPolicyAgreed);
    if (errorMessagePolicy) {
      setErrorMessagePolicy("");
    }
  };

  const handleSubmit = () => {
    if (!isAgreed) {
      setErrorMessage("You must agree to the terms and conditions to proceed.");
    } else if (!isPolicyAgreed) {
      setErrorMessagePolicy("You must agree to the GDPR policy to proceed.");
    } else {
      acceptTerms();
      // navigate(/permissions/${encoded_zoho_lead_id});  // Navigate dynamically
      navigate("/permissions", {
        state: { encoded_zoho_lead_id, encoded_interview_link_send_count },
      });
    }
  };
  useEffect(() => {
    if (encoded_zoho_lead_id == null) {
      setTimeout(() => navigate("/expired"), 100);
    }
  }, [encoded_zoho_lead_id, navigate]);
  if (encoded_zoho_lead_id == null) return null;

  const styles = {
    privacyStyle: {
      color: "#2563EB",
    },
  };


  return (
    <>
      <div className="bg-white min-h-screen">
        <div className="relative isolate px-6 pt-8 lg:px-8">
          <div
            aria-hidden="true"
            className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80"
          >
            <div
              style={{
                clipPath:
                  "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)",
              }}
              className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
            />
          </div>
          <div className="mx-auto max-w-4xl py-8 sm:py-12 lg:py-12">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 sm:text-3xl leading-tight">
                Terms and Conditions
              </h1>
              <p className="mt-4 text-lg text-gray-500">
                Please read these Terms and Conditions carefully before using
                our service.
              </p>
            </div>

            <div className="space-y-8 text-gray-700">
              <section>
                <p className="text-lg font-semibold text-blue-600 termsheading">
                  1. Introduction
                </p>
                <p>
                  By clicking on 'I agree,' you accept EAscencia Business
                  School’s Terms and Conditions.
                </p>
              </section>
              <section>
                <p className="text-lg font-semibold text-blue-600 termsheading">
                  2. Use of the Platform
                </p>
                <p>
                  You agree to use the platform for interviews, including video,
                  text, and sentiment analysis. By participating, you consent to
                  data collection and processing as described in our Privacy
                  Policy.
                </p>
              </section>
              <section>
                <p className="text-lg font-semibold text-blue-600">
                  3. User Responsibilities
                </p>
                <ul className="list-disc pl-5">
                  <li>Provide accurate information during the interview.</li>
                  <li>
                    Ensure your device meets technical requirements for video
                    and audio recording.
                  </li>
                  <li>Do not attempt to bypass platform security.</li>
                </ul>
              </section>
              <section>
                <p className="text-lg font-semibold text-blue-600">
                  4. Data Collection
                </p>
                <p>
                  We collect and process video, audio, and text data to analyze
                  your responses. This data will be stored and processed
                  according to our{" "}
                  <span style={styles.privacyStyle}>
                    <NavLink
                      to="/privacy-policy"
                      state={{
                        encoded_zoho_lead_id,
                        encoded_interview_link_send_count,
                      }}
                    >
                      Privacy Policy.
                    </NavLink>
                  </span>
                </p>
              </section>
            </div>

            <div className="mt-10 flex items-center justify-start gap-x-6">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="agree"
                  checked={isAgreed}
                  onChange={handleCheckboxChange}
                  className="mr-2 h-5 w-5 border-gray-300 rounded text-blue-600 focus:ring-blue-500"
                />
                <label
                  htmlFor="agree"
                  className="text-sm font-semibold text-gray-900"
                >
                  I agree to the Terms and Conditions
                </label>
              </div>
            </div>

            <p className="text-red-500 text-sm mt-2">{errorMessage}</p>

            <div className="mt-5 flex items-center justify-start gap-x-6">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="agreepolicy"
                  checked={isPolicyAgreed}
                  onChange={handleCheckboxPolicy}
                  className="mr-2 h-5 w-5 border-gray-300 rounded text-blue-600 focus:ring-blue-500"
                />
                <label
                  htmlFor="agreepolicy"
                  className="text-sm font-semibold text-gray-900"
                >
                  Please accept{" "}
                  
                  <NavLink to="/GDPRPolicy.pdf" target="_blank" className="mr-2 text-blue-600">
                    GDPR Policy
                  </NavLink>
                </label>
              </div>
            </div>

            <p className="text-red-500 text-sm mt-2">{errorMessagePolicy}</p>

            <div className="mt-10 flex items-center justify-center">
              <button
                onClick={handleSubmit}
                className="rounded-md bg-pink-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-pink-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

TermsAndCondition.propTypes = {
  setHasAgreed: PropTypes.func.isRequired,
};

export default TermsAndCondition;