// // ProtectedRoute.jsx
// ProtectedRoute.propTypes = {
//   element: PropTypes.element.isRequired,
//   isAllowed: PropTypes.bool.isRequired,
// };

// export default ProtectedRoute;

// import PropTypes from "prop-types";
// import { Navigate } from "react-router-dom";

// const ProtectedRoute = ({ element, isAllowed, redirectTo = "/terms-and-conditions" }) => {
//   if (!isAllowed) {
//     return <Navigate to={redirectTo} />;
//   }
//   return element;
// };

// ProtectedRoute.propTypes = {
//   element: PropTypes.element.isRequired,
//   isAllowed: PropTypes.bool.isRequired,
//   redirectTo: PropTypes.string, // Allow customizable redirection
// };

// export default ProtectedRoute;


// import { Navigate } from "react-router-dom";
// import {usePermission} from '../context/PermissionContext.js';
// import { toast } from "react-toastify";

// const ProtectedRoute = ({ element, isAllowed, redirectPath  }) => {

//   const { isExamSubmitted } = usePermission();
//   const examSubmitted = localStorage.getItem("interviewSubmitted") === "true";

//   if ((isExamSubmitted || examSubmitted) && redirectPath !== "/interviewsubmitted") {
//     toast.error("You have already submitted the exam.",{hideProgressBar:true});
//     return <Navigate to="/interviewsubmitted" replace />;
//   }

//   return isAllowed ? element :  <Navigate to={redirectPath}/>
// }

// export default ProtectedRoute;


import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { usePermission } from "../context/PermissionContext.js";
import { toast } from "react-toastify";

const ProtectedRoute = ({ element, isAllowed, redirectPath }) => {
  const { isExamSubmitted } = usePermission();
  const [shouldRedirect, setShouldRedirect] = useState(false);
  const [redirectTo, setRedirectTo] = useState(null);

  const examSubmitted = localStorage.getItem("interviewSubmitted") === "true";

  useEffect(() => {
    if ((isExamSubmitted) && redirectPath !== "/interviewsubmitted") {
      // toast.error("You have already submitted the exam.", { hideProgressBar: true });
      setShouldRedirect(true);
      setRedirectTo("/interviewsubmitted");
    }
  }, [isExamSubmitted,redirectPath]);

  if (shouldRedirect) {
    return <Navigate to={redirectTo} replace />;
  }

  return isAllowed ? element : <Navigate to={redirectPath} />;
};

export default ProtectedRoute;