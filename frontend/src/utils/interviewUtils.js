import { toast } from "react-toastify";

// Time formatter
export const formatTime = (s) =>
  `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;


export const showOrUpdateWarningToast = (toastRef, secondsLeft) => {
  const message = ` You have only ${secondsLeft} second${
    secondsLeft !== 1 ? "s" : ""
  } left`;

  if (!toastRef.current) {
    toastRef.current = toast.warning(message, {
      autoClose: false,
      closeOnClick: false,
      draggable: false,
    });
  } else {
    toast.update(toastRef.current, { render: message });
  }
};
