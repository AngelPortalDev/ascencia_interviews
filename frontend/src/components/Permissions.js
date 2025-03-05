import { useState, useEffect  } from "react";
import {
  Dialog,
  DialogBackdrop,
  DialogPanel,
  DialogTitle,
} from "@headlessui/react";
import { useNavigate,useParams,useLocation } from "react-router-dom";
import {usePermission} from '../context/PermissionContext.js';


const Permissions = () => {
  
  const [audioPermission, setAudioPermission] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [recordVideoPermission, setRecordVideoPermission] = useState(false);
  const [errorMessageVideoPermission, setErrorMessageVideoPermission] = useState("");

  const [open, setOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  const encoded_zoho_lead_id = location.state?.encoded_zoho_lead_id || null;
  const encoded_interview_link_send_count = location.state?.encoded_interview_link_send_count || null;

  // console.log("lead id: " + encoded_zoho_lead_id)
  // console.log("interview link: " + encoded_interview_link_send_count)



  const {acceptAudioVideo}  = usePermission();
  // const { encoded_zoho_lead_id } = useParams();
  const handleAudioPermission = async () => {
    if(audioPermission){
      setAudioPermission(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log(stream,"stream is available");
      setAudioPermission(true);
      setErrorMessage("");
      stream.getTracks().forEach((track) => track.stop());
    } catch (err) {
      setAudioPermission(false);
      if (err.name === "NotFoundError") {
        setErrorMessage(
          "Your device does not have a audio. Please ensure you have a audio on your device."
        );
      }
      console.log(err);
    }
  };

  const handleVideoPermission = async () => {
    if(recordVideoPermission){
      setRecordVideoPermission(false)
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      setRecordVideoPermission(true);
      setErrorMessageVideoPermission("");
      stream.getTracks().forEach((track) => track.stop());
    } catch (error) {
      setRecordVideoPermission(false);
      if (error.name === "NotFoundError") {
        setErrorMessageVideoPermission(
          "Your device does not have a camera. Please ensure you have a camera on your device."
        );
      }
      console.log(error, "errors");
    }
  };

  const handleSubmit = () => {
    if (!audioPermission) {
      setErrorMessage("Please grant audio permission to proceed.");
      return;
    }
    if (!recordVideoPermission) {
      setErrorMessageVideoPermission("Please Accept permission to record the video.");
      return;
    } else {
      if (audioPermission && recordVideoPermission) {
        // setShowWelcome(true);
        // localStorage.setItem("hasPermissions", "true");
        acceptAudioVideo();
        // navigate(`/questions/${encoded_zoho_lead_id}/${encoded_interview_link_send_count}`);
        navigate(`/questions`, {
          state: { encoded_zoho_lead_id, encoded_interview_link_send_count }
        });
      }
    }
    setOpen(false);
  };


  useEffect(() => {
    const termsAccepted = localStorage.getItem("termsAccepted");

    if (termsAccepted !== "true") {
      navigate("/terms-and-conditions");
    }
  }, [navigate]);

  return (
    <div>
      <Dialog open={open} onClose={() => {}} className="relative z-10">
        <DialogBackdrop
          transition
          className="fixed inset-0 bg-gray-500/75 transition-opacity data-closed:opacity-0 data-enter:duration-300 data-enter:ease-out data-leave:duration-200 data-leave:ease-in"
        />

        <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center sm:items-center sm:p-0">
            <DialogPanel
              transition
              className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all data-closed:translate-y-4 data-closed:opacity-0 data-enter:duration-300 data-enter:ease-out data-leave:duration-200 data-leave:ease-in sm:my-8 sm:w-full sm:max-w-2xl data-closed:sm:translate-y-0 data-closed:sm:scale-95"
            >
              <div className="bg-white px-6 py-5 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                    <DialogTitle
                      as="h3"
                      className="text-xl font-semibold text-blue-600 mb-4"
                    >
                      Instructions
                    </DialogTitle>
                    <div className="space-y-4">
                      <ul className="list-disc pl-5">
                        <li className="text-gray-700 text-justify">
                          Please check the box to grant permission for audio
                          access, allowing the application to use your
                          microphone for audio-related features. An error
                          message will appear if not accepted.
                        </li>
                      </ul>
                      <ul className="list-disc pl-5">
                        <li className="text-gray-700 text-justify">
                          Check the box to allow video recording, enabling the
                          use of your camera for video-related functions. An
                          error message will appear if not accepted.
                        </li>
                      </ul>
                      <ul className="list-disc pl-5">
                        <li className="text-gray-700 text-justify">
                          After granting the necessary permissions, click the
                          Submit button to save your selections.
                        </li>
                      </ul>
                      <ul className="list-disc pl-5">
                        <li className="text-gray-700 text-justify">
                          Ensure both audio and video permissions are granted to
                          use the required features. Adjust your choices before
                          submitting.
                        </li>
                      </ul>
                    </div>

                    <div className="mt-6 space-y-4">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={audioPermission}
                          onChange={handleAudioPermission}
                          className="h-5 w-5 text-blue-600 border-gray-300 rounded"
                          id="audioPermission"
                        />
                        <label
                          htmlFor="audioPermission"
                          className="ml-3 text-sm text-gray-700 font-semibold"
                        >
                          Please accept audio
                        </label>
                      </div>
                      <p className="text-sm text-red-500 mt-2 text-justify">
                        {!audioPermission ? errorMessage : ""}
                      </p>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={recordVideoPermission}
                          onChange={handleVideoPermission}
                          className="h-5 w-5 text-blue-600 border-gray-300 rounded"
                          id="videoPermission"
                        />
                        <label
                          htmlFor="videoPermission"
                          className="ml-3 text-sm text-gray-700 font-semibold text-justify"
                        >
                          Please accept video recording
                        </label>
                      </div>
                      <p className="text-sm text-red-500 mt-2 text-justify">
                        {!recordVideoPermission
                          ? errorMessageVideoPermission
                          : ""}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                <button
                  type="button"
                  onClick={handleSubmit}
                  className="inline-flex w-full justify-center rounded-md bg-pink-600 px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-pink-500 sm:ml-3 sm:w-auto"
                >
                  Submit
                </button>
              </div>
            </DialogPanel>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default Permissions;
