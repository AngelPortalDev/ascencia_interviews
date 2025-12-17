// // services/upload.js

// import axios from "axios";


// const getBrowserInfo = () => {
//   const userAgent = navigator.userAgent;
//   let browserName = "Unknown";
//   let fullVersion = "Unknown";

//   if (userAgent.includes("Chrome") && !userAgent.includes("Edg") && !userAgent.includes("OPR")) {
//     browserName = "Chrome";
//     fullVersion = userAgent.match(/Chrome\/([\d.]+)/)?.[1] || "Unknown";
//   } else if (userAgent.includes("Firefox")) {
//     browserName = "Firefox";
//     fullVersion = userAgent.match(/Firefox\/([\d.]+)/)?.[1] || "Unknown";
//   } else if (userAgent.includes("Safari") && !userAgent.includes("Chrome")) {
//     browserName = "Safari";
//     fullVersion = userAgent.match(/Version\/([\d.]+)/)?.[1] || "Unknown";
//   } else if (userAgent.includes("Edg")) {
//     browserName = "Edge";
//     fullVersion = userAgent.match(/Edg\/([\d.]+)/)?.[1] || "Unknown";
//   } else if (userAgent.includes("OPR") || userAgent.includes("Opera")) {
//     browserName = "Opera";
//     fullVersion = userAgent.match(/(OPR|Opera)\/([\d.]+)/)?.[2] || "Unknown";
//   }

//   return {
//     browserName,
//     fullVersion,
//     userAgent
//   };
// };

// let isUploading = false;

// export const uploadFile = async (blob, filename,zoho_lead_id,question_id,last_question_id,encoded_interview_link_send_count) => {
//   console.log("encoded_interview_link_send_count file uplaod" ,encoded_interview_link_send_count);
//   if (isUploading) return;  //  Duplicate Execution
//   isUploading = true;

//   const browserInfo = getBrowserInfo();
//   console.log("Browser Info:", browserInfo);

//   const isInterviewSubmitted = question_id === last_question_id;
//   console.log('question_id',question_id);
  
//   console.log('last_question_id',last_question_id);
//   console.log('isInterviewSubmitted',isInterviewSubmitted);

//   const formData = new FormData();
//   formData.append("file", blob, filename);
//   formData.append("zoho_lead_id",btoa(zoho_lead_id));
//   formData.append("last_question_id",last_question_id);
//   formData.append("is_interview_submitted", isInterviewSubmitted);
//   console.log("isInterviewSubmitted",isInterviewSubmitted);
  
//   formData.append("Browser Name",browserInfo.browserName)
//   formData.append("Browser Version",browserInfo.fullVersion)
  
//   try {
//     const response = await axios.post(
//       `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-video-upload/`,
//       formData,
//       {
//         headers: {
//           "Content-Type": "multipart/form-data",
//         },
//         onUploadProgress: (progressEvent) => {
//           const percentCompleted = Math.round(
//             (progressEvent.loaded * 100) / progressEvent.total
//           );
//           console.log(`Upload progress: ${percentCompleted}%`);
//         }
//       }
//     );
//      console.log("✅ Upload Success Response:", response.data);
//     if (response.data.file_path) {
//       const videoFilePath = response.data.file_path;
//       const audioFilePath = response.data.audio_path || videoFilePath;

//       console.log("Video uploaded successfully. File Path:", videoFilePath);

//       // Call analyzeVideo function after upload is complete
//       await interviewAddVideoPath(videoFilePath, audioFilePath, zoho_lead_id, question_id,last_question_id,isInterviewSubmitted,encoded_interview_link_send_count);
//     } else {
//       console.warn("⚠️ File path is missing in response.");
//     }
//     return response.data.file_path;
//   } catch (error) {
//     console.error("File upload failed:", error);
//   }finally{
//     isUploading = false;
//   }
// };

// // File download function
// export const downloadFile = (blob, filename) => {
//     const url = URL.createObjectURL(blob);
//     const link = document.createElement("a");
//     link.href = url;
//     link.download = filename;
//     document.body.appendChild(link);
//     link.click();
//     document.body.removeChild(link);
//     URL.revokeObjectURL(url);
// };

// // Analyze Video
// let isAnalyzing = false; 
// export const interviewAddVideoPath = async (videoFilePath, audioFilePath,zoho_lead_id,question_id,last_question_id,isInterviewSubmitted,encoded_interview_link_send_count) => {
//   // if (!videoFilePath || !audioFilePath) {
//   //   throw new Error("Video or audio path is missing.");
//   if (isAnalyzing) {
//     return;  
//   }
//   isAnalyzing = true;
//   // }
//   // console.log(zoho_lead_id,"test student");
//   // console.log(question_id,"test question........................");
//   // console.log("isInterviewSubmitted add video path",isInterviewSubmitted)
//   const formData = new FormData();
//   formData.append("video_path", videoFilePath);
//   formData.append("audio_path", audioFilePath); 
//   formData.append("zoho_lead_id", btoa(zoho_lead_id));
//   formData.append("question_id", btoa(question_id));
//   formData.append("last_question_id", btoa(last_question_id));
//   formData.append("is_interview_submitted", isInterviewSubmitted);
//   formData.append("encoded_interview_link_send_count",encoded_interview_link_send_count);
//   // console.log('encoded_interview_link_send_count 11111111111',encoded_interview_link_send_count)
//   try {
//     const response = await axios.post(
//       `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-add-video-path/`,
//       formData,
//       {
//         headers: {
//           "Content-Type": "multipart/form-data",
//         },
//       }
//     );

//      console.log("Video path upload started successfully:", response.data);

//     console.log("Video analysis started successfully:", response.data);
//     return response.data;
//   } catch (error) {
//     console.error("Error analyzing video:", error);
//   }finally {
//     isAnalyzing = false; //  Reset flag after execution
//   }
// };



// ************* Working END ************



// ********************************************** New Started ********************************************


// services/upload.js 

import axios from "axios";

const getBrowserInfo = () => {
  const userAgent = navigator.userAgent;
  let browserName = "Unknown";
  let fullVersion = "Unknown";

  if (userAgent.includes("Chrome") && !userAgent.includes("Edg") && !userAgent.includes("OPR")) {
    browserName = "Chrome";
    fullVersion = userAgent.match(/Chrome\/([\d.]+)/)?.[1] || "Unknown";
  } else if (userAgent.includes("Firefox")) {
    browserName = "Firefox";
    fullVersion = userAgent.match(/Firefox\/([\d.]+)/)?.[1] || "Unknown";
  } else if (userAgent.includes("Safari") && !userAgent.includes("Chrome")) {
    browserName = "Safari";
    fullVersion = userAgent.match(/Version\/([\d.]+)/)?.[1] || "Unknown";
  } else if (userAgent.includes("Edg")) {
    browserName = "Edge";
    fullVersion = userAgent.match(/Edg\/([\d.]+)/)?.[1] || "Unknown";
  } else if (userAgent.includes("OPR") || userAgent.includes("Opera")) {
    browserName = "Opera";
    fullVersion = userAgent.match(/(OPR|Opera)\/([\d.]+)/)?.[2] || "Unknown";
  }

  return {
    browserName,
    fullVersion,
    userAgent
  };
};

//  FIX: Track individual uploads instead of global flag
const activeUploads = new Map();
const activeAnalyses = new Map();

//  Network error tracking and callback
let networkErrorCallback = null;
export const setNetworkErrorCallback = (callback) => {
  networkErrorCallback = callback;
};

//  FIX: Upload with retry logic
export const uploadFile = async (
  blob, 
  filename, 
  zoho_lead_id, 
  question_id, 
  last_question_id, 
  encoded_interview_link_send_count,
  maxRetries = 3
) => {
  // Create unique ID for this specific upload
  const uploadId = `${zoho_lead_id}_${question_id}_${Date.now()}`;
  
  //  If this exact upload is already in progress, return the existing promise
  if (activeUploads.has(uploadId)) {
    console.log(` Upload ${uploadId} already in progress, returning existing promise`);
    return activeUploads.get(uploadId);
  }

  console.log(` Starting new upload: ${uploadId}`);
  
  // Create the upload promise
  const uploadPromise = performUploadWithRetry(
    blob,
    filename,
    zoho_lead_id,
    question_id,
    last_question_id,
    encoded_interview_link_send_count,
    maxRetries,
    uploadId
  );

  // Store it in the Map
  activeUploads.set(uploadId, uploadPromise);

  try {
    const result = await uploadPromise;
    return result;
  } finally {
    // Always cleanup after upload completes (success or failure)
    activeUploads.delete(uploadId);
    console.log(` Cleaned up upload: ${uploadId}`);
  }
};

//  Internal function with retry logic
const performUploadWithRetry = async (
  blob,
  filename,
  zoho_lead_id,
  question_id,
  last_question_id,
  encoded_interview_link_send_count,
  maxRetries,
  uploadId
) => {
  const browserInfo = getBrowserInfo();
  const isInterviewSubmitted = question_id === last_question_id;

  console.log(` Upload ${uploadId} - Interview submitted: ${isInterviewSubmitted}`);

  const formData = new FormData();
  formData.append("file", blob, filename);
  formData.append("zoho_lead_id", btoa(zoho_lead_id));
  formData.append("last_question_id", last_question_id);
  formData.append("is_interview_submitted", isInterviewSubmitted);
  formData.append("Browser Name", browserInfo.browserName);
  formData.append("Browser Version", browserInfo.fullVersion);

  let lastError = null;

  //  Retry loop
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(` Upload attempt ${attempt}/${maxRetries} for ${uploadId}`);

      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-video-upload/`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 120000, //  2 minute timeout
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            console.log(` Upload ${uploadId} progress: ${percentCompleted}%`);
          }
        }
      );

      console.log(` Upload ${uploadId} successful:`, response.data);

      if (response.data.file_path) {
        const videoFilePath = response.data.file_path;
        const audioFilePath = response.data.audio_path || videoFilePath;

        //  Call analyze in background (don't await)
        interviewAddVideoPath(
          videoFilePath,
          audioFilePath,
          zoho_lead_id,
          question_id,
          last_question_id,
          isInterviewSubmitted,
          encoded_interview_link_send_count
        ).catch(error => {
          console.error(` Analysis failed for ${uploadId}:`, error);
          // Silent failure - user doesn't need to know
        });

        return response.data.file_path;
      } else {
        console.warn(` Upload ${uploadId} missing file_path in response`);
        return null;
      }

    } catch (error) {
      lastError = error;
      console.error(` Upload attempt ${attempt}/${maxRetries} failed for ${uploadId}:`, error.message);

      // Network error detection - notify frontend
      if (!error.response || error.code === 'ECONNABORTED' || error.code === 'ENOTFOUND' || !navigator.onLine) {
        console.error(` Network error detected for ${uploadId}`);
        if (networkErrorCallback) {
          networkErrorCallback({
            type: 'network_error',
            uploadId,
            error: error.message,
            attempt
          });
        }
      }
      
      if (error.response && error.response.status >= 400 && error.response.status < 500) {
        console.error(`Client error ${error.response.status}, not retrying`);
        if (networkErrorCallback) {
          networkErrorCallback({
            type: 'api_error',
            uploadId,
            status: error.response.status,
            error: error.response.data?.error || error.message
          });
        }
        break;
      }

      //  Wait before retry (exponential backoff)
      if (attempt < maxRetries) {
        const waitTime = Math.min(1000 * Math.pow(2, attempt - 1), 10000); // Max 10s
        console.log(` Waiting ${waitTime}ms before retry...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
  }

  console.error(` Upload ${uploadId} failed after ${maxRetries} attempts:`, lastError);
  
  //  TODO: Save to IndexedDB for later retry
  await saveFailedUploadToIndexedDB(blob, filename, {
    zoho_lead_id,
    question_id,
    last_question_id,
    encoded_interview_link_send_count,
    error: lastError?.message
  });

  return null; 
};

//  FIX: Same approach for analysis
export const interviewAddVideoPath = async (
  videoFilePath,
  audioFilePath,
  zoho_lead_id,
  question_id,
  last_question_id,
  isInterviewSubmitted,
  encoded_interview_link_send_count
) => {
  const analysisId = `${zoho_lead_id}_${question_id}_analysis`;

  //  Prevent duplicate analysis calls
  if (activeAnalyses.has(analysisId)) {
    console.log(` Analysis ${analysisId} already in progress`);
    return activeAnalyses.get(analysisId);
  }

  console.log(` Starting analysis: ${analysisId}`);

  const analysisPromise = performAnalysis(
    videoFilePath,
    audioFilePath,
    zoho_lead_id,
    question_id,
    last_question_id,
    isInterviewSubmitted,
    encoded_interview_link_send_count,
    analysisId
  );

  activeAnalyses.set(analysisId, analysisPromise);

  try {
    const result = await analysisPromise;
    return result;
  } finally {
    activeAnalyses.delete(analysisId);
    console.log(` Cleaned up analysis: ${analysisId}`);
  }
};

const performAnalysis = async (
  videoFilePath,
  audioFilePath,
  zoho_lead_id,
  question_id,
  last_question_id,
  isInterviewSubmitted,
  encoded_interview_link_send_count,
  analysisId
) => {
  const formData = new FormData();
  formData.append("video_path", videoFilePath);
  formData.append("audio_path", audioFilePath);
  formData.append("zoho_lead_id", btoa(zoho_lead_id));
  formData.append("question_id", btoa(question_id));
  formData.append("last_question_id", btoa(last_question_id));
  formData.append("is_interview_submitted", isInterviewSubmitted);
  formData.append("encoded_interview_link_send_count", encoded_interview_link_send_count);

  try {
    const response = await axios.post(
      `${process.env.REACT_APP_API_BASE_URL}interveiw-section/interview-add-video-path/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        timeout: 60000, // 1 minute timeout
      }
    );

    console.log(` Analysis ${analysisId} completed:`, response.data);
    return response.data;
  } catch (error) {
    console.error(` Analysis ${analysisId} failed:`, error);
    
    // Network error detection
    if (!error.response || error.code === 'ECONNABORTED' || error.code === 'ENOTFOUND' || !navigator.onLine) {
      console.error(` Backend disconnected during analysis for ${analysisId}`);
      if (networkErrorCallback) {
        networkErrorCallback({
          type: 'backend_disconnected',
          analysisId,
          error: error.message
        });
      }
    }
    
    return null;
  }
};

//  IndexedDB backup for failed uploads
const saveFailedUploadToIndexedDB = async (blob, filename, metadata) => {
  try {
    // Check if IndexedDB is available
    if (!window.indexedDB) {
      console.warn(" IndexedDB not available, cannot save backup");
      return;
    }

    const dbName = "interview-backup";
    const storeName = "pending-uploads";

    // Open database
    const openRequest = indexedDB.open(dbName, 1);

    openRequest.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(storeName)) {
        db.createObjectStore(storeName, { keyPath: "id", autoIncrement: true });
      }
    };

    openRequest.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction([storeName], "readwrite");
      const store = transaction.objectStore(storeName);

      const data = {
        blob,
        filename,
        metadata,
        timestamp: new Date().toISOString(),
        retryCount: 0
      };

      store.add(data);
      console.log(" Saved failed upload to IndexedDB for later retry");

      transaction.oncomplete = () => db.close();
    };

    openRequest.onerror = (error) => {
      console.error(" Failed to save to IndexedDB:", error);
    };
  } catch (error) {
    console.error(" IndexedDB backup error:", error);
  }
};


export const retryFailedUploads = () => {
  return new Promise((resolve) => {
    const dbRequest = indexedDB.open("interview-backup", 1);

    dbRequest.onerror = () => {
      console.error("❌ Failed to open IndexedDB");
      resolve();
    };

    dbRequest.onsuccess = async (event) => {
      const db = event.target.result;

      if (!db.objectStoreNames.contains("pending-uploads")) {
        console.log("📦 No pending-uploads store found");
        resolve();
        return;
      }

      const transaction = db.transaction(["pending-uploads"], "readwrite");
      const store = transaction.objectStore("pending-uploads");

      const getAllRequest = store.getAll();

      getAllRequest.onsuccess = async () => {
        const items = getAllRequest.result;

        if (!items || items.length === 0) {
          console.log("📭 No pending uploads found");
          resolve();
          return;
        }

        console.log(` Found ${items.length} pending upload(s). Retrying...`);

        for (const item of items) {
          const { blob, filename, metadata } = item;

          // Retry the upload silently
          const result = await uploadFile(
            blob,
            filename,
            metadata.zoho_lead_id,
            metadata.question_id,
            metadata.last_question_id,
            metadata.encoded_interview_link_send_count
          );

          if (result) {
            // Remove after success
            store.delete(item.id);
            console.log(`✅ Successfully uploaded pending file: ${filename}`);
          } else {
            console.log(`⏳ Upload failed again for: ${filename}`);
          }
        }

        resolve();
      };

      getAllRequest.onerror = () => {
        console.error("❌ Failed to read IndexedDB");
        resolve();
      };
    };
  });
};

// File download function (unchanged)
export const downloadFile = (blob, filename) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};


// window.addEventListener("online", () => retryFailedUploads());
// ********************************************** New End *************************************************