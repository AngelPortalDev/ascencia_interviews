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
import ProtectedRoute from "./components/ProtectedRoute.js";
import NotFound from "./components/NotFound.js";

function App() {
  const [hasAgreed, setHasAgreed] = useState(() => {
    return localStorage.getItem("hasAgreed") === "true";
  });

  useEffect(() => {
    localStorage.setItem("hasAgreed", hasAgreed);
  }, [hasAgreed]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          path="/terms-and-conditions"
          element={<TermsAndCondition setHasAgreed={setHasAgreed} />}
        />
        {/* <Route path="/permissions" element={<Permissions />} /> */}
        {/* <Route path="/interview-player" element={<InterviewPlayer/>}/> */}
        {/* <Route exact path="/questions" element={<Questions/>}/> */}
        {/* <Route
          path="/questions"
          element={<ProtectedRoute element={<Questions />} />}
        /> */}
        <Route
          path="/questions"
          element={
            <ProtectedRoute
              element={<Questions />}
              isAllowed={localStorage.getItem("hasPermissions") === "true"}
              redirectTo="/questions"
            />
          }
        />

        <Route
          path="/permissions"
          element={
            <ProtectedRoute element={<Permissions />} isAllowed={hasAgreed} />
          }
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;
