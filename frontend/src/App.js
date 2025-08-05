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

 useEffect(() => {
  const currentPath = window.location.pathname;

  if (currentPath === "/frontend/notSupported") return;

  const ua = navigator.userAgent;

  const isIE = ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;

  const isOldAndroidBrowser =
    (ua.includes("Android") && ua.includes("AppleWebKit") && !ua.includes("Chrome")) ||
    (ua.toLowerCase().includes("samsungbrowser") && !ua.includes("Chrome"));

  const isBadBrowser =
    ua.includes("SamsungBrowser") ||
    ua.includes("UCBrowser") ||
    ua.includes("HeyTapBrowser");

  const isiOS = /iP(hone|ad|od)/.test(ua);

  const isChromeIOS = /CriOS/.test(ua);
  const isFirefoxIOS = /FxiOS/.test(ua);
  const isEdgeIOS = /EdgiOS/.test(ua);

  const isSafariOnIOS =
    isiOS &&
    !isChromeIOS &&
    !isFirefoxIOS &&
    !isEdgeIOS &&
    /Safari/.test(ua) &&
    !/GSA/.test(ua); // Optional: Google Search App

  if (isIE || isOldAndroidBrowser || isBadBrowser || isSafariOnIOS) {
    alert("This browser is not supported. Please use Chrome, Firefox, or another modern browser.");
    window.location.href = "/frontend/notSupported";
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
