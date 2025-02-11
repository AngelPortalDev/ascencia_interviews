import { useState, useRef, useEffect } from "react";
import AllowRecordingModal from "./AllowRecordingModal.js";
import StartPlayerHomePage from "./StartPlayerHomePage.js";
// import { Pagination, Navigation } from "swiper/modules";
// import { Swiper, SwiperSlide } from "swiper/react";

// import "swiper/css";
// import "swiper/css/pagination";
// import "swiper/css/navigation";

const InterviewPlayer = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCheckPermission, setIsCheckPermission] = useState(false);
  const [errorMessagePermission, setErrorMessagePermission] = useState("");
  const [showHomepageData, setShowHomepageData] = useState(true);
  // const [isThankYouMessageVisible, setIsThankYouMessageVisible] =
  //   useState(false);

  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const timerRef = useRef(null);

  const handleStartInterview = () => {
    setIsModalOpen(true);
  };

  //  close the modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleChangeCheck = () => {
    setIsCheckPermission(true);
    setErrorMessagePermission("");
  };

  const handleSumbitPermission = async (e) => {
    e.preventDefault();
    setErrorMessagePermission("");

    if (!isCheckPermission) {
      setErrorMessagePermission("Please accept the permission to proceed.");
      return;
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
          video: true,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        mediaRecorderRef.current = new MediaRecorder(stream);
        mediaRecorderRef.current.ondataavailable = (e) => {
          if (e.data.size > 0) {
            recordedChunksRef.current.push(e.data);
          }
        };
        // Start recording
        mediaRecorderRef.current.start();

        timerRef.current = setTimeout(() => {
          // stop recording
          mediaRecorderRef.current.stop();

          if (videoRef.current && videoRef.current.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach((track) => track.stop());
          }
          // setIsThankYouMessageVisible(true);
        }, 500000);

        console.log("timeref cureent", timerRef.current);

        setIsModalOpen(false);
        setShowHomepageData(false);
      } catch (err) {
        console.log(err);
        return;
      }
    }
  }

  // const downloadVideo = () => {
  //   const blob = new Blob(recordedChunksRef.current, { type: "video/mp4" });
  //   const url = URL.createObjectURL(blob);
  //   const link = document.createElement("a");
  //   link.href = url;
  //   link.download = "recorded-video.webm";
  //   link.click();
  //   // Clean up the URL after the download
  //   URL.revokeObjectURL(url);
  // };

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  return (
    <div>
      <div className="relative isolate px-6 pt-14 lg:px-8">
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
        {/* Start Player Home Page */}
        {showHomepageData && (
          <StartPlayerHomePage handleStartInterview={handleStartInterview} />
        )}

        <div
          aria-hidden="true"
          className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]"
        >
          <div
            style={{
              clipPath:
                "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)",
            }}
            className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]"
          />
        </div>

      </div>

      {/* AllowrecordingModal */}
      {isModalOpen && (
        <AllowRecordingModal
          isCheckPermission={isCheckPermission}
          handleChangeCheck={handleChangeCheck}
          errorMessagePermission={errorMessagePermission}
          handleCloseModal={handleCloseModal}
          handleSumbitPermission={handleSumbitPermission}
        />
      )}

      {/* {isRecording && (
        <InterviewQuestions
          questions={questions}
          currentQuestionIndex={currentQuestionIndex}
          handleNext={handleNext}
          handlePrev={handlePrev}
          handleSubmit={handleSubmit}
        />
      )} */}

      {/* 
      {isRecording && (
      
        
      )} */}

      {/* {isThankYouMessageVisible && (
        <div className="thank-you-message">
          <h2>Thank you for your interest!</h2>
          <button className="btn btn-primary">submit</button>
        </div>
      )} */}

      {/* {!isThankYouMessageVisible && (
       
      )} */}

        <div className="text-center">
          <h1 className="text-balance text-3xl font-semibold tracking-tight text-gray-900 sm:text-4xl">
            AI Powered Interview Assistance
          </h1>

        </div>


<video
          ref={videoRef}
          className="fixed bottom-10 right-10 w-64 h-48 border-2 border-gray-400 rounded-lg"
          muted
          autoPlay
        />
    </div>
  );
};

export default InterviewPlayer;
