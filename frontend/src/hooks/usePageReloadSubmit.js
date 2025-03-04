import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

// Import the stopRecording function
import { stopRecording } from "../utils/recording.js"; 

const usePageReloadSubmit = (videoRef, mediaRecorderRef, audioRecorderRef, recordedChunksRef, recordedAudioChunksRef) => {
    const navigate = useNavigate();

    useEffect(() => {

        // Function to handle stopping recording before reload
        const handleBeforeUnload = () => {
            sessionStorage.setItem("isReload", "true");

            stopRecording(
                videoRef,
                mediaRecorderRef,
                audioRecorderRef,
                recordedChunksRef,
                recordedAudioChunksRef
            );
        };

        window.addEventListener("beforeunload", handleBeforeUnload);

        return () => {
            window.removeEventListener("beforeunload", handleBeforeUnload);
        };
    }, [videoRef, mediaRecorderRef, audioRecorderRef, recordedChunksRef, recordedAudioChunksRef]);

    useEffect(() => {
        // On page mount, check if it was a reload
        if (localStorage.getItem("InterviewSubmitted") === "true" || sessionStorage.getItem("isReload") === "true") {
            // sessionStorage.removeItem("isReload"); 
            navigate("/interviewsubmitted", { replace: true });
        }
    }, [navigate]);
};

export default usePageReloadSubmit;
