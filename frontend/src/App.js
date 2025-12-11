import { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Home from "./components/Home.js";
import TermsAndCondition from "./components/TermsAndCondition.js";
import Permissions from "./components/Permissions.js";
import InterviewPlayer from "./components/InterviewPlayer.js";
import Questions from "./components/Questions.js";
import ProtectedRoute from './components/ProtectedRoute.js'
import NotFound from "./components/NotFound.js";
import {usePermission} from "./context/PermissionContext.js";
import ExpiredPage from "./components/ExpiredPage.js";
import  InterviewSubmitted from "./components/InterviewSubmitted.js";
import { ToastContainer } from "react-toastify";
import Goback from './components/Goback.js'
import StudentFaceEnrollment from "./components/StudentFaceEnrollment.js";
import PrivacyPolicy from "./components/PrivacyPolicy.js";
import NotSupported from './components/NotSuppotedBrowser.js'

function App() {

  const { termsAccept, audioVideoAccepted, isExamSubmitted } = usePermission();

  // const [hasAgreed, setHasAgreed] = useState(() => { 
  //   return localStorage.getItem("hasAgreed") === "true";
  // });

  // useEffect(() => {
  //   localStorage.setItem("hasAgreed", hasAgreed);
  // }, [hasAgreed]);

// useEffect(() => {
//   const currentPath = window.location.pathname;
//   if (currentPath === "/frontend/notSupported") return;

//   const ua = navigator.userAgent;

//   const isIE = ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;
//   const isIOS = /iP(hone|ad|od)/.test(ua);

//   const isOldAndroidBrowser =
//     (ua.includes("Android") && ua.includes("AppleWebKit") && !ua.includes("Chrome")) ||
//     (ua.toLowerCase().includes("samsungbrowser") && !ua.includes("Chrome"));

//   const isBadBrowser =
//     ua.includes("SamsungBrowser") ||
//     ua.includes("UCBrowser") ||
//     ua.includes("HeyTapBrowser");

//   const isiOS = /iP(hone|ad|od)/.test(ua);

//   const isChromeIOS = /CriOS/.test(ua);
//   const isFirefoxIOS = /FxiOS/.test(ua);
//   const isEdgeIOS = /EdgiOS/.test(ua);

//   const isSafariOnIOS =
//     isiOS &&
//     !isChromeIOS &&
//     !isFirefoxIOS &&
//     !isEdgeIOS &&
//     /Safari/.test(ua) &&
//     !/GSA/.test(ua);

//      const isSafariIOS =
//         isIOS &&
//         !isChromeIOS &&
//         !isFirefoxIOS &&
//         !isEdgeIOS &&
//         /Safari/.test(ua) &&
//         !/GSA/.test(ua); 

//      let iOSVersion = null;
//       if (isIOS) {
//         const versionMatch = ua.match(/OS (\d+)_/);
//         if (versionMatch && versionMatch[1]) {
//           iOSVersion = parseInt(versionMatch[1], 10);
//         }
//       }

//        const supportsMediaRecorder =
//           window.MediaRecorder &&
//           typeof MediaRecorder.isTypeSupported === "function" &&
//           (
//             MediaRecorder.isTypeSupported("video/mp4") ||
//             MediaRecorder.isTypeSupported("video/mp4;codecs=h264,aac") ||
//             MediaRecorder.isTypeSupported("audio/mp4")
//           );

//       const isUnsupportedIOS =
//       isIOS &&
//       (
//         iOSVersion < 15 ||        
//         !isSafariIOS ||             
//         !supportsMediaRecorder      
//       );

//   //  Correct check: returns TRUE if browser does NOT support MediaRecorder properly
//   const isMediaRecorderUnsupported =
//     !window.MediaRecorder ||
//     typeof MediaRecorder.isTypeSupported !== "function" ||
//     !MediaRecorder.isTypeSupported("video/webm;codecs=vp8");

//   // Optionally: Chrome version check
//   const rawChrome = ua.match(/Chrom(e|ium)\/([0-9]+)\./);
//   const chromeVersion = rawChrome ? parseInt(rawChrome[2], 10) : null;
//   const isOldChrome = chromeVersion && chromeVersion < 70;

// if (
//   isIE ||
//   isOldAndroidBrowser ||
//   isBadBrowser ||
//   isMediaRecorderUnsupported ||
//   isOldChrome ||
//   isUnsupportedIOS 
// ) {
//   alert("This browser is not supported. Please use the latest version of Chrome or Firefox.");
//     window.location.replace("/frontend/notSupported");
//   }
// }, []);
useEffect(() => {
  const currentPath = window.location.pathname;
  if (currentPath === "/frontend/notSupported") return;

  const ua = navigator.userAgent;

  const isiOS = /iP(hone|ad|od)/.test(ua);
  let iOSVersion = null;
  if (isiOS) {
    const match = ua.match(/OS (\d+)_/);
    if (match) iOSVersion = parseInt(match[1], 10);
  }


  const isSafariIOS = /Safari/.test(ua) && !/CriOS|FxiOS|EdgiOS|GSA/.test(ua);
  const isChromeIOS = /CriOS/.test(ua);


  const supportsIOSRecording =
    window.MediaRecorder &&
    typeof MediaRecorder.isTypeSupported === "function" &&
    (
      MediaRecorder.isTypeSupported("video/mp4;codecs=h264,aac") ||
      MediaRecorder.isTypeSupported("video/mp4") 
    );

  const isUnsupportedIOS =
    isiOS &&
    (
      iOSVersion < 15 ||                    
      !(isSafariIOS || isChromeIOS) ||          
      !supportsIOSRecording                    
    );

  const isIE = ua.includes("MSIE ") || ua.includes("Trident/");
  const isBadBrowser = ua.includes("UCBrowser") || ua.includes("HeyTapBrowser") || ua.includes("SamsungBrowser");
  const isOldAndroidBrowser = ua.includes("Android") && ua.includes("AppleWebKit") && !ua.includes("Chrome");

  // Chrome version check
  const chromeMatch = ua.match(/Chrom(e|ium)\/([0-9]+)\./);
  const chromeVersion = chromeMatch ? parseInt(chromeMatch[2], 10) : null;
  const isOldChrome = chromeVersion && chromeVersion < 70;

  const isMediaRecorderUnsupported = !window.MediaRecorder || typeof MediaRecorder.isTypeSupported !== "function";

  if (
    isIE ||
    isOldAndroidBrowser ||
    isBadBrowser ||
    isUnsupportedIOS ||
    isMediaRecorderUnsupported ||
    isOldChrome
  ) {
    alert("This browser is not supported. Please use the latest version of Chrome, Safari, or Firefox.");
    window.location.replace("/frontend/notSupported");
  }
}, []);

  

  return (

      <Router basename="/frontend">
        <ToastContainer/>
        <Routes>
          <Route path="/interview_panel/:encoded_zoho_lead_id/:encoded_interview_link_send_count" element={<Home />} />
          <Route
            path="/terms-and-conditions/"
            element={<ProtectedRoute element={<TermsAndCondition />} isAllowed={!isExamSubmitted} redirectPath="/"/>}/>
          <Route 
          path="/permissions/" 
          element={<ProtectedRoute element={<Permissions/>} isAllowed={termsAccept && !isExamSubmitted} redirectPath="/terms-and-conditions"/>} />

          <Route path="/questions"  element={<ProtectedRoute element={<Questions/>} isAllowed={audioVideoAccepted && !isExamSubmitted} redirectPath="/permissions"/>}/>
         {/* Add Question Router Here */}
         

          <Route path="/studentfaceenrollment"  element={<ProtectedRoute element={<StudentFaceEnrollment/>} isAllowed={termsAccept && !isExamSubmitted} redirectPath="/permissions"/>}/>
          <Route path="/interviewsubmitted" element={<InterviewSubmitted/>}/>
          <Route path="/expired/:zohoLeadId" element={<ExpiredPage />} />

          <Route path="/goback" element={<Goback/>}/>
          <Route path="/privacy-policy" element={<PrivacyPolicy/>}/>
          {/* <Route path="/notSupported" element={<NotSupported/>}/> */}
          <Route path="/notSupported/:encoded_zoho_lead_id" element={<NotSupported />} />
           <Route path="/not-found/:encoded_zoho_lead_id?" element={<NotFound />} />
          <Route path="*" element={<NotFound />} />

        </Routes>
      </Router>
 
  );
}

export default App;
