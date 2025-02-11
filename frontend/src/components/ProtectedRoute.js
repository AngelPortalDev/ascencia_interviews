// ProtectedRoute.jsx
import PropTypes from "prop-types";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ element, permissionforInterviewPlayer }) => {
  if (!permissionforInterviewPlayer) {
    return <Navigate to="/permissions" />;
  }

  return element;
};

ProtectedRoute.propTypes = {
  element: PropTypes.element.isRequired,
  permissionforInterviewPlayer: PropTypes.bool.isRequired,
};

export default ProtectedRoute;
