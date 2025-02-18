import React, { useState, useEffect } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import Axios from "axios";
import { Pagination, Navigation,Autoplay} from "swiper/modules";
import ChatIcon from "../assest/icons/one.svg";

const Questions = () => {
  const [countdown, setCountdown] = useState(300);
  const [userData, setUserData] = useState(null);

  const [getQuestions, setQuestions] = useState([]);

  const fetchQuestions = async () => {
    const res = await Axios.get(
      "https://192.168.1.15:8000/interveiw-section/interview-questions/"
    );
    setQuestions(res.data.questions);
  };
  useEffect(() => {
    fetchQuestions();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      const mockData = {
        name: "John Doe",
        email: "johndoe@example.com",
        mobile: "123-456-7890",
        jobId: "JOB12345",
      };
      setUserData(mockData);
    };

    fetchData();

    if (countdown > 0) {
      const timer = setInterval(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [countdown]);

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    return `COUNTDOWN =  ${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  if (!userData) {
    return <div>Loading...</div>;
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
      <div className="flex justify-between px-8 pt-12 lg:px-16">
        <div>
          <h3 className="text-black text-3xl">Interview Questions</h3>
        </div>
        <div
          className={` px-4 py-2 rounded-xl text-3xl font-extrabold transition-all tracking-wider
        ${
          countdown < 30
            ? "text-red-500 animate-blink"
            : "bg-gradient-to-r from-[#ff80b5] to-[#9089fc]"
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
          navigation={true}
          modules={[Pagination, Navigation,Autoplay]}
          className="mySwiper"
          autoplay={{
            delay: 30000,
            disableOnInteraction: false,
          }}
        >
          {getQuestions.map((questionItem, index) => {
            return (
              <SwiperSlide
                key={index}
                className="bg-white p-6 rounded-lg shadow-lg text-black position-relative"
              >
                <p>{questionItem.question}</p>
                {index === getQuestions.length - 1 && (
                  <button
                    onClick={() => alert("Form Submitted!")}
                    className="bg-gradient-to-r from-[#ff80b5] to-[#9089fc] text-white text-xl font-semibold py-3 px-8 rounded-xl shadow-lg hover:bg-gradient-to-l transition-all"
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
        <div className="grid grid-cols-12 gap-8 mt-12">
          {/* User Info (8 columns) */}
          <div className="col-span-12 lg:col-span-8 bg-white p-6 rounded-xl shadow-lg text-black border border-gray-200">
            <h3 className="text-2xl font-semibold mb-6 text-center">
              Matt Morgon
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8">
              {/* Mobile No */}
              <div className="chat-notification shadow-md p-3 flex items-center rounded-md">
                <div className="chat-notification-logo-wrapper">
                  <img
                    className="chat-notification-logo rounded-md"
                    src={ChatIcon}
                    alt="ChitChat Logo"
                    style={{ height: "40px" }}
                  />
                </div>
                <div className="chat-notification-content ms-3">
                  <div className="chat-notification-title text-xl font-medium text-black">
                    Mobile No
                  </div>
                  <p className="chat-notification-message">+91 6789354628</p>
                </div>
              </div>

              {/* Email */}
              <div className="chat-notification shadow-md p-3 flex items-center rounded-md">
                <div className="chat-notification-logo-wrapper">
                  <img
                    className="chat-notification-logo rounded-md"
                    src={ChatIcon}
                    alt="ChitChat Logo"
                    style={{ height: "40px" }}
                  />
                </div>
                <div className="chat-notification-content ms-3">
                  <div className="chat-notification-title text-xl font-medium text-black">
                    Email id
                  </div>
                  <p className="chat-notification-message">abc12@gmail.com</p>
                </div>
              </div>

              {/* Job Id */}
              <div className="chat-notification shadow-md p-3 flex items-center rounded-md">
                <div className="chat-notification-logo-wrapper">
                  <img
                    className="chat-notification-logo rounded-md"
                    src={ChatIcon}
                    alt="ChitChat Logo"
                    style={{ height: "40px" }}
                  />
                </div>
                <div className="chat-notification-content ms-3">
                  <div className="chat-notification-title text-xl font-medium text-black">
                    Job Id
                  </div>
                  <p className="chat-notification-message">JOB11223</p>
                </div>
              </div>
            </div>
          </div>

          {/* Video Player (4 columns) */}
          <div className="col-span-12 lg:col-span-4 bg-white p-6 rounded-xl shadow-lg text-black border border-gray-200">
            <h3 className="text-2xl font-semibold mb-6">Instructional Video</h3>
            <div className="relative aspect-w-16 aspect-h-9">
              <iframe
                src="https://www.youtube.com/embed/dQw4w9WgXcQ"
                title="YouTube video"
                frameBorder="0"
                allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="w-full h-full rounded-xl shadow-lg"
              ></iframe>
            </div>
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
