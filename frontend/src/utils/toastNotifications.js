import { toast } from "react-toastify";

export const showWarningToast = (message) => {
  toast.warning(message, {
    position: "top-center",
    autoClose: 3000,
    hideProgressBar: true,
  });
};

export const showErrorToast = (message) => {
  toast.error(message, {
    position: "top-center",
    autoClose: 3000,
    hideProgressBar: true,
  });
};


export const showSuccessToast = (message) => {
    toast.success(message, {
    position: "top-right",
    autoClose: 3000,
    hideProgressBar: true,
  });
}