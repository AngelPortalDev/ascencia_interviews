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

function App() {

  const { termsAccept, audioVideoAccepted, isExamSubmitted } = usePermission();


  // const [hasAgreed, setHasAgreed] = useState(() => { 
  //   return localStorage.getItem("hasAgreed") === "true";
  // });

  // useEffect(() => {
  //   localStorage.setItem("hasAgreed", hasAgreed);
  // }, [hasAgreed]);
  

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
          <Route path="/interviewsubmitted" element={<InterviewSubmitted/>}/>
          <Route path="/expired"  element={<ExpiredPage/>}/>
        </Routes>
      </Router>
 
  );
}

export default App;
