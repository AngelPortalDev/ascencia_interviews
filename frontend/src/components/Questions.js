/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect, useRef } from "react";
import { toast } from "react-toastify";
import { useLocation, useNavigate } from "react-router-dom";
import Axios from "axios";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import { initDaily } from "../utils/initDaily.js";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { startRecordingApi, stopRecordingApi } from "../utils/recordingApi.js";
import {
  formatTime,
  showOrUpdateWarningToast,
} from "../utils/interviewUtils.js";
import Logo from "../assest/Logo.png";
import { CompletionPage } from "./CompletionPage.js";
import { useMediaPermissions } from "../utils/useMediaPermissions.js";
import { useInterviewExit } from "../hooks/useInterviewExit.js";
import { useTabSwitchDetection } from "../hooks/useTabSwitchDetection.js";
import { usePageNavigation } from "../hooks/usePageNavigation.js";
import OpenAIRealtimeMicWS from "./OpenAIRealtimeMicWS.js";

const Questions = () => {
  // ================= STATE =================
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [countdown, setCountdown] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingId, setRecordingId] = useState(null);
  const [tokenData, setTokenData] = useState(null);
  const [callJoined, setCallJoined] = useState(false);
  const recordingIdRef = useRef(null);
  const [isRecordingReady, setIsRecordingReady] = useState(false);
  const [initialTime, setInitialTime] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showCompletionPage, setShowCompletionPage] = useState(false);
  const [completionCountdown, setCompletionCountdown] = useState(30);
  const completionTimerRef = useRef(null);

  const [isTimerActive, setIsTimerActive] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const isTransitioningRef = useRef(false);

  const location = useLocation();
  const navigate = useNavigate();

  // ================= SWIPER REF =================
  const swiperRef = useRef(null);

  // ================= ROUTE STATE =================
  const encoded_zoho_lead_id =
    location.state?.encoded_zoho_lead_id ||
    sessionStorage.getItem("zoho_lead_id");

  const encoded_interview_link_send_count =
    location.state?.encoded_interview_link_send_count ||
    sessionStorage.getItem("interview_link_count");

  // ================= REFS =================
  const videoContainerRef = useRef(null);
  const dailyRef = useRef(null);
  const timerRef = useRef(null);
  const hasInitialized = useRef(false);
  const currentQuestionIdRef = useRef(null);
  const warningToastIdRef = useRef(null);

  const { checkMediaPermissions } = useMediaPermissions();
  const {
    isInterviewCompletedRef,
    isTabSwitchExceededRef,
    isNavigatingAwayRef,
    reportInterviewExit,
  } = useInterviewExit(
    encoded_zoho_lead_id,
    encoded_interview_link_send_count,
    currentQuestionIdRef
  );

  // ================= PERSIST PARAMS =================
  useEffect(() => {
    if (encoded_zoho_lead_id) {
      sessionStorage.setItem("zoho_lead_id", encoded_zoho_lead_id);
    }
    if (encoded_interview_link_send_count) {
      sessionStorage.setItem(
        "interview_link_count",
        encoded_interview_link_send_count
      );
    }
  }, [encoded_zoho_lead_id, encoded_interview_link_send_count]);

  const currentQuestionId = questions[currentQuestionIndex]?.encoded_id || null;

  useEffect(() => {
    currentQuestionIdRef.current =
      questions[currentQuestionIndex]?.encoded_id || null;
  }, [currentQuestionIndex, questions]);

  // ================= TAB SWITCH DETECTION =================

  const handleTabSwitchExceeded = async () => {
    try {
      isTabSwitchExceededRef.current = true;
      isInterviewCompletedRef.current = true;

      // Stop recording if active
      if (isRecording) {
        await stopQuestionRecording(currentQuestionIndex + 1);
      }

      // Use the hook's reportInterviewExit function (much cleaner!)
      reportInterviewExit("TAB_SWITCH_EXCEEDED");

      // Clear storage and redirect
      localStorage.clear();
      sessionStorage.clear();

      toast.error("Interview ended due to tab switching violations.", {
        autoClose: 2000,
      });

      setTimeout(() => {
        window.location.replace("/frontend/goback");
      }, 2000);
    } catch (err) {
      console.error("Error handling tab switch exceeded:", err);
      localStorage.clear();
      sessionStorage.clear();
      window.location.replace("/frontend/goback");
    }
  };

  // tab switch detection hook
  useTabSwitchDetection(
    handleTabSwitchExceeded,
    isInterviewCompletedRef.current
  );

  // Navigation detection hook
  usePageNavigation(reportInterviewExit, isInterviewCompletedRef);

  // ================= FETCH QUESTIONS =================
  const fetchInterviewQuestions = async () => {
    try {
      const res = await Axios.post(
        `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-questions/`,
        {
          zoho_lead_id: encoded_zoho_lead_id,
          interview_link_count: encoded_interview_link_send_count,
        },
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      if (!res.data?.questions?.length) {
        throw new Error("No questions received");
      }

      setQuestions(res.data.questions);
      setCurrentQuestionIndex(0);
      setCountdown(res.data.questions[0].time_limit);
      setInitialTime(res.data.questions[0].time_limit);
      return res.data.questions;
    } catch (err) {
      console.error(err);
      throw new Error("Failed to load interview questions");
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        setLoading(true);
        await fetchInterviewQuestions();
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (encoded_zoho_lead_id && encoded_interview_link_send_count) {
      init();
    }
  }, [encoded_zoho_lead_id, encoded_interview_link_send_count]);

  // ================= DAILY TOKEN =================
  const fetchDailyToken = async () => {
    const response = await fetch(
      `${process.env.REACT_APP_API_BASE_URL}api/interveiw-section/daily/token/`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          zoho_lead_id: atob(encoded_zoho_lead_id),
          question_id: currentQuestionId,
        }),
      }
    );
    console.log("response", response);

    if (!response.ok) {
      throw new Error("Failed to fetch Daily token");
    }

    return response.json();
  };

  // ================= START QUESTION RECORDING =================
  const startQuestionRecording = async (questionNumber) => {
    if (!tokenData?.room_name) {
      console.warn("No room name available");
      return;
    }

    if (isRecording && recordingIdRef.current) {
      console.warn("Recording in progress, waiting...");
      await new Promise((resolve) => setTimeout(resolve, 1000));
      if (isRecording) {
        recordingIdRef.current = null;
        setIsRecording(false);
      }
      return;
    }

    try {
      console.log(` Starting recording for Question ${questionNumber}`);

      await new Promise((res) => setTimeout(res, 1500));

      const data = await startRecordingApi(tokenData.room_name, questionNumber);

      const recId = data.recording_id;
      recordingIdRef.current = recId;
      setRecordingId(recId);

      setIsRecording(true);
      setIsRecordingReady(true);

      console.log(` Recording started for Question ${questionNumber}:`, recId);
    } catch (err) {
      console.error(" Failed to start question recording:", err);
      setIsRecordingReady(false);

      if (err.message?.includes("rate-limit") || err.message?.includes("429")) {
        toast.error("Please wait a moment before continuing");
      } else if (
        err.message?.includes("active stream") ||
        err.message?.includes("active-stream")
      ) {
        toast.warning("Previous recording still stopping, please wait...");
        setTimeout(() => startQuestionRecording(questionNumber, true), 3000);
      } else {
        toast.warning("Recording may not have started");
      }
    }
  };

  // ================= STOP QUESTION RECORDING =================
  const stopQuestionRecording = async (questionNumber) => {
    const recIdToUse = recordingIdRef.current || recordingId;

    if (!tokenData?.room_name || !recIdToUse) {
      console.warn("Cannot stop recording - missing room name or recording ID");
      setIsRecording(false);
      setIsRecordingReady(false);
      recordingIdRef.current = null;
      setRecordingId(null);
      return;
    }

    if (!isRecording) {
      console.warn("No active recording to stop");
      return;
    }

    try {
      console.log(` Stopping recording for Question ${questionNumber}`);

      const data = await stopRecordingApi(
        tokenData.room_name,
        recIdToUse,
        questionNumber
      );

      console.log(` Recording stopped for Question ${questionNumber}`);

      setIsRecording(false);
      setIsRecordingReady(false);

      recordingIdRef.current = null;
      setRecordingId(null);

      await new Promise((res) => setTimeout(res, 500));

      return data;
    } catch (err) {
      console.error(" Failed to stop question recording:", err);

      setIsRecording(false);
      setIsRecordingReady(false);
      recordingIdRef.current = null;
      setRecordingId(null);

      toast.warning("Failed to save recording");
    }
  };

  // ================= START RECORDING WHEN CALL JOINS =================
  useEffect(() => {
    if (
      callJoined &&
      tokenData &&
      !isRecording &&
      currentQuestionIndex === 0 &&
      !isTransitioningRef.current
    ) {
      console.log("Call joined - starting recording for Question 1");
      startQuestionRecording(1, true);
    }
  }, [callJoined, tokenData]);

  // ================= INITIAL LOAD =================
  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    const init = async () => {
      try {
        if (!encoded_zoho_lead_id) {
          throw new Error("Invalid interview link");
        }

        await checkMediaPermissions();
        await fetchInterviewQuestions();
        await new Promise((resolve) => setTimeout(resolve, 100));

        const tokenData = await fetchDailyToken();
        setTokenData(tokenData);
        await initDaily({
          tokenData,
          videoContainerRef,
          dailyRef,
          setCallJoined,
          setLoading,
        });
      } catch (err) {
        console.error("Init error:", err);
        setError(err.message);
        toast.error(err.message);
        setLoading(false);
      }
    };

    init();

    return () => {
      clearInterval(timerRef.current);
      if (dailyRef.current) {
        dailyRef.current.destroy();
      }
    };
  }, []);

  // ================= TIMER =================
  useEffect(() => {
    if (!questions.length || loading || !callJoined || isTransitioning) {
      clearInterval(timerRef.current);
      setIsTimerActive(false);
      return;
    }

    const canStartTimer = isRecordingReady || currentQuestionIndex > 0;

    if (!canStartTimer && currentQuestionIndex === 0) {
      clearInterval(timerRef.current);
      setIsTimerActive(false);
      return;
    }

    setIsTimerActive(true);
    clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      setCountdown((prev) => {
        const next = prev - 1;

        if (next <= 0) {
           setTimeout(() => {
              handleNext();
            }, 0);
          return 0;
        }

        if (next <= 10) {
          showOrUpdateWarningToast(warningToastIdRef, next);
        }

        return next;
      });
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, [
    currentQuestionIndex,
    questions,
    loading,
    callJoined,
    isRecordingReady,
    isTransitioning,
  ]);

  useEffect(() => {
    if (countdown > 10 && warningToastIdRef.current) {
      toast.dismiss(warningToastIdRef.current);
      warningToastIdRef.current = null;
    }
  }, [currentQuestionIndex]);

  // ================= COMPLETION PAGE COUNTDOWN =================
  useEffect(() => {
    if (!showCompletionPage) return;

    completionTimerRef.current = setInterval(() => {
      setCompletionCountdown((prev) => {
        const next = prev - 1;

        if (next <= 0) {
          clearInterval(completionTimerRef.current);
          // window.location.href = `/interviewsubmitted?lead=${encoded_zoho_lead_id}&link=${encoded_interview_link_send_count}`;
          navigate(
        `/interviewsubmitted?lead=${encoded_zoho_lead_id}&link=${encoded_interview_link_send_count}`
      );
          return 0;
        }

        return next;
      });
    }, 1000);

    return () => {
      if (completionTimerRef.current) {
        clearInterval(completionTimerRef.current);
      }
    };
  }, [showCompletionPage, encoded_zoho_lead_id]);

  // ================= SUBMIT =================
  const submitInterview = async () => {
    try {
      setIsSubmitting(true);
      setShowCompletionPage(true);
      setCompletionCountdown(30);

      if (dailyRef.current) {
        await dailyRef.current.leave();
        dailyRef.current.destroy();
      }
      isInterviewCompletedRef.current = true;

      // toast.success("Interview submitted");
    } catch (err) {
      console.error("Submit error:", err);
      toast.error("Submission failed");
      setIsSubmitting(false);
      setShowCompletionPage(false);
      isInterviewCompletedRef.current = false;
    }
  };

  // ================= HANDLE SLIDE CHANGE =================
  const handleSlideChange = (swiper) => {
    const newIndex = swiper.activeIndex;

    if (newIndex < currentQuestionIndex) {
      swiper.slideTo(currentQuestionIndex);
      return;
    }

    if (isTransitioningRef.current) {
      swiper.slideTo(currentQuestionIndex);
      return;
    }
    if (warningToastIdRef.current) {
      toast.dismiss(warningToastIdRef.current);
      warningToastIdRef.current = null;
    }

    if (newIndex > currentQuestionIndex) {
      handleNext();
    }
  };

  // ================= NEXT =================
  const handleNext = async () => {
    if (isTransitioningRef.current) {
      console.warn(" Transition already in progress, ignoring");
      return;
    }
    if (warningToastIdRef.current) {
      toast.dismiss(warningToastIdRef.current);
      warningToastIdRef.current = null;
    }

    isTransitioningRef.current = true;
    clearInterval(timerRef.current);
    setIsTimerActive(false);
    setIsTransitioning(true);

    try {
      const currentQ = currentQuestionIndex + 1;
      console.log(`\n === Transitioning from Question ${currentQ} ===`);

      // toast.info("Saving your response...", { autoClose: 1500 });

      await stopQuestionRecording(currentQ);

      recordingIdRef.current = null;
      setRecordingId(null);
      setIsRecording(false);
      setIsRecordingReady(false);

      await new Promise((resolve) => setTimeout(resolve, 1000));

      if (currentQuestionIndex < questions.length - 1) {
        const nextIndex = currentQuestionIndex + 1;
        const nextQ = nextIndex + 1;

        console.log(` Moving to Question ${nextQ}`);

        setCurrentQuestionIndex(nextIndex);
        setCountdown(questions[nextIndex].time_limit);
        setInitialTime(questions[nextIndex].time_limit);

        if (swiperRef.current) {
          swiperRef.current.slideNext();
        }

        startQuestionRecording(nextQ, false);
        setIsTransitioning(false);
        isTransitioningRef.current = false;
      } else {
        console.log(" Last question completed, submitting interview");
        await submitInterview();
      }
    } catch (err) {
      console.error(" Error in handleNext:", err);
      toast.error("Error processing question transition");
      setIsTransitioning(false);
      isTransitioningRef.current = false;
    }
  };

  const isNextEnabled =
    isTimerActive &&
    countdown <= initialTime / 2 &&
    !loading &&
    !isTransitioning;

  const isLastQuestion = currentQuestionIndex === questions.length - 1;

  const isNextArrowEnabled =
  !isLastQuestion &&
  isTimerActive &&
  countdown <= initialTime / 2 &&
  !loading &&
  !isTransitioning;


  // ================= ERROR =================
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
          <p className="text-red-500 mb-4 text-center">{error}</p>
          <button
            className="bg-pink-500 text-white px-4 py-2 rounded w-full hover:bg-pink-600 transition-colors"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // ================= LOADING QUESTIONS =================
  if (!questions.length) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 via-purple-50 to-pink-100">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-pink-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-700 text-lg">Loading interview...</p>
        </div>
      </div>
    );
  }

  // ================= RENDER COMPLETION PAGE =================
  if (showCompletionPage) {
    return <CompletionPage completionCountdown={completionCountdown} />;
  }

  const shouldShowLoadingOverlay = isTransitioning || !isTimerActive;



  // ================= UI =================
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-pink-50 via-purple-50 to-pink-100 relative overflow-hidden">
      <div className="w-full h-full flex flex-col">
        {/* Header with Logo and Timer */}
        <div className="w-full px-3 py-3 sm:px-6 sm:py-4">
          <div className="w-full mx-auto">
            <div className="flex justify-between items-center gap-2">
              {/* Logo */}
              <div className="flex items-center flex-shrink-0">
                <img 
                  src={Logo} 
                  alt="AI Software" 
                  className="h-10 xs:h-10 sm:h-12 md:h-16 w-auto object-contain" 
                />
              </div>

              {/* Countdown Timer */}
              <div className="flex-shrink-0">
                <div className="font-bold text-sm xs:text-base sm:text-xl md:text-2xl tracking-wide sm:tracking-wider text-red-500 whitespace-nowrap">
                  <span className="hidden xs:inline">COUNTDOWN = </span>
                  <span className="xs:hidden">⏱ </span>
                  {formatTime(countdown)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex items-center justify-center px-3 py-0 sm:px-6 sm:py-0">
          <div className="w-full  mx-auto">
            {/* Question Container - Centered */}
            <div className="flex flex-col items-center gap-4">
              <div className="w-full  relative">
                {/* Navigation Arrow Left */}
                <button
                  className="absolute left-0 xs:left-1 sm:left-3 md:left-4 top-1/2 -translate-y-1/2 z-10 
                    w-8 h-8 xs:w-10 xs:h-10 sm:w-12 sm:h-12 md:w-14 md:h-14
                    rounded-full bg-white/50 hover:bg-white/70 active:bg-white/80
                    shadow-md flex items-center justify-center 
                    text-gray-300 cursor-not-allowed transition-all
                    touch-manipulation"
                  disabled
                  aria-label="Previous question"
                >
                  <ChevronLeft 
                    className="w-5 h-5 xs:w-6 xs:h-6 sm:w-7 sm:h-7 md:w-9 md:h-9" 
                    strokeWidth={2} 
                  />
                </button>

                {/* Question Card with Swiper */}
                <div className="text-center px-10 xs:px-12 sm:px-16 md:px-20 py-0 sm:py-6 md:py-0">
                  <Swiper
                    modules={[Navigation, Pagination]}
                    spaceBetween={30}
                    slidesPerView={1}
                    allowTouchMove={false}
                    onSwiper={(swiper) => {
                      swiperRef.current = swiper;
                    }}
                    onSlideChange={handleSlideChange}
                    allowSlidePrev={false}
                    simulateTouch={false}
                    resistanceRatio={0}
                    className="mb-4 sm:mb-6 md:mb-8"
                  >
                    {questions.map((question, index) => (
                      <SwiperSlide key={question.encoded_id || index}>
                        <h1 className="text-base xs:text-lg sm:text-xl md:text-xl lg:text-xl 
                          font-normal text-gray-700 leading-relaxed
                          break-words hyphens-auto">
                          {question.question}
                        </h1>
                      </SwiperSlide>
                    ))}
                  </Swiper>
                  
                  {/* Question Counter */}
                  <p className="text-gray-600 text-sm xs:text-base sm:text-lg md:text-xl font-medium">
                    {currentQuestionIndex + 1} / {questions.length}
                  </p>
                </div>

                {/* Navigation Arrow Right */}
                <button
                  onClick={handleNext}
                  disabled={!isNextArrowEnabled}
                  className={`absolute right-0 xs:right-1 sm:right-3 md:right-4 top-1/2 -translate-y-1/2 z-10 
                    w-8 h-8 xs:w-10 xs:h-10 sm:w-12 sm:h-12 md:w-14 md:h-14
                    rounded-full shadow-lg flex items-center justify-center 
                    transition-all touch-manipulation
                    ${isNextArrowEnabled
                      ? 'bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white cursor-pointer hover:scale-105 active:scale-95' 
                      : 'bg-gray-200 text-gray-400 cursor-not-allowed opacity-60'
                    }`}
                  aria-label="Next question"
                >
                  <ChevronRight 
                    className="w-5 h-5 xs:w-6 xs:h-6 sm:w-7 sm:h-7 md:w-9 md:h-9" 
                    strokeWidth={2.5} 
                  />
                </button>
              </div>

              {/* Next Button - Below Swiper Right Side */}
              <div className="w-full  flex justify-end pt-2">
                <button
                  onClick={handleNext}
                  disabled={!isNextEnabled}
                  className={`px-6 xs:px-8 sm:px-10 md:px-12 py-2.5 xs:py-3 sm:py-3
                    rounded-md font-medium text-sm xs:text-base
                    transition-all shadow-lg
                    touch-manipulation whitespace-nowrap
                    ${isNextEnabled 
                      ? 'bg-pink-500 hover:bg-pink-600 active:bg-pink-700 text-white cursor-pointer hover:shadow-xl active:scale-95' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-60'
                    }`}
                  aria-label={currentQuestionIndex === questions.length - 1 ? 'Submit interview' : 'Next question'}
                >
                  {isTransitioning ? 'Loading...' : 
                   currentQuestionIndex === questions.length - 1 ? 'Submit' : 'Next'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Video Box - Bottom Right (Responsive positioning) */}
        {/* <div>
          <div className="">
                      <OpenAIRealtimeMicWS />
          </div >
          <div className="fixed 
            bottom-16 right-20 xs:bottom-20 xs:right-3
            sm:bottom-6 sm:right-6
            w-52 h-40 xs:w-56 xs:h-40
            sm:w-64 sm:h-48 md:w-72 md:h-52
            bg-gray-900 rounded-lg sm:rounded-xl md:rounded-2xl 
            shadow-xl sm:shadow-2xl overflow-hidden z-20 
            border-2 sm:border-3 md:border-4 border-white
            touch-manipulation">
            <div
              ref={videoContainerRef}
              className="w-full h-full"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            />

            {shouldShowLoadingOverlay && !loading && (
              <div className="absolute inset-0 flex items-center justify-center 
                text-white bg-black bg-opacity-80 z-10 
                rounded-lg sm:rounded-xl md:rounded-2xl">
                <div className="text-center px-3 xs:px-4">
                  {isTransitioning ? (
                    <>
                      <div className="mb-2 xs:mb-3">
                        <div className="w-6 h-6 xs:w-8 xs:h-8 sm:w-10 sm:h-10 
                          border-2 xs:border-3 border-white border-t-transparent 
                          rounded-full animate-spin mx-auto"></div>
                      </div>
                      <p className="text-xs sm:text-sm font-semibold mb-1">
                        Saving your response...
                      </p>
                      <p className="text-xs opacity-75 hidden xs:block">
                        Preparing next question
                      </p>
                    </>
                  ) : (
                    <>
                      <p className="text-xs sm:text-sm">Connecting camera...</p>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div> */}
        {/* Audio + Video Row */}
<div className="w-full  mx-auto px-3 sm:px-6 mt-6">
  <div className="flex flex-col sm:flex-row gap-4 items-stretch">

    {/* OpenAI Realtime Mic - 60% */}
    <div className="w-full sm:w-[70%] bg-white rounded-xl  p-4">
      <OpenAIRealtimeMicWS />
    </div>

    {/* Video Box - 40% */}
    <div className="w-full sm:w-[30%] 
      bg-gray-900 rounded-xl shadow-xl overflow-hidden 
      border-2 border-white relative">

      <div
        ref={videoContainerRef}
        className="w-full h-64 flex items-center justify-center"
      />

      {shouldShowLoadingOverlay && !loading && (
        <div className="absolute inset-0 flex items-center justify-center 
          text-white bg-black bg-opacity-80 z-10 rounded-xl">
          <div className="text-center px-4">
            {isTransitioning ? (
              <>
                <div className="mb-3">
                  <div className="w-8 h-8 border-2 border-white border-t-transparent 
                    rounded-full animate-spin mx-auto"></div>
                </div>
                <p className="text-sm font-semibold">Saving your response...</p>
              </>
            ) : (
              <p className="text-sm">Connecting camera...</p>
            )}
          </div>
        </div>
      )}
    </div>

  </div>
</div>

      
      </div>

      {/* Add spacing at bottom for mobile to prevent video overlap with next button */}
      <div className="h-24 sm:h-0"></div>
    </div>
  );
};

export default Questions;