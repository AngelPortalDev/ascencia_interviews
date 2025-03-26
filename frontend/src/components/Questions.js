import React, {
  useState,
  useEffect,
  useCallback,
  useMemo,
  useRef,
} from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import Axios from "axios";
import { Pagination, Navigation, Autoplay } from "swiper/modules";
import InterviewPlayer from "./InterviewPlayer.js";
import { toast } from "react-toastify";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import { usePermission } from "../context/PermissionContext.js";
import QuestionChecker from "./QuestionChecker.js";
import Swal from "sweetalert2";
import {
  startRecording,
  stopRecording,
  setupMediaStream,
} from "../utils/recording.js";
import {interviewAddVideoPath} from '../utils/fileUpload.js';
import usePageReloadSubmit from "../hooks/usePageReloadSubmit.js";
import AI_LOGO from "../assest/AI_LOGO.png";
// import useBackSubmitHandler from '../hooks/useBackSubmitHandler.js';

const Questions = () => {
  const [countdown, setCountdown] = useState(60);
  // const [userData, setUserData] = useState(null);
  const [getQuestions, setQuestions] = useState([]);
  const [navigationTime, setNavigationTime] = useState(0);
  const [isNavigationEnabled, setIsNavigationEnabled] = useState(false);
  const [timeSpent, setTimeSpent] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [transcribedText, setTranscribedText] = useState(""); // To hold transcribed text
  const [activeQuestionId, setActiveQuestionId] = useState(null); // Track active question
  const [student, setStudent] = useState(null);

  const [backButtonClicked, setBackButtonClicked] = useState(false);

  // const { student_id } = useParams(); // Get encoded student_id from URL
  const location = useLocation();
  const encoded_zoho_lead_id = location.state?.encoded_zoho_lead_id || null;
  const zoho_lead_id = atob(encoded_zoho_lead_id);

  //  // Recording State & Refs
  const [videoFilePath, setVideoFilePath] = useState(null);
  const [audioFilePath, setAudioFilePath] = useState(null);
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const audioRecorderRef = useRef(null);
  const recordedAudioChunksRef = useRef([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isFirstQuestionSet, setIsFirstQuestionSet] = useState(false);
  const [loading, setLoading] = useState(false);

  // usePageReloadSubmit(
  //   videoRef,
  //   mediaRecorderRef,
  //   audioRecorderRef,
  //   recordedChunksRef,
  //   recordedAudioChunksRef
  // );

  const navigate = useNavigate();
  const { submitExam } = usePermission();
  const last_question_id =
    getQuestions.length > 0
      ? getQuestions[getQuestions.length - 1].encoded_id
      : null;
  // console.log("LastQuestion id", last_question_id);

  // ***********  Fetch QUestions ***********
  const fetchQuestions = async () => {
    try {
      const res = await Axios.get(
        `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-questions/`
      );

      if (res.data && res.data.questions && res.data.questions.length > 0) {
        setQuestions(res.data.questions);
        setActiveQuestionId(res.data.questions[0].encoded_id);
      } else {
        console.warn("No questions found in the response.");
        setQuestions([]); // Ensure state is updated with an empty array
      }
    } catch (error) {
      console.error("Error fetching questions:", error);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, []);


  // When click back button tehn go to expired page

  //   window.history.pushState(null, '', window.location.pathname);
  //   window.addEventListener('popstate', handlePopState);
  //   return () => {
  //     window.removeEventListener('popstate', handlePopState);
  //   };
  // }, []);
  // useEffect(()=>{
  //   function DisableBackButton() {
  //     window.history.forward()
  //     }
  //     DisableBackButton();
  //     window.onload = DisableBackButton;
  //     window.onpageshow = function(evt) { if (evt.persisted) DisableBackButton() }
  //     window.onunload = function() { void (0) }
  // },[])

  // ************* Get First Question id *********

  useEffect(() => {
    if (getQuestions.length > 0 && !isFirstQuestionSet) {
      const firstQuestion = getQuestions[0];
      setActiveQuestionId(firstQuestion.encoded_id);
      setIsFirstQuestionSet(true);

      // console.log("Question start rrecordign LastQuestion id use effect", last_question_id);

      // Start the recording for the first question
      startRecording(
        videoRef,
        mediaRecorderRef,
        audioRecorderRef,
        recordedChunksRef,
        recordedAudioChunksRef,
        setIsRecording,
        setVideoFilePath,
        setAudioFilePath,
        // student_id,
        zoho_lead_id,
        firstQuestion.encoded_id,
        last_question_id
      );
    }
  }, [getQuestions, isFirstQuestionSet, last_question_id, zoho_lead_id]);


  const handleSubmit = useCallback(async () => {
    setLoading(true);
    const newQuestionId = getQuestions[currentQuestionIndex]?.encoded_id;
    if (!newQuestionId) {
      console.error("Error: newQuestionId is undefined or invalid.");
      return;
    }
  
    if (newQuestionId !== activeQuestionId) {
      setActiveQuestionId(newQuestionId);
    }
  
    try {
      await stopRecording(
        videoRef,
        mediaRecorderRef,
        audioRecorderRef,
        recordedChunksRef,
        recordedAudioChunksRef,
        setVideoFilePath,
        setAudioFilePath,
        zoho_lead_id,
        activeQuestionId,
        () => {
          try {
            startRecording(
              videoRef,
              mediaRecorderRef,
              audioRecorderRef,
              recordedChunksRef,
              recordedAudioChunksRef,
              setIsRecording,
              setVideoFilePath,
              setAudioFilePath,
              zoho_lead_id,
              newQuestionId,
              last_question_id
            );
          } catch (err) {
            console.error("Failed to start recording:", err);
          }
        },
        last_question_id
      );
  
      localStorage.setItem("interviewSubmitted", "true");
      submitExam();
      navigate("/interviewsubmitted");
    } catch (error) {
      console.error("Error in handleSubmit:", error);
    } finally {
      setLoading(false);
    }
  }, [
    activeQuestionId,
    getQuestions,
    currentQuestionIndex,
    last_question_id,
    submitExam,
    zoho_lead_id,
    navigate,
  ]);


  const handleSubmitNew = useCallback(async () => {
    setLoading(true);
    const newQuestionId = getQuestions[currentQuestionIndex]?.encoded_id;
    if (!newQuestionId) {
      console.error("Error: newQuestionId is undefined or invalid.");
      return;
    }
  
    if (newQuestionId !== activeQuestionId) {
      setActiveQuestionId(newQuestionId);
    }

    const response = await interviewAddVideoPath(videoFilePath, audioFilePath,zoho_lead_id,newQuestionId,last_question_id);
    console.log("response studnet",response.status);
    if(response.status === true && newQuestionId === last_question_id){
      navigate("/interviewsubmitted");
    }
    try {
      await stopRecording(
        videoRef,
        mediaRecorderRef,
        audioRecorderRef,
        recordedChunksRef,
        recordedAudioChunksRef,
        setVideoFilePath,
        setAudioFilePath,
        zoho_lead_id,
        activeQuestionId,
        () => {
          try {
            startRecording(
              videoRef,
              mediaRecorderRef,
              audioRecorderRef,
              recordedChunksRef,
              recordedAudioChunksRef,
              setIsRecording,
              setVideoFilePath,
              setAudioFilePath,
              zoho_lead_id,
              newQuestionId,
              last_question_id
            );
          } catch (err) {
            console.error("Failed to start recording:", err);
          }
        },
        last_question_id
      );
      
      localStorage.setItem("interviewSubmitted", "true");
      submitExam();
      navigate("/interviewsubmitted");
    } catch (error) {
      console.error("Error in handleSubmit:", error);
    } finally {
      setLoading(false);
    }
  }, [
    activeQuestionId,
    getQuestions,
    currentQuestionIndex,
    last_question_id,
    submitExam,
    zoho_lead_id,
    videoFilePath,
    audioFilePath,
    navigate,
  ]);


  //   usePageReloadSubmit(
  //   videoRef,
  //   mediaRecorderRef,
  //   audioRecorderRef,
  //   recordedChunksRef,
  //   recordedAudioChunksRef,
  // );

  
  // useEffect to trigger handleSubmit when the page is reloaded
// useEffect(() => {
//   const handleBeforeUnload = (event) => {
//     // Check if the interview has already been submitted to prevent unnecessary calls
//     if (!localStorage.getItem("interviewSubmitted")) {
//       event.preventDefault();
//       handleSubmit();  
//     }
//   };

//   window.addEventListener('beforeunload', handleBeforeUnload);

//   // Cleanup the event listener when the component unmounts
//   return () => {
//     window.removeEventListener('beforeunload', handleBeforeUnload);
//   };
// }, [handleSubmit]);

  // ************* Handle Countdown *************
  useEffect(() => {
    if (countdown > 0) {
      // Decrement countdown
      const timer = setInterval(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(timer); // Clean up the timer when countdown reaches 0
    } else {
      // When countdown reaches zero, handle transition to next question
      if (currentQuestionIndex < getQuestions.length - 1) {
        setCurrentQuestionIndex((prev) => {
          const nextIndex = prev + 1; // Move to the next question
          setActiveQuestionId(getQuestions[nextIndex]?.encoded_id); // Update the active question ID
          return nextIndex; // Return the updated index
        });
        setCountdown(60); // Reset the countdown for the next question
      } else {
        // Last question reached, stop media and submit the exam
        // stopMediaStream();
        handleSubmitNew();
      }
    }
  }, [countdown, currentQuestionIndex, getQuestions, handleSubmitNew]);

  // useEffect(() => {
  //   console.log("Countdown:", countdown);
  //   console.log("Current Question Index:", currentQuestionIndex);
  // }, [countdown, currentQuestionIndex]);

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    return `COUNTDOWN =  ${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setNavigationTime((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // ************ User Spent More Than 30 seconds then navigation enabled ****************
  useEffect(() => {
    if (timeSpent >= 5) {
      setIsNavigationEnabled(true);
    } else {
      setIsNavigationEnabled(false);
    }
  }, [timeSpent]);

  useEffect(() => {
    setTimeSpent(0);
  }, [currentQuestionIndex]);

  // Thhis recording & download work with help of arrow change
  const handleQuestionChange = useCallback(
    (swiper) => {
      if (!swiper) {
        console.error("Error: swiper is undefined.");
        return;
      }

      const newQuestionIndex = swiper.activeIndex;
      if (newQuestionIndex === undefined) {
        console.error("Error: activeIndex is undefined.");
        return;
      }

      setTimeSpent(0); // Reset time tracker on question change
      setCurrentQuestionIndex(newQuestionIndex); // Update question index

      const newQuestionId = getQuestions[newQuestionIndex]?.encoded_id;
      if (newQuestionId !== activeQuestionId) {
        setActiveQuestionId(newQuestionId); // Update active question ID
      }

      // Stop current recording and start new recording for the new question
      stopRecording(
        videoRef,
        mediaRecorderRef,
        audioRecorderRef,
        recordedChunksRef,
        recordedAudioChunksRef,
        setVideoFilePath,
        setAudioFilePath,
        zoho_lead_id,
        activeQuestionId,
        () => {
          try {
            startRecording(
              videoRef,
              mediaRecorderRef,
              audioRecorderRef,
              recordedChunksRef,
              recordedAudioChunksRef,
              setIsRecording,
              setVideoFilePath,
              setAudioFilePath,
              zoho_lead_id,
              newQuestionId,
              last_question_id
            );
          } catch (err) {
            console.error("Failed to start recording:", err);
          }
        },
        last_question_id
      );
      // console.log("videoRef",videoRef)
      // console.log("srcObject Video",videoRef.current.srcObject

      // Reset countdown
      setCountdown(60);
    },
    [activeQuestionId, getQuestions, zoho_lead_id, last_question_id,videoRef]
  );

  // Prevent unnecessary re-renders of InterviewPlayer
  const interviewPlayerMemo = useMemo(
    () => (
      <InterviewPlayer
        onTranscription={setTranscribedText}
        zoho_lead_id={zoho_lead_id}
        question_id={activeQuestionId}
        last_question_id={last_question_id}
        videoRef={videoRef}
        mediaRecorderRef={mediaRecorderRef}
        audioRecorderRef={audioRecorderRef}
        recordedChunksRef={recordedChunksRef}
        recordedAudioChunksRef={recordedAudioChunksRef}
      />
    ),
    [activeQuestionId, zoho_lead_id, last_question_id]
  );
  // console.log("Question interview player LastQuestion id", last_question_id);

  const handleTimeSpent = () => {
    // Increment time spent on current question
    setTimeSpent((prev) => prev + 1);
  };

  // Timer to track how long the user spends on each question
  useEffect(() => {
    const timeTracker = setInterval(() => {
      handleTimeSpent();
    }, 1000);

    return () => clearInterval(timeTracker);
  }, []);

  // ************ Interview Submit Go to Home Page ****************************
  // Here downlaod & recoding work after button click

  const fetchStudentData = async (zoho_lead_id) => {
    // console.log(student_id, 'student data');

    const formData = new FormData();
    formData.append("zoho_lead_id", btoa(zoho_lead_id));

    try {
      const res = await Axios.post(
        `${process.env.REACT_APP_API_BASE_URL}interveiw-section/student-data/`,
        formData // ✅ Pass formData here
      );
      if (res.data && res.data.student_data.length > 0) {
        setStudent(res.data.student_data[0]); // Get first object
      }
    } catch (error) {
      console.error("Error fetching student data:", error);
      return null; // Return null or handle the error properly
    }
  };
  useEffect(() => {
    if (zoho_lead_id) {
      fetchStudentData(zoho_lead_id);
    }
  }, [zoho_lead_id]);

  useEffect(() => {
    const handlePopState = () => {
      if (!backButtonClicked) {
        Swal.fire({
          title: "Submit Interview?",
          text: "Are you sure you want to submit the interview?",
          icon: "warning",
          showCancelButton: true,
          confirmButtonText: "Yes, submit",
          cancelButtonText: "No, stay",
        }).then((result) => {
          if (result.isConfirmed) {
            handleSubmit();
            setBackButtonClicked(true);
            window.history.pushState(null, "", window.location.href); // Push again after confirmation
          } else {
            window.history.pushState(null, "", window.location.href); // Prevent actual navigation
          }
        });
      } else {
        console.log("HandleSubmit Calling...");
        handleSubmit();
      }
    };
  
    // Add popstate event listener
    window.addEventListener("popstate", handlePopState);
    window.history.pushState(null, "", window.location.href); // Ensures the back button triggers popstate
  
    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, [backButtonClicked, handleSubmit]);
  
  if (loading) {
    return (
      <div>
        <section class="dots-container">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </section>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-gradient-to-r text-white">
      {/* Background Effect */}
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

      {/* Countdown Timer */}
      <div className="flex justify-between flex-col sm:flex-row px-8 pt-8 sm:pt-4  lg:px-16 items-center">
        <div>
          <h3 className="text-black text-xl sm:text-2xl mb-2">
            <img src={AI_LOGO} alt="AI Software" className="h-16" />
          </h3>
          {/* <img src={Logo} alt="Not found" style={{width:'200px'}}/> */}
        </div>
        <div
          className={` px-4 py-2 rounded-2xl text-lg sm:text-2xl font-extrabold transition-all tracking-wider
        ${
          countdown < 30
            ? "text-red-500 animate-blink"
            : "bg-gradient-to-r from-[#ff80b5] to-[#9089fc] sm:mt-2.5"
        }`}
        >
          {formatTime(countdown)}
        </div>
      </div>

      {/* Main Layout */}
      <div className="relative px-8 pt-8 lg:px-16">
        {/* Swiper for questions */}
        <Swiper
          pagination={{
            type: "fraction",
            renderFraction: (currentClass, totalClass) => (
              <span>
                <span className={currentClass}></span> /{" "}
                <span className={totalClass}></span>
              </span>
            ),
          }}
          navigation={isNavigationEnabled}
          allowSlidePrev={false}
          modules={[Pagination, Navigation, Autoplay]}
          className="mySwiper"
          autoplay={{
            delay: 60000,
            disableOnInteraction: false,
          }}
          onSlideChange={(swiper) => handleQuestionChange(swiper)} // Pass swiper here
          allowTouchMove={false}
        >
          {getQuestions.map((questionItem, index) => {
            return (
              <SwiperSlide
                key={index}
                className="bg-white p-6 rounded-lg shadow-lg text-black position-relative"
              >
                <p className="text-base sm:text-lg">{questionItem.question}</p>
                {index === getQuestions.length - 1 && (
                  <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="
                    bg-gradient-to-r from-[#ff80b5] to-[#9089fc] text-white font-semibold 
                    text-xs md:text-sm 
                    py-1 px-3 md:py-2 md:px-4 
                    rounded-xl shadow-lg 
                    hover:bg-gradient-to-l transition-all
                    w-auto"
                    style={{
                      position: "absolute",
                      right: "20px",
                      bottom: "20px",
                    }}
                  >
                    Submit
                  </button>
                )}
              </SwiperSlide>
            );
          })}
        </Swiper>

        {/* Grid Layout for User Info and Video */}
        <div className="grid grid-cols-12 gap-0  h-full sm:gap-8">
          <div
            className="col-span-12 md:col-span-9 bg-white p-2 rounded-xl  text-black  mt-2 sm:mt-0 "
            style={{ display: "hidden" }}
          ></div>
          <div className="col-span-12 md:col-span-3 bg-white p-2 rounded-xl  text-black interviewPlayer">
            {interviewPlayerMemo}
          </div>
        </div>
      </div>

      {/* Blinking effect for countdown */}
      <style>
        {`
        @keyframes blink {
          0% { opacity: 1; }
          50% { opacity: 0; }
          100% { opacity: 1; }
        }
        .animate-blink {
          animation: blink 1s infinite;
        }
      `}
      </style>
    </div>
  );
};

export default Questions;
