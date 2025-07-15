// BasicInstruction.js
import {
  Dialog,
  DialogBackdrop,
  DialogPanel,
  DialogTitle,
} from "@headlessui/react";

const BasicInstruction = ({ open, onClose }) => {
  return (
    <Dialog open={open} onClose={onClose} className="relative z-10">
      <DialogBackdrop
        transition
        className="fixed inset-0 bg-gray-500/75 transition-opacity data-closed:opacity-0 data-enter:duration-300 data-enter:ease-out data-leave:duration-200 data-leave:ease-in"
      />

      <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
          <DialogPanel
            transition
            className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all data-closed:translate-y-4 data-closed:opacity-0 data-enter:duration-300 data-enter:ease-out data-leave:duration-200 data-leave:ease-in sm:my-8 sm:w-full sm:max-w-2xl data-closed:sm:translate-y-0 data-closed:sm:scale-95"
          >
            <div className="bg-white px-6 py-5 sm:p-6 sm:pb-4">
              <div className="sm:flex sm:items-start">
                <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                  <DialogTitle
                    as="h3"
                    className="text-xl font-semibold text-blue-600 mb-4"
                  >
                    Basic Instructions
                  </DialogTitle>
                  <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <span className="text-green-600">✓</span>
                        <p className="text-gray-700 text-justify leading-5">
                        Do not close the browser during the interview process. Doing so may result in disqualification.
                        </p>
                    </div>
                    <div className="flex items-start gap-3">
                        <span className="text-green-600">✓</span>
                        <p className="text-gray-700 text-justify leading-5">
                        Do not switch tabs, minimize the window, or allow your device to enter sleep mode while the interview is in progress.
                        Continuous monitoring is essential for accurate evaluation.
                        </p>
                    </div>
                    <div className="flex items-start gap-3">
                        <span className="text-green-600">✓</span>
                        <p className="text-gray-700 text-justify leading-5">
                            Please speak clearly and slightly louder than usual to ensure your responses are captured accurately by the microphone.
                        </p>
                    </div>
                    <div className="flex items-start gap-3">
                          <span className="text-green-600">✓</span>
                          <p className="text-gray-700 text-justify leading-5">
                          Avoid noisy locations, background conversations,
                        or moving out of the computer frame.
                        If detected, the test will be automatically cancelled.
                          </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
              <button
              onClick={onClose}
                type="button"
                className="inline-flex w-full justify-center rounded-md bg-pink-600 px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-pink-500 sm:ml-3 sm:w-auto"
              >
                Ok
              </button>
            </div>
          </DialogPanel>
        </div>
      </div>
    </Dialog>
  );
};

export default BasicInstruction;
