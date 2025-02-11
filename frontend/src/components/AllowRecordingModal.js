// import React from 'react'
import PropTypes from "prop-types";

const AllowRecordingModal = ({
  isCheckPermission,
  handleChangeCheck,
  errorMessagePermission,
  handleCloseModal,
  handleSumbitPermission,
}) => {
  return (
    <div>
      <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-start justify-center">
        <div className="bg-white p-6 rounded-lg shadow-lg w-1/3 mt-10">
          <form>
            {/* Checkbox and agreement text */}
            <div className="mt-4 flex items-center space-x-2">
              <input
                type="checkbox"
                checked={isCheckPermission}
                onChange={handleChangeCheck}
                id="agreement"
                className="h-4 w-4 text-indigo-600 border-gray-300 rounded"
              />
              <label htmlFor="agreement" className="text-base text-gray-700">
                Do you agree to start the recording of your video?
              </label>
            </div>
            {/* Error message */}
            <p className="text-red-500 text-sm mt-2">
              {errorMessagePermission}
            </p>

            {/* Buttons */}
            <div className="mt-4 flex justify-end gap-x-4">
              <button
                type="button"
                onClick={handleCloseModal}
                className="rounded-md bg-gray-500 text-white px-4 py-2"
              >
                Close
              </button>
              <button
                type="submit"
                className="rounded-md bg-pink-600 text-white px-4 py-2"
                onClick={handleSumbitPermission}
              >
                Submit
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

AllowRecordingModal.propTypes = {
  isCheckPermission: PropTypes.bool.isRequired,
  handleChangeCheck: PropTypes.func.isRequired,
  errorMessagePermission: PropTypes.string.isRequired,
  handleCloseModal: PropTypes.func.isRequired,
  handleSumbitPermission: PropTypes.func.isRequired,
};

export default AllowRecordingModal;
