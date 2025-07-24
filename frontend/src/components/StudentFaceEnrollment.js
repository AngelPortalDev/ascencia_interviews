import React, { useState, useRef } from "react";
import Webcam from "react-webcam";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Instruction from "../assest/studentWIthId.jpg";
import Logo from "../assest/Logo.svg";
import { useNavigate, useLocation } from "react-router-dom";
import Axios from "axios";

const StudentFaceEnrollment = () => {
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [showInstructions, setShowInstructions] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const encoded_zoho_lead_id = location.state?.encoded_zoho_lead_id || null;
  const encoded_interview_link_send_count =
    location.state?.encoded_interview_link_send_count || null;

  console.log(
    "encoded_interview_link_send_count",
    encoded_interview_link_send_count
  );
  console.log("encoded_zoho_lead_id", encoded_zoho_lead_id);

  const videoConstraints = {
    width: 400,
    height: 300,
    facingMode: "user",
  };

  const handleStartCapture = () => {
    setShowInstructions(true);
  };

  const handleCapture = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
    const blob = await (await fetch(imageSrc)).blob();
    console.log("blob", blob);
    console.log("imageSrc", imageSrc);

    const formData = new FormData();
    formData.append("image", blob);
    formData.append("zoho_lead_id", encoded_zoho_lead_id);
    try {
      const response = await Axios.post(
        `${process.env.REACT_APP_API_BASE_URL}interveiw-section/upload-profile-photo/`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log("response", response);

      if (response.status === 200) {
        toast.success("Uploaded successfully!",{
          autoClose:2000,
          hideProgressBar:true,
        });
        // alert("SUCCESSFULLY UPLOADED...")
        setShowCamera(false);
      }
    } catch (err) {
      const message =
        err?.response?.data?.message || err?.message || "Failed to upload!";
      console.error("Upload error:", message);
      console.log(err);
    }
  };

  const handleSubmit = () => {
    navigate(`/questions`, {
      state: { encoded_zoho_lead_id, encoded_interview_link_send_count },
    });
  };

  return (
    <div className="mx-auto max-w-4xl py-2 sm:py-4 lg:py-4">
      {/* <ToastContainer /> */}
      <div className="text-center mb-10">
        <img src={Logo} alt="Logo" className="h-16 mx-auto" />
        <h2 className="text-2xl font-bold mt-4 text-gray-800">
          Face Authentication Enrollment
        </h2>
        <p className="text-gray-600 mt-2 max-w-xl mx-auto text-sm">
          Please capture a clear photo of your face holding your ID card. These will
          help us authenticate you securely in future. Ensure
          you're in good lighting and your face is clearly visible.
        </p>
      </div>

      <div className="flex flex-col items-center space-y-4 border rounded p-3 max-w-md mx-auto">
        {/* {capturedImage && (
          <img
            src={capturedImage}
            alt="Captured"
            className="w-64 h-64 object-cover border rounded"
          />
        )} */}

        {capturedImage ? (
          <img
            src={capturedImage}
            alt="Captured"
            className="w-full h-64 object-cover rounded border"
          />
        ) : (
          <div className="w-full h-48 flex items-center justify-center bg-gray-50 text-gray-400 border rounded">
            No Image
          </div>
        )}
        <div className="d-flex space-x-3">
          <button
            className="bg-pink-500 text-white px-6 py-2 rounded hover:bg-pink-700 transition"
            onClick={handleStartCapture}
          >
            {!capturedImage ? "Capture Face with ID" : "Retake"}
          </button>
          <button
            onClick={handleSubmit}
            disabled={!capturedImage}
            className={`mt-6 px-6 mr-4 py-2 rounded transition ${
              capturedImage
                ? "bg-green-600 hover:bg-green-700 text-white"
                : "bg-gray-400 text-white cursor-not-allowed"
            }`}
          >
            Submit & Next
          </button>
        </div>
      </div>
      {/* Instruction Modal */}
      {showInstructions && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg text-center w-full max-w-2xl">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">
              Instructions
            </h3>
            <div className="flex items-start gap-3">
              <span className="text-green-600">✓</span>
              <p className="text-gray-700 text-justify leading-5">
                The Id you are holding should be same as the once you
                photographed
              </p>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-green-600">✓</span>
              <p className="text-gray-700 text-justify leading-5">
                The Photo side of your id should be facing towards the camera.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-green-600">✓</span>
              <p className="text-gray-700 text-justify leading-5">
                Take your selfi in a well-lit space.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-green-600">✓</span>
              <p className="text-gray-700 text-justify leading-5">
                Make sure the info on your id is clearly legible.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-green-600">✓</span>
              <p className="text-gray-700 text-justify leading-5">
                Make sure your face is fully visible and your student ID is held
                clearly below your chin like this:
              </p>
            </div>
            <div style={{ display: "flex", justifyContent: "center" }}>
              <img
                src={Instruction}
                alt="Example"
                className="rounded-lg border mb-4 mt-4"
                style={{ width: "250px" }}
              />
            </div>

            <button
              onClick={() => {
                setShowInstructions(false);
                setShowCamera(true);
              }}
              className="px-5 py-2 bg-pink-600 text-white rounded hover:bg-pink-700 transition"
            >
              I’m Ready
            </button>
          </div>
        </div>
      )}

      {/* Webcam Modal */}
      {showCamera && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-11/12 max-w-md text-center">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">
              Capture Your Face with ID 
            </h3>
            {!isCameraReady && (
              <div className="w-full h-[300px] flex items-center justify-center bg-gray-100 text-gray-400 rounded">
                Loading camera...
              </div>
            )}
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              className={`rounded border ${!isCameraReady ? "hidden" : ""}`}
              onUserMedia={() => setIsCameraReady(true)}
            />
            <div className="mt-4 space-x-3">
              <button
                onClick={handleCapture}
                className="px-4 py-2 bg-pink-600 text-white rounded hover:bg-pink-700 transition"
              >
                Capture
              </button>
              <button
                onClick={() => {
                  setShowCamera(false);
                  setIsCameraReady(false);
                }}
                className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-700 transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentFaceEnrollment;
