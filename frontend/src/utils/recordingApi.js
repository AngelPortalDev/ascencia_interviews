const API = process.env.REACT_APP_API_BASE_URL;

export const startRecordingApi = async (roomName, questionNumber) => {
  const res = await fetch(
    `${API}api/interveiw-section/daily/start_daily_recording/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room_name: roomName, question_number: questionNumber }),
    }
  );

  if (!res.ok) throw new Error("Start recording failed");
  return res.json();
};

export const stopRecordingApi = async (roomName, recordingId, questionNumber) => {
  const res = await fetch(
    `${API}api/interveiw-section/daily/stop_daily_recording/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        room_name: roomName,
        recording_id: recordingId,
        question_number: questionNumber,
      }),
    }
  );

  if (!res.ok) throw new Error("Stop recording failed");
  return res.json();
};
