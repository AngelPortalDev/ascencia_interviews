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

  const MIN_VERSIONS = {
    Chrome: 81,
    Edge: 79,
    Safari: 14.1,
    Firefox: 25,
    Opera: 36,
    'Chrome for Android': 139,
    'Samsung Internet': 5,
    'Opera Mini': null, 
    'Opera Mobile': 80,
    'UC Browser for Android': 15.5,
    'Android Browser': 139,
    'Firefox for Android': 142,
    QQ: null, 
    Baidu: null,
    KaiOS: 3.1,
};


function getBrowserInfo() {
  const ua = navigator.userAgent;

  if (/Chrome\/(\d+)/.test(ua) && !/Edg|OPR|SamsungBrowser/.test(ua)) {
    return { name: "Chrome", version: parseInt(ua.match(/Chrome\/(\d+)/)[1], 10) };
  }
  if (/Edg\/(\d+)/.test(ua)) {
    return { name: "Edge", version: parseInt(ua.match(/Edg\/(\d+)/)[1], 10) };
  }
  if (/Firefox\/(\d+)/.test(ua)) {
    return { name: "Firefox", version: parseInt(ua.match(/Firefox\/(\d+)/)[1], 10) };
  }
  if (/Safari\/(\d+)/.test(ua) && /Version\/(\d+(\.\d+)?)/.test(ua) && !/Chrome/.test(ua)) {
    // Safari version is in Version/x.x format
    return { name: "Safari", version: parseFloat(ua.match(/Version\/(\d+(\.\d+)?)/)[1]) };
  }
  if (/OPR\/(\d+)/.test(ua)) {
    return { name: "Opera", version: parseInt(ua.match(/OPR\/(\d+)/)[1], 10) };
  }
  if (/SamsungBrowser\/(\d+)/.test(ua)) {
    return { name: "Samsung Internet", version: parseInt(ua.match(/SamsungBrowser\/(\d+)/)[1], 10) };
  }
  // Add more if needed, or default:
  return { name: "Unknown", version: 0 };
}

useEffect(() => {
  const currentPath = window.location.pathname;
  if (currentPath === "/frontend/notSupported") return;

  // MediaRecorder support basic check
  const isMediaRecorderUnsupported =
    !window.MediaRecorder ||
    typeof MediaRecorder.isTypeSupported !== "function" ||
    !MediaRecorder.isTypeSupported("video/webm;codecs=vp8");

  if (isMediaRecorderUnsupported) {
    alert("This browser does not support MediaRecorder.");
    window.location.replace("/frontend/notSupported");
    return;
  }

  const { name, version } = getBrowserInfo();

  // Compare with minimum supported versions
  const minVersion = MIN_VERSIONS[name];

  if (minVersion === null || minVersion === undefined) {
    // Browser not recognized or no support data => show warning
    alert("This browser is not supported. Please use a supported browser.");
    window.location.replace("/frontend/notSupported");
    return;
  }

  if (version < minVersion) {
    alert(`Your browser version (${version}) is not supported. Please update to version ${minVersion} or later.`);
    window.location.replace("/frontend/notSupported");
  }

}, []);



// useEffect(() => {
//   const currentPath = window.location.pathname;
//   if (currentPath === "/frontend/notSupported") return;

//   const ua = navigator.userAgent;

//   const isIE = ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;

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

//   // ✅ Correct check: returns TRUE if browser does NOT support MediaRecorder properly
//   const isMediaRecorderUnsupported =
//     !window.MediaRecorder ||
//     typeof MediaRecorder.isTypeSupported !== "function" ||
//     !MediaRecorder.isTypeSupported("video/webm;codecs=vp8");

//   // Optionally: Chrome version check
//   const rawChrome = ua.match(/Chrom(e|ium)\/([0-9]+)\./);
//   const chromeVersion = rawChrome ? parseInt(rawChrome[2], 10) : null;
//   const isOldChrome = chromeVersion && chromeVersion < 70;

//   if (
//     isIE ||
//     isOldAndroidBrowser ||
//     isBadBrowser ||
//     isSafariOnIOS ||
//     isMediaRecorderUnsupported ||
//     isOldChrome
//   ) {
//     alert("This browser is not supported. Please use the latest version of Chrome or Firefox.");
//     window.location.replace("/frontend/notSupported");
//   }
// }, []);

  

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
          <Route path="*" element={<NotFound />} />
          <Route path="/studentfaceenrollment"  element={<ProtectedRoute element={<StudentFaceEnrollment/>} isAllowed={termsAccept && !isExamSubmitted} redirectPath="/permissions"/>}/>
          <Route path="/interviewsubmitted" element={<InterviewSubmitted/>}/>
          <Route path="/expired"  element={<ExpiredPage/>}/>
          <Route path="/goback" element={<Goback/>}/>
          <Route path="/privacy-policy" element={<PrivacyPolicy/>}/>
          <Route path="/notSupported" element={<NotSupported/>}/>
        </Routes>
      </Router>
 
  );
}

export default App;
