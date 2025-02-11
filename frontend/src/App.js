import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import Home from "./components/Home.js";
import TermsAndCondition from "./components/TermsAndCondition.js";
import Permissions from "./components/Permissions.js";
import InterviewPlayer from "./components/InterviewPlayer.js";

function App() {
  return (
    <Router>
      <Routes>
          <Route path="/home" element={<Home />} /> 
          <Route path="/terms-and-conditions" element={<TermsAndCondition />} /> 
          <Route path="/permissions" element={<Permissions />} />
          <Route path="/interview-player" element={<InterviewPlayer/>}/>
      </Routes>
    </Router>
  );
}

export default App;
