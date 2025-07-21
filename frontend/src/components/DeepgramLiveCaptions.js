import { useEffect, useRef, useState } from "react";

const DeepgramLiveCaptions = () => {
  const [captions, setCaptions] = useState([]);
  const socketRef = useRef(null);
  const recorderRef = useRef(null);

  useEffect(() => {
    const connectWebSocketAndStartRecording = async () => {
      try {
        // Connect to Django WebSocket server
        socketRef.current = new WebSocket(
          "wss://dev.ascencia-interview.com/ws/audio/"
        );

        console.log("websocket connected...");
        socketRef.current.onopen = () => {

          navigator.mediaDevices
            .getUserMedia({ audio: true,sampleRate: 16000,noiseSuppression: true })
            .then((stream) => {
              const recorder = new MediaRecorder(stream, {
                mimeType: "audio/webm;codecs=opus",
                audioBitsPerSecond: 128000,
              });
              recorderRef.current = recorder;

              recorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                  if (socketRef.current?.readyState === WebSocket.OPEN) {
                    socketRef.current.send(event.data);
                  }
                }
              };

              recorder.onerror = (e) =>
                console.error("MediaRecorder error:", e);
              recorder.start(300);
              console.log("🎬 Recorder started");
            })
            .catch((err) => {
              console.error("🎤 Microphone access error:", err);
            });
        };

        socketRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.text) {
              const id = Date.now(); // Unique ID for each caption
              const newCaption = { id, text: data.text };
              setCaptions((prev) => [...prev, newCaption]);
              console.log("newCaption",newCaption);

              // Remove the caption after 10 seconds
              setTimeout(() => {
                setCaptions((prev) =>
                  prev.filter((caption) => caption.id !== id)
                );
              }, 10000);
            }
          } catch (err) {
            console.error("❌ Failed to parse message:", err);
          }
        };

        socketRef.current.onerror = (err) => {
          console.error("❌ WebSocket error:", err);
        };

        socketRef.current.onclose = () => {
          console.log("🔌 WebSocket closed");
        };
      } catch (err) {
        console.error("❌ WebSocket connection failed:", err);
      }
    };

    connectWebSocketAndStartRecording();

    return () => {
      recorderRef.current?.stop();
      socketRef.current?.close();
      console.log("🧹 Cleaned up recorder and WebSocket");
    };
  }, []);

  return (
    <div style={{ background: "#fff", color: "#000", padding: 10 }}>
      <h3>You're Saying:</h3>
      <p style={{marginTop:'10px'}}>{captions.map((cap) => cap.text).join(" ")}</p>
    </div>
  );
};

export default DeepgramLiveCaptions;