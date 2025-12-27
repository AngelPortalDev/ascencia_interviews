/* eslint-disable no-lone-blocks */
/* eslint-disable react-hooks/exhaustive-deps */
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
// import OpenAIRealtimeMicWS from "./OpenAIRealtimeMicWS.js";
import {
  startRecording,
  stopRecording,
  setupMediaStream,
} from "../utils/recording.js";
import { interviewAddVideoPath } from "../utils/fileUpload.js";
import Logo from "../assest/Logo.png";
import usePageUnloadHandler from "../hooks/usePageUnloadHandler.js";
import { setNetworkErrorCallback } from "../utils/fileUpload.js";
import useVisibilityWarning from '../hooks/useVisibilityWarning.js';

// // Suppress specific AudioContext errors

if (typeof window !== 'undefined') {
  const originalError = window.console.error;
  window.console.error = (...args) => {
    const errorMsg = args[0]?.toString() || '';
    if (
      errorMsg.includes('AudioContext') ||
      errorMsg.includes('close a closed') ||
      errorMsg.includes('Audio context')
    ) {
      console.log('[Suppressed]', ...args);
      return;
    }
    originalError.apply(console, args);
  };

  window.addEventListener('error', (event) => {
    const errorMsg = event.message || event.error?.message || '';
    if (
      errorMsg.includes('AudioContext') ||
      errorMsg.includes('close a closed') ||
      errorMsg.includes('Audio context')
    ) {
      console.log('[Suppressed Runtime Error]:', errorMsg);
      event.preventDefault();
      event.stopPropagation();
      return false;
    }
  }, true);
}

const Questions = () => {

  const [branding, setBranding] = useState({
      logo: Logo,
      name: "Question",
    });

  const [countdown, setCountdown] = useState(60);
  const [currentTimeLimit, setCurrentTimeLimit] = useState(60);

  const [endCountdown, setEndcountdwn] = useState(30);
  const [endCountdownTwo, setEndcountdwnTwo] = useState(30);
  const [getQuestions, setQuestions] = useState([]);
  const [navigationTime, setNavigationTime] = useState(0);
  const [isNavigationEnabled, setIsNavigationEnabled] = useState(false);
  const [timeSpent, setTimeSpent] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [transcribedText, setTranscribedText] = useState(""); // To hold transcribed text
  const [activeQuestionId, setActiveQuestionId] = useState(null); // Track active question
  const [student, setStudent] = useState(null);
  const [networkError, setNetworkError] = useState(null); // Track network/API errors
  const location = useLocation();
  const encoded_zoho_lead_id = location.state?.encoded_zoho_lead_id || null;
  const encoded_interview_link_send_count =
    location?.state?.encoded_interview_link_send_count || null;
  const zoho_lead_id = atob(encoded_zoho_lead_id);
  const safe_encoded_zoho_lead_id =
    encoded_zoho_lead_id || sessionStorage.getItem("zoho_lead_id");
  const safe_encoded_interview_link_send_count =
    encoded_interview_link_send_count ||
    sessionStorage.getItem("interview_link_count");

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
  const swiperRef = useRef(null);
  const recordingTimeoutRef = useRef(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const [showUploading, setShowUploading] = useState(false);
  const toastId = useRef(null);
  const endCountdownStartedRef = useRef(false);
  const endCountdownStartedRefTwo = useRef(false);
  const hasHandledZeroRef = useRef(false);
  const popstateHandlerRef = useRef(false);
  const isMobileOrIOS = () => /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);



const reportInterviewExit = (reason) => {
  const zoho_lead_id =
    sessionStorage.getItem("zoho_lead_id") || encoded_zoho_lead_id;

  const interview_link_count =
    sessionStorage.getItem("interview_link_count") ||
    encoded_interview_link_send_count;

  const exit_question_index = Number(
    sessionStorage.getItem("currentQuestionIndex")
  );

  const payload = {
    zoho_lead_id: atob(zoho_lead_id),
    interview_link_count,
    exit_question_index,
    exit_question_id: exit_question_index,
    exit_reason: reason,
  };

  if (!zoho_lead_id || !interview_link_count) {
    console.warn("❌ Missing interview identifiers, exit not reported");
    return;
  }

  navigator.sendBeacon(
    `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-exit/`,
    JSON.stringify(payload)
  );
};




  // For Safri reload detection
  useEffect(() => {
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    if (!isSafari) return;

    const nav = performance.getEntriesByType("navigation")[0];

    if (nav && nav.type === "reload") {
      navigate(
        `/interviewsubmitted?lead=${safe_encoded_zoho_lead_id}&link=${safe_encoded_interview_link_send_count}&reason=PAGE_RELOADED`
      );
    }
}, []);

  useEffect(() => {
    if (safe_encoded_zoho_lead_id) {
      sessionStorage.setItem("zoho_lead_id", safe_encoded_zoho_lead_id);
    }
    if (safe_encoded_interview_link_send_count) {
      sessionStorage.setItem(
        "interview_link_count",
        safe_encoded_interview_link_send_count
      );
    }
  }, [safe_encoded_zoho_lead_id, safe_encoded_interview_link_send_count]);

// Enhanced network status monitoring
  useEffect(() => {
    
    const handleOffline = () => {
      console.log(' Connection lost');
      setNetworkError({
        type: 'network_error',
        error: 'Your internet connection was lost. Please check your connection.'
      });
    };
    
    window.addEventListener('offline', handleOffline);
    
    return () => {
    
      window.removeEventListener('offline', handleOffline);
    };
  }, [networkError]);

  // Setup network error callback
  useEffect(() => {
    setNetworkErrorCallback((errorData) => {
      console.error("Network error detected:", errorData);
      setNetworkError(errorData);
      setLoading(false);
    });
  }, []);

  usePageUnloadHandler(
    safe_encoded_zoho_lead_id,
    safe_encoded_interview_link_send_count,
    getQuestions,
    currentQuestionIndex,
    countdown

  );

   useVisibilityWarning(
    safe_encoded_zoho_lead_id,
    safe_encoded_interview_link_send_count,
    currentQuestionIndex,
    getQuestions
  );

  useEffect(() => {
  if (activeQuestionId) {
    sessionStorage.setItem("currentQuestionId", activeQuestionId);
  }
}, [activeQuestionId]);

  // usePageUnloadHandler(encoded_zoho_lead_id,encoded_interview_link_send_count);
  const navigate = useNavigate();
  const { submitExam } = usePermission();
  const last_question_id =
    getQuestions.length > 0
      ? getQuestions[getQuestions.length - 1].encoded_id
      : null;
  // console.log("LastQuestion id", last_question_id);

  // ***********  Fetch QUestions ***********
  // const fetchQuestions = async () => {
  //   try {
  //     const res = await Axios.get(
  //       `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-questions/`
  //     );

  //     if (res.data && res.data.questions && res.data.questions.length > 0) {
  //       setQuestions(res.data.questions);
  //       setActiveQuestionId(res.data.questions[0].encoded_id);
  //     } else {
  //       console.warn("No questions found in the response.");
  //       setQuestions([]); // Ensure state is updated with an empty array
  //     }
  //   } catch (error) {
  //     console.error("Error fetching questions:", error);
  //   }
  // };

  const fetchInterviewQuestions = async () => {
    const formData = new FormData();
    formData.append("zoho_lead_id", safe_encoded_zoho_lead_id);
    formData.append(
      "interview_link_count",
      safe_encoded_interview_link_send_count
    );

    try {
      const res = await Axios.post(
        `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-questions/`,
        {
          zoho_lead_id: safe_encoded_zoho_lead_id,
          interview_link_count: safe_encoded_interview_link_send_count,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log("data", res.data);

      if (res.data && res.data.questions) {
        setQuestions(res.data.questions);
        setActiveQuestionId(res.data.questions[0].question_id); // or encoded_id
      } else {
        console.warn("No questions found in the response.");
        setNetworkError({
          type: 'api_error',
          error: 'No questions found. Please refresh to retry.'
        });
      }
    } catch (error) {
      console.error("Error fetching interview questions:", error);
      if (!error.response || error.code === 'ECONNABORTED' || error.code === 'ENOTFOUND' || !navigator.onLine) {
        setNetworkError({
          type: 'network_error',
          error: error.message
        });
      } else {
        setNetworkError({
          type: 'backend_disconnected',
          error: 'Failed to fetch questions. Please refresh to retry.'
        });
      }
    }
  };
  // Store countdown in the sessionstorage for resuem resume
  useEffect(() => {
    // Stop the timer if countdown reaches 0 or during loading

      // if (networkError) {
      //   return;
      // }


    if (countdown <= 0 || loading) {
      return;
    }

    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer); // Stop immediately when reaching 0
          return 0;
        }
        const newValue = prev - 1;
        sessionStorage.setItem("countdown", newValue.toString());
        return newValue;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [countdown, loading, currentQuestionIndex]);

  useEffect(() => {
    // Store time spent and question index
    sessionStorage.setItem("timeSpent", timeSpent);
    sessionStorage.setItem("currentQuestionIndex", currentQuestionIndex);
  }, [timeSpent, currentQuestionIndex]);

  useEffect(() => {
    // Restore time spent and question index on reload
    const storedTimeSpent = sessionStorage.getItem("timeSpent");
    const storedQuestionIndex = sessionStorage.getItem("currentQuestionIndex");

    if (storedTimeSpent) setTimeSpent(parseInt(storedTimeSpent, 10));
    if (storedQuestionIndex)
      setCurrentQuestionIndex(parseInt(storedQuestionIndex, 10));
  }, []);

  useEffect(() => {
    // fetchQuestions();
    fetchInterviewQuestions();
  }, []);

  // 10 sec popup implement

  useEffect(() => {
    if (loading) {
      return;
    }
    const warningThreshold = Math.min(10, Math.floor(currentTimeLimit / 3));

    if (countdown <= warningThreshold && countdown >= 1) {
      if (!toastId.current) {
        toastId.current = toast.warn(
          `You have only ${countdown} seconds left!`,
          {
            position: "top-center",
            autoClose: false,
            hideProgressBar: true,
          }
        );
      } else {
        toast.update(toastId.current, {
          render: `You have only ${countdown} seconds left!`,
        });
      }

      if (countdown === 1 && toastId.current) {
        setTimeout(() => {
          toast.dismiss(toastId.current);
          toastId.current = null;
        }, 900);
      }
    } else if (countdown === 0 && toastId.current) {
      toastId.current = null;
    }
  }, [countdown,networkError]);

  // ************* Get First Question id *********

  useEffect(() => {
    if (getQuestions.length > 0 && !isFirstQuestionSet) {
      const firstQuestion = getQuestions[0];
      const timeLimit = firstQuestion.time_limit || 60;
      setActiveQuestionId(firstQuestion.encoded_id);
      setCurrentTimeLimit(timeLimit);
      setCountdown(timeLimit);
      setIsFirstQuestionSet(true);

      console.log("TimeLimit........", timeLimit);

      sessionStorage.setItem("currentTimeLimit", timeLimit.toString());
      sessionStorage.setItem("countdown", timeLimit.toString());

      // Start the recording for the first question
      startRecording(
        videoRef,
        mediaRecorderRef,
        audioRecorderRef,
        recordedChunksRef,
        recordedAudioChunksRef,
        setIsRecording,
        setCountdown,
        setVideoFilePath,
        setAudioFilePath,
        // student_id,
        zoho_lead_id,
        firstQuestion.encoded_id,
        last_question_id,
        encoded_interview_link_send_count,
        timeLimit
      );
    }
  }, [
    getQuestions,
    isFirstQuestionSet,
    last_question_id,
    zoho_lead_id,
    encoded_interview_link_send_count,
  ]);


  
    
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
  

  const handleSubmit = useCallback(async () => {
    setLoading(true);
    const newQuestionId = getQuestions[currentQuestionIndex]?.encoded_id;
    const isLastQuestion = newQuestionId === last_question_id;
    if (!newQuestionId) {
      console.error("Error: newQuestionId is undefined or invalid.");
      return;
    }

    if (newQuestionId !== activeQuestionId) {
      setActiveQuestionId(newQuestionId);
    }

     if (networkError) {
      if (toastId.current) {
        toast.dismiss(toastId.current);
        toastId.current = null;
      }
      return; // Stop the countdown completely
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
        last_question_id,
        encoded_interview_link_send_count,
        () => {
          try {
            const nextIndex = currentQuestionIndex + 1;
            const nextQuestion = getQuestions[nextIndex];
            const nextTimeLimit = nextQuestion?.time_limit || 60;

            setCurrentTimeLimit(nextTimeLimit);
            setCountdown(nextTimeLimit);

            sessionStorage.setItem(
              "currentTimeLimit",
              nextTimeLimit.toString()
            );
            sessionStorage.setItem("countdown", nextTimeLimit.toString());

            startRecording(
              videoRef,
              mediaRecorderRef,
              audioRecorderRef,
              recordedChunksRef,
              recordedAudioChunksRef,
              setIsRecording,
              setCountdown,
              setVideoFilePath,
              setAudioFilePath,
              zoho_lead_id,
              newQuestionId,
              last_question_id,
              encoded_interview_link_send_count,
              nextTimeLimit
            );
          } catch (err) {
            console.error("Failed to start recording:", err);
          }
        }
      );
      localStorage.setItem("interviewSubmitted", "true");
      if (isLastQuestion) {
        if (!endCountdownStartedRef.current) {
          endCountdownStartedRef.current = true;
          setEndcountdwn(30);
          setLoading(true);
        }
      } else {
        setLoading(false);
      }

      // }
    } catch (error) {
      console.error("Error in handleSubmit:", error);
    }
    // finally {
    //   setLoading(false);
    // }
  }, [
    activeQuestionId,
    getQuestions,
    currentQuestionIndex,
    last_question_id,
    submitExam,
    zoho_lead_id,
    navigate,
    encoded_interview_link_send_count,
  ]);


  // ************* Handle Countdown *************
useEffect(() => {
  const handleNextQuestion = async () => {

    if (networkError) {
      console.log(' Network error exists - skipping question transition');
      return;
    }

    const currentQId = getQuestions[currentQuestionIndex]?.encoded_id;
    const isLastQuestion = currentQId === last_question_id;

    if (isLastQuestion) {
      //  Last question - upload in background and show countdown
      if (!endCountdownStartedRefTwo.current) {
        endCountdownStartedRefTwo.current = true;
        setEndcountdwnTwo(30);
        setLoading(true);

        // Upload last question in background
        stopRecording(
          videoRef,
          mediaRecorderRef,
          audioRecorderRef,
          recordedChunksRef,
          recordedAudioChunksRef,
          setVideoFilePath,
          setAudioFilePath,
          zoho_lead_id,
          currentQId,
          last_question_id,
          encoded_interview_link_send_count
        ).catch((err) => console.error("Upload failed:", err));
      }
    } else {
      //  Not last question - move to next immediately
      const nextIndex = currentQuestionIndex + 1;
      const nextQuestion = getQuestions[nextIndex];
      const nextQId = nextQuestion?.encoded_id;
      const nextTimeLimit = nextQuestion?.time_limit || 60;

      // Stop current recording (uploads in background)
      stopRecording(
        videoRef,
        mediaRecorderRef,
        audioRecorderRef,
        recordedChunksRef,
        recordedAudioChunksRef,
        setVideoFilePath,
        setAudioFilePath,
        zoho_lead_id,
        currentQId,
        last_question_id,
        encoded_interview_link_send_count,
        async () => {
          //  This callback runs immediately after blob is created
          console.log(" Moving to next question:", nextQId);

          // Update UI immediately
          setCurrentQuestionIndex(nextIndex);
          setActiveQuestionId(nextQId);
          setCurrentTimeLimit(nextTimeLimit);
          setCountdown(nextTimeLimit);

          if (swiperRef.current) {
            swiperRef.current.slideTo(nextIndex);
          }

          // Update session storage
          sessionStorage.setItem("currentTimeLimit", nextTimeLimit.toString());
          sessionStorage.setItem("countdown", nextTimeLimit.toString());
          sessionStorage.setItem("currentQuestionIndex", nextIndex.toString());

          hasHandledZeroRef.current = false;

          //  Start new recording immediately (don't wait for upload)
          try {
            await startRecording(
              videoRef,
              mediaRecorderRef,
              audioRecorderRef,
              recordedChunksRef,
              recordedAudioChunksRef,
              setIsRecording,
              setCountdown,
              setVideoFilePath,
              setAudioFilePath,
              zoho_lead_id,
              nextQId,
              last_question_id,
              encoded_interview_link_send_count,
              nextTimeLimit
            );
            console.log(" New recording started for:", nextQId);
          } catch (err) {
            console.error("❌ Failed to start new recording:", err);
          }
        }
      ).catch((err) => console.error("❌ Error stopping recording:", err));
    }
  };

  //  Trigger when countdown hits 0
  if (
    countdown === 0 &&
    getQuestions.length > 0 &&
    !hasHandledZeroRef.current &&
    !loading
  ) {
    hasHandledZeroRef.current = true;
    console.log("⏰ Countdown reached 0, auto-advancing...");
    handleNextQuestion();
  }
}, [
  countdown,
  currentQuestionIndex,
  getQuestions,
  loading,
  videoRef,
  mediaRecorderRef,
  audioRecorderRef,
  recordedChunksRef,
  recordedAudioChunksRef,
  setVideoFilePath,
  setAudioFilePath,
  zoho_lead_id,
  last_question_id,
  submitExam,
  navigate,
  encoded_interview_link_send_count,
]);

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
    const minimumTimeBeforeNav = Math.floor(currentTimeLimit / 2);
    if (timeSpent >= minimumTimeBeforeNav) {
      setIsNavigationEnabled(true);
    } else {
      setIsNavigationEnabled(false);
    }
  }, [timeSpent]);

  // Countdown reach 0
  useEffect(() => {
    if (loading && endCountdown === 0) {
      localStorage.clear();
      sessionStorage.clear();
      // setLoading(false);
      navigate(
        `/interviewsubmitted?lead=${encoded_zoho_lead_id}&link=${encoded_interview_link_send_count}&reason=TIME_ENDED`
      );
    }
  }, [endCountdown, loading]);

  useEffect(() => {
    if (loading && endCountdownTwo === 0) {
      localStorage.clear();
      sessionStorage.clear();
      // setLoading(false);
      navigate(
        `/interviewsubmitted?lead=${encoded_zoho_lead_id}&link=${encoded_interview_link_send_count}&reason=TIME_ENDED`
      );
    }
  }, [endCountdownTwo, loading]);

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
      if (toastId.current) {
        toast.dismiss(toastId.current);
        toastId.current = null;
      }

      const newQuestionIndex = swiper.activeIndex;
      if (newQuestionIndex === undefined) {
        console.error("Error: activeIndex is undefined.");
        return;
      }

      setTimeSpent(0); // Reset time tracker on question change
      setCurrentQuestionIndex(newQuestionIndex); // Update question index

      //  FIX: Get the question object first, then get timeLimit from it
      const newQuestion = getQuestions[newQuestionIndex];
      const newQuestionId = newQuestion?.encoded_id;
      const timeLimit = newQuestion?.time_limit || 60; // ✅ Get time_limit from question object

      if (newQuestionId !== activeQuestionId) {
        setActiveQuestionId(newQuestionId); // Update active question ID
      }

      //  Update time limit and countdown
      setCurrentTimeLimit(timeLimit);
      setCountdown(timeLimit);

      // Store in sessionStorage
      sessionStorage.setItem("currentTimeLimit", timeLimit.toString());
      sessionStorage.setItem("countdown", timeLimit.toString());

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
        last_question_id,
        encoded_interview_link_send_count,
        () => {
          try {
            startRecording(
              videoRef,
              mediaRecorderRef,
              audioRecorderRef,
              recordedChunksRef,
              recordedAudioChunksRef,
              setIsRecording,
              setCountdown,
              setVideoFilePath,
              setAudioFilePath,
              zoho_lead_id,
              newQuestionId,
              last_question_id,
              encoded_interview_link_send_count,
              timeLimit //  Pass the time limit
            );
          } catch (err) {
            console.error("Failed to start recording:", err);
          }
        }
      );

      console.log("last_question_id below", last_question_id);
      console.log("New question time_limit:", timeLimit); // ✅ Debug log

      // ✅ REMOVED: setCountdown(60) - This was overriding the dynamic time limit!
    },
    [
      activeQuestionId,
      getQuestions,
      zoho_lead_id,
      last_question_id,
      videoRef,
      encoded_interview_link_send_count,
    ]
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
        encoded_interview_link_send_count={encoded_interview_link_send_count}
      />
    ),
    [
      activeQuestionId,
      zoho_lead_id,
      last_question_id,
      encoded_interview_link_send_count,
    ]
  );

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
        formData //  Pass formData here
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

  // Go back button via back button browser

  // window.history.pushState(null, null, window.location.href);

  // window.onpopstate = function () {
  //   // Show the confirmation dialog
  //   const userConfirmed = window.confirm(
  //     "Are you sure you want to leave this page? Your interview process will not be saved..."
  //   );

  //   if (!userConfirmed) {
  //     // If user cancels, push the current state again to block navigation
  //     window.history.pushState(null, null, window.location.href);
  //   } else {
  //     if (safe_encoded_zoho_lead_id && safe_encoded_interview_link_send_count) {
  //       reportInterviewExit("NAVIGATION_LEFT");
  //       localStorage.clear();
  //       sessionStorage.clear();
  //       navigate(
  //         `/interviewsubmitted?lead=${safe_encoded_zoho_lead_id}&link=${safe_encoded_interview_link_send_count}&reason=NAVIGATION_LEFT`
  //       );
  //     } else {
  //       if (currentIndex === 0 || isNaN(currentIndex)) {
  //         localStorage.clear();
  //         sessionStorage.clear();
  //         navigate("/goback");
  //       } else {
  //         localStorage.clear();
  //         sessionStorage.clear();
  //         navigate(
  //           `/interviewsubmitted?lead=${encoded_zoho_lead_id}&link=${encoded_interview_link_send_count}&reason=NAVIGATION_LEFT`
  //         );
  //       }
  //     }
  //   }
  // };


useEffect(() => {
  if (popstateHandlerRef.current) return; 
  
  popstateHandlerRef.current = true;
  
  window.history.pushState(null, null, window.location.href);

  const handlePopState = () => {
    const userConfirmed = window.confirm(
      "Are you sure you want to leave this page? Your interview process will not be saved..."
    );

    if (!userConfirmed) {
      window.history.pushState(null, null, window.location.href);
    } else {
      const isFirstQuestion = currentQuestionIndex === 0;

      if (isFirstQuestion) {
        localStorage.clear();
        sessionStorage.clear();
        navigate(
          `/goback?lead=${safe_encoded_zoho_lead_id}&link=${safe_encoded_interview_link_send_count}`,
          { replace: true }
        );
      } else {
        reportInterviewExit("NAVIGATION_LEFT");
        localStorage.clear();
        sessionStorage.clear();
        navigate(
          `/interviewsubmitted?lead=${safe_encoded_zoho_lead_id}&link=${safe_encoded_interview_link_send_count}&reason=NAVIGATION_LEFT`,
          { replace: true }
        );
      }
    }
  };

  window.addEventListener("popstate", handlePopState);

  return () => {
    window.removeEventListener("popstate", handlePopState);
    popstateHandlerRef.current = false;
  };
}, [
  safe_encoded_zoho_lead_id,
  safe_encoded_interview_link_send_count,
  currentQuestionIndex,
  navigate,
]);

  {
    showUploading && (
      <div
        style={{
          position: "fixed",
          top: "20px",
          left: "50%",
          transform: "translateX(-50%)",
          backgroundColor: "#333",
          color: "#fff",
          padding: "10px 20px",
          borderRadius: "5px",
          zIndex: 9999,
        }}
      >
        ⏳ Uploading Answer... Please wait.
      </div>
    );
  }

  useEffect(() => {
    if (loading && endCountdown > 0) {
      const timer = setInterval(() => {
        setEndcountdwn((prev) => prev - 1);
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [loading, endCountdown]);

  useEffect(() => {
    if (loading && endCountdownTwo > 0) {
      const timer = setInterval(() => {
        setEndcountdwnTwo((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  },[loading,endCountdownTwo]);

  if (loading) {
    return (
      <div style={{padding:'10px 20px'}}>
        <div className="logomobile">
          <img src={branding.logo} alt="AI Software" className="h-16" />
        </div>

        <section class="dots-container">
          {/* <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div> */}

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              padding: "10px",
            }}
          >
            <div>
              {endCountdown > 0 ? (
                <h3 className="text-lg sm:text-xl font-semibold text-gray-800 text-center">
                  Please wait, your interview will end in {endCountdown} second
                  {endCountdown !== 1 ? "s" : ""}...
                </h3>
              ) : endCountdownTwo > 0 ? (
                <h3 className="text-lg sm:text-xl font-semibold text-gray-800 text-center">
                  Please wait, your interview will end in {endCountdownTwo}{" "}
                  second{endCountdownTwo !== 1 ? "s" : ""}...
                </h3>
              ) : null}
            </div>
            <br />
            <div>
              <p className="text-sm text-red-600 mt-1 font-medium">
                Do not refresh or close the tab.
              </p>
            </div>
          </div>
        </section>
      </div>
    );
  }

  // Network error page
  if (networkError) {
    return (
      <div className="relative min-h-screen bg-white flex items-center justify-center">
        <div className="max-w-md w-full rounded-lg shadow-lg p-8 connectionlostbgcard">
          <div className="text-center">
            <div className="mb-4">
              <img src={branding.logo} alt="AI Software" className="h-16 mx-auto" />
            </div>
            <h1 className="text-2xl font-bold text-red-600 mb-4">Connection Error</h1>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-gray-700 font-semibold mb-2">
                {networkError.type === 'network_error' 
                  ? "Network Connection Lost" 
                  : networkError.type === 'backend_disconnected'
                  ? "Server Connection Lost"
                  : "Server Error"}
              </p>
              <p className="text-gray-600 text-sm">
                {networkError.type === 'network_error'
                  ? "Your internet connection was interrupted. Please check your connection and refresh the page."
                  : networkError.type === 'backend_disconnected'
                  ? "The server went offline during your interview. Please refresh to reconnect."
                  : `Error: ${networkError.error}`}
              </p>
            </div>
            <p className="text-xs text-gray-500 mt-4">
              Network was lost during your interview. Your progress has been saved. 
              Please contact your Student Manager to reschedule or resume your interview.
            </p>
          </div>
        </div>
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
      <div className="flex justify-between flex-col sm:flex-row px-8 pt-3 sm:pt-3  lg:px-16 items-center">
        <div>
          <h3 className="text-black text-xl sm:text-2xl mb-2">
            <img src={branding.logo} alt="AI Software" className="h-16 sm:h-16" />
          </h3>
          {/* <img src={Logo} alt="Not found" style={{width:'200px'}}/> */}
        </div>
        <div
          className={` px-4 py-2 rounded-2xl text-lg sm:text-2xl font-extrabold transition-all tracking-wider
        ${
          countdown < 30 && !isMobileOrIOS()
            ? "text-red-500 animate-blink"
            : "bg-gradient-to-r from-[#ff80b5] to-[#9089fc] sm:mt-2.5"
        }`}
        >
          {formatTime(countdown)}
        </div>
      </div>

      {/* Main Layout */}
      <div className="relative px-4 pt-4 sm:px-8 sm:pt-8 lg:px-16">
        {/* Swiper for questions */}
        <Swiper
          onSwiper={(swiper) => (swiperRef.current = swiper)}
          pagination={{
            type: "fraction",
            renderFraction: (currentClass, totalClass) =>
              `<span class="${currentClass}"></span> / <span class="${totalClass}"></span>`,
          }}
          navigation={isNavigationEnabled}
          allowSlidePrev={false}
          modules={[Pagination, Navigation, Autoplay]}
          className="mySwiper"
          // style={{ minHeight: "200px" }}
          // autoplay={{
          //   delay: 60000,
          //   disableOnInteraction: false,
          // }}
          autoplay={false}
          onSlideChange={(swiper) => {
            setCurrentIndex(swiper.activeIndex);
            handleQuestionChange(swiper); // if needed
          }} // Pass swiper here
          allowTouchMove={false}
        >
          {getQuestions.map((questionItem, index) => {
            return (
              <SwiperSlide
                key={index}
                className="bg-white pb-6 pt-0 pr-6 pl-6  rounded-lg shadow-lg text-black position-relative"
              >
                <p className="text-base sm:text-lg">{questionItem.question}</p>
                {index === getQuestions.length - 1 && timeSpent >= Math.floor(currentTimeLimit / 2) && (
                  <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="
                 bg-pink-500 text-white px-4 py-2 rounded hover:bg-pink-600 text-sm font-medium
                "
                    style={{
                      position: "absolute",
                      right: "5px",
                      bottom: "20px",
                      minWidth: "100px",
                    }}
                  >
                    Submit
                  </button>
                )}
              </SwiperSlide>
            );
          })}
        </Swiper>
        {currentIndex !== getQuestions.length - 1 && (
          <div className="flex justify-end gap-3 mt-4">
            {/* <button
                  onClick={() => swiperRef.current?.slideNext()} // replace swiperRef with your actual swiper instance
                  className="bg-gray-200 text-black px-4 py-2 rounded hover:bg-gray-300 text-sm font-medium"
                >
                  Skip
                </button> */}
            {(timeSpent >= Math.floor(currentTimeLimit / 2)) && (
              <button
                onClick={() => {
                  swiperRef.current?.slideNext();
                  handleQuestionChange(swiperRef.current);
                }}
                className="bg-pink-500 text-white px-4 py-2 rounded hover:bg-pink-600 text-sm font-medium"
              >
                Next
              </button>
            )}
          </div>
        )}

        {/* Grid Layout for User Info and Video */}
        <div className="grid grid-cols-12 gap-0  h-full sm:gap-8">
          <div
            className="col-span-12 md:col-span-9 bg-white p-2 rounded-xl  text-black  "
            style={{ display: "hidden" }}
          >
             {/* <DeepgramLiveCaptions
              /> */}
              {/* <OpenAIRealtimeMicWS /> */}
          </div>
          <div className="col-span-12 md:col-span-3 bg-white p-2 rounded-xl pt-0 sm:mt-2 text-black interviewPlayer">
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
