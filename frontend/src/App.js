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

function App() {

  const { termsAccept, audioVideoAccepted } = usePermission();


  // const [hasAgreed, setHasAgreed] = useState(() => { 
  //   return localStorage.getItem("hasAgreed") === "true";
  // });

  // useEffect(() => {
  //   localStorage.setItem("hasAgreed", hasAgreed);
  // }, [hasAgreed]);

  return (

      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/terms-and-conditions"
            element={<TermsAndCondition />}
          />
          <Route 
          path="/permissions" 
          element={<ProtectedRoute element={<Permissions/>} isAllowed={termsAccept} redirectPath="/terms-and-conditions"/>} />

          <Route path="/questions" 
          element={<ProtectedRoute element={<Questions/>} isAllowed={audioVideoAccepted} redirectPath="/permissions"/>}/>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
 
  );
}

export default App;
