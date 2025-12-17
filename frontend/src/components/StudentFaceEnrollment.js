import React, { useState, useRef, useEffect } from "react";
import Webcam from "react-webcam";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Instruction from "../assest/studentWIthId.jpg";
import Logo from "../assest/Logo.png";
import { useNavigate, useLocation } from "react-router-dom";
import Loader from "./Loader.js";
import Axios from "axios";

const StudentFaceEnrollment = () => {
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [showInstructions, setShowInstructions] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [loading, setLoading] = useState(false);

  // ✅ Add this line here
const [branding, setBranding] = useState({
  logo: Logo,
  name: "Face Authentication Enrollment",
});

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
      setLoading(true);
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
        toast.success("Uploaded successfully!", {
          autoClose: 2000,
          hideProgressBar: true,
        });
        setShowCamera(false);
        // alert("SUCCESSFULLY UPLOADED...")
        setShowCamera(false);
      }
    } catch (err) {
      const message =
        err?.response?.data?.message || err?.message || "Failed to upload!";
      console.error("Upload error:", message);
      console.log(err);
    } finally {
      setLoading(false);
    }
  };



function hasMicActivity(stream) {
  return new Promise((resolve) => {
    let audioContext = null;
    let analyser = null;
    let source = null;
    let interval = null;
    
    try {
      audioContext = new AudioContext();
      analyser = audioContext.createAnalyser();
      source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);

      const data = new Uint8Array(analyser.frequencyBinCount);

      let activity = false;
      let checks = 0;

      interval = setInterval(() => {
        try {
          analyser.getByteFrequencyData(data);
          const volume = data.reduce((a, b) => a + b, 0) / data.length;
          if (volume > 5) activity = true;
          checks++;

          if (checks > 20) { 
            clearInterval(interval);
            interval = null;
            
            // Safe cleanup - disconnect source first
            try {
              if (source) {
                source.disconnect();
                source = null;
              }
            } catch (e) {
              console.log('[Cleanup] Source disconnect:', e.message);
            }
            
            // Safe cleanup - close AudioContext
            try {
              if (audioContext && audioContext.state !== 'closed') {
                audioContext.close()
                  .then(() => console.log('[Cleanup] AudioContext closed'))
                  .catch(e => console.log('[Cleanup] AudioContext close:', e.message));
              }
            } catch (e) {
              console.log('[Cleanup] AudioContext:', e.message);
            }
            
            resolve(activity);
          }
        } catch (err) {
          console.log('[MicActivity] Check error:', err.message);
          if (interval) {
            clearInterval(interval);
            interval = null;
          }
          
          // Safe cleanup on error
          try {
            if (source) source.disconnect();
          } catch (e) {
            console.log('[Error cleanup] Source:', e.message);
          }
          
          try {
            if (audioContext && audioContext.state !== 'closed') {
              audioContext.close().catch(e => console.log('[Error cleanup] AudioContext:', e.message));
            }
          } catch (e) {
            console.log('[Error cleanup] AudioContext check:', e.message);
          }
          
          resolve(false);
        }
      }, 100);
    } catch (err) {
      console.log('[MicActivity] Init error:', err.message);
      if (interval) clearInterval(interval);
      resolve(false);
    }
  });
}

// This function needs to be outside or accessible here if it's not already in global scope
function getSupportedMimeType(types) {
  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) {
      return type;
    }
  }
  return "";
}

async function testRecording() {
  let stream = null;
  let recorder = null;
  
  try {
    // 1. Check MediaStream for audio and video tracks
    stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: { noiseSuppression: false, echoCancellation: false, autoGainControl: true },
    });

    const videoTracks = stream.getVideoTracks();
    const audioTracks = stream.getAudioTracks();

    if (videoTracks.length === 0) {
      console.error("Recording test failed: No video track found in stream.");
      
      // Cleanup before returning
      if (stream) {
        stream.getTracks().forEach(t => {
          try { t.stop(); } catch (e) { console.log('[Cleanup] Track:', e.message); }
        });
      }
      
      return { 
        success: false, 
        message: "We couldn't detect your camera. Please ensure it's connected and enabled, and that you've granted permission to access it" 
      };
    }
    
    if (audioTracks.length === 0) {
      console.error("Recording test failed: No audio track found in stream.");
      
      // Cleanup before returning
      if (stream) {
        stream.getTracks().forEach(t => {
          try { t.stop(); } catch (e) { console.log('[Cleanup] Track:', e.message); }
        });
      }
      
      return { 
        success: false, 
        message: "We couldn't detect your microphone. Please ensure it's connected and enabled, and that you've granted permission to access it" 
      };
    }
    
    console.log(`Stream obtained. Video tracks: ${videoTracks.length}, Audio tracks: ${audioTracks.length}`);

    // Check mic activity with proper error handling
    let micHasSound = false;
    try {
      micHasSound = await hasMicActivity(stream);
      console.log('micHasSound', micHasSound);
    } catch (err) {
      console.log("Mic activity check failed:", err.message);
      // Continue anyway - don't block on mic check failure
    }
    
    if (!micHasSound) {
      // Cleanup before returning
      if (stream) {
        stream.getTracks().forEach(t => {
          try { t.stop(); } catch (e) { console.log('[Cleanup] Track:', e.message); }
        });
      }
      
      return { 
        success: false, 
        message: "Your microphone is detected, but no sound was picked up. Please unmute or select the correct device." 
      };
    }

    // 2. Select a robust MIME type
    const types = [
      "video/webm;codecs=vp8,opus", 
      "video/webm;codecs=vp9,opus",
      "video/webm",
    ];
    const mimeType = getSupportedMimeType(types);

    if (!mimeType) {
      console.error("Recording test failed: No supported video/audio MIME type found for MediaRecorder.");
      
      // Cleanup before returning
      if (stream) {
        stream.getTracks().forEach(t => {
          try { t.stop(); } catch (e) { console.log('[Cleanup] Track:', e.message); }
        });
      }
      
      return { 
        success: false, 
        message: "Your browser isn't fully compatible with our recording system. Please try updating your browser or using a different one like Chrome, Firefox, or Edge." 
      };
    }

    recorder = new MediaRecorder(stream, {
      mimeType: mimeType,
      audioBitsPerSecond: 64000,
      videoBitsPerSecond: 2000000,
    });
    
    let chunks = [];

    recorder.ondataavailable = e => {
      if (e.data.size > 0) {
        console.log("Recorder data available:", e.data.size);
        chunks.push(e.data);
      }
    };

    recorder.onerror = (e) => {
      console.error("Recorder error during test:", e.error);
    };

    recorder.start();
    console.log("Recorder started.");

    // Record for a short duration
    await new Promise(res => setTimeout(res, 1000));

    // Stop the recorder
    recorder.stop();

    // Wait for the 'onstop' event to ensure all data is flushed
    await new Promise(res => (recorder.onstop = res));
    console.log("Recorder stopped.");

    // Cleanup stream tracks safely
    if (stream) {
      stream.getTracks().forEach(t => {
        try {
          t.stop();
        } catch (err) {
          console.log("Track cleanup:", err.message);
        }
      });
    }

    if (chunks.length === 0) {
      console.log("chunks.length", chunks.length);
      console.error("Recording test failed: No data chunks were recorded.");
      return { 
        success: false, 
        message: "We couldn't capture any video or audio data. Please ensure your camera and microphone are working correctly." 
      };
    }

    // Attempt to create a blob to simulate final output
    const testBlob = new Blob(chunks, { type: mimeType });
    if (testBlob.size === 0) {
      console.log("testBlob.size", testBlob.size);
      console.error("Recording test failed: Created 0-byte blob.");
      return { 
        success: false, 
        message: "The recording produced an empty file. This might be a browser issue. Please try again or use a different browser" 
      };
    }

    return { success: true, message: "Recording test passed." };

  } catch (err) {
    console.error("Comprehensive recording test failed:", err);
    
    // More specific error messages for getUserMedia failures
    if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
      return { 
        success: false, 
        message: "Camera/microphone access denied. Please allow permissions." 
      };
    } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
      return { 
        success: false, 
        message: "No camera or microphone found." 
      };
    } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
      return { 
        success: false, 
        message: "Camera/microphone already in use or inaccessible." 
      };
    } else if (err.name === "OverconstrainedError") {
      return { 
        success: false, 
        message: "Browser could not satisfy media constraints. Try default audio:true." 
      };
    }
    
    return { 
      success: false, 
      message: `An unexpected error occurred: ${err.message}.` 
    };
  } finally {
    // Ensure tracks are always stopped in case of early exit
    if (stream) {
      stream.getTracks().forEach(t => {
        try {
          t.stop();
        } catch (err) {
          console.log("Final cleanup:", err.message);
        }
      });
    }
  }
}

// And your handleSubmit would be updated to:

useEffect(() => {
  const fetchBranding = async () => {
    if (!encoded_zoho_lead_id) return;
    try {
      const response = await Axios.post(
        `${process.env.REACT_APP_API_BASE_URL}interveiw-section/get-branding-by-zoho-id/`,
        { zoho_lead_id: encoded_zoho_lead_id }
      );
      if (response.data.success) {
        setBranding({
          logo: response.data.logo_url || Logo,
          name: response.data.company_name || "Face Authentication Enrollment",
        });
      }
    } catch (err) {
      console.error("Branding fetch failed:", err);
    }
  };
  fetchBranding();
}, [encoded_zoho_lead_id]);

const handleSubmit = async () => {
  // setLoading(true);
  // const testResult = await testRecording();

  // if (!testResult.success) {
  //   alert(`Recording setup failed: ${testResult.message}\n\nPlease check your browser permissions, or try again using another device or an incognito/private window.`);
  //   return;
  // }
  navigate(`/questions`, {
    state: { encoded_zoho_lead_id, encoded_interview_link_send_count },
  });

};

  return (
    <>
      {loading && <Loader />}
      <div className="mx-auto max-w-4xl py-2 sm:py-4 lg:py-4">
        {/* <ToastContainer /> */}
        <div className="text-center mb-10">
          <img src={branding.logo} alt="Logo" className="h-16 mx-auto" />
          <h2 className="text-2xl font-bold mt-4 text-gray-800">
            Face Authentication Enrollment
          </h2>
          <p className="text-gray-600 mt-2 max-w-xl mx-auto text-sm">
            Please capture a clear photo of your face holding your ID card.
            These will help us authenticate you securely in future. Ensure
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
          {/* <div className="d-flex space-x-3">
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
        </div> */}
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mt-4 ">
            <button
              className="bg-pink-500 text-white px-6 py-2 rounded hover:bg-pink-700 transition w-full sm:w-auto text-center"
              onClick={handleStartCapture}
            >
              {!capturedImage ? "Capture Face with ID" : "Retake"}
            </button>

            <button
              onClick={handleSubmit}
              disabled={!capturedImage}
              className={`px-6 py-2 rounded transition w-full sm:w-auto text-center ${
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
                  Make sure your face is fully visible and your student ID is
                  held clearly below your chin like this:
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
    </>
  );
};

export default StudentFaceEnrollment;
