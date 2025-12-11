import { useEffect, useRef, useState } from "react";

const DeepgramLiveCaptions = () => {
  const [captions, setCaptions] = useState([]);
  const socketRef = useRef(null);
  const recorderRef = useRef(null);
  const streamRef = useRef(null);
  const pingIntervalRef = useRef(null);
  const recorderWatchdogRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connectWebSocketAndStartRecording = async () => {
    try {
      console.log("🔌 Connecting WebSocket...");
      socketRef.current = new WebSocket(
        "wss://ascencia-interview.com/ws/audio/"
      );

      // PING every 30s
      pingIntervalRef.current = setInterval(() => {
        if (socketRef.current?.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000);

      socketRef.current.onopen = () => {
        console.log("✅ WebSocket connected");

        navigator.mediaDevices
          .getUserMedia({
            audio: true,
            sampleRate: 16000,
            noiseSuppression: true,
          })
          .then((stream) => {
            streamRef.current = stream;
            const recorder = new MediaRecorder(stream, {
              mimeType: "audio/webm;codecs=opus",
              audioBitsPerSecond: 128000,
            });

            recorderRef.current = recorder;

            setCaptions([{ id: "init", text: "🎤 Listening..." }]);

            recorder.ondataavailable = (event) => {
              if (event.data && event.data.size > 0) {
                if (socketRef.current?.readyState === WebSocket.OPEN) {
                  socketRef.current.send(event.data);
                }
              }
            };

            recorder.onerror = (e) =>
              console.error("MediaRecorder error:", e);

            setTimeout(() => {
              try {
                recorder.start(250);
                console.log("🎬 Recorder started after delay");
              } catch (err) {
                console.error("❌ Failed to start recorder:", err);
              }

              // 🕵️ Recorder Watchdog - only restart if actually stopped
              recorderWatchdogRef.current = setInterval(() => {
                if (
                  recorderRef.current &&
                  recorderRef.current.state !== "recording"
                ) {
                  console.warn("🎤 Recorder stopped. Restarting...");
                  try {
                    recorderRef.current.start(250);
                  } catch (e) {
                    console.error("❌ Failed to restart recorder:", e);
                  }
                }
              }, 5000);
            }, 500);
          })
          .catch((err) => {
            console.error("🎤 Microphone access error:", err);
          });
      };

      socketRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.text) {
            const id = Date.now();
            const newCaption = { id, text: data.text };

            setCaptions((prev) => [
              ...prev.filter((cap) => cap.id !== "init"),
              newCaption,
            ]);

            setTimeout(() => {
              setCaptions((prev) =>
                prev.filter((caption) => caption.id !== id)
              );
            }, 2000);
          }
        } catch (err) {
          console.error("❌ Failed to parse message:", err);
        }
      };

      socketRef.current.onerror = (err) => {
        console.error("❌ WebSocket error:", err);
      };

      socketRef.current.onclose = () => {
        console.warn("🔌 WebSocket closed. Attempting to reconnect...");
        cleanup();
        attemptReconnect();
      };
    } catch (err) {
      console.error("❌ WebSocket setup failed:", err);
      attemptReconnect();
    }
  };

  // Reconnect with delay
  const attemptReconnect = () => {
    if (reconnectTimeoutRef.current) return;
    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectTimeoutRef.current = null;
      connectWebSocketAndStartRecording();
    }, 3000);
  };

  // Clean up everything - STOP RECORDER FIRST before closing socket
  const cleanup = () => {
    console.log("🧹 Cleaning up...");
    
    // ⚠️ CRITICAL: Stop recorder FIRST so ondataavailable stops firing
    if (recorderRef.current) {
      try {
        if (recorderRef.current.state === "recording") {
          recorderRef.current.stop();
        }
      } catch (e) {
        console.error("Error stopping recorder:", e);
      }
    }
    recorderRef.current = null;

    // Stop all audio tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch (e) {}
      });
      streamRef.current = null;
    }

    // Clear intervals BEFORE closing socket
    clearInterval(pingIntervalRef.current);
    clearInterval(recorderWatchdogRef.current);

    // NOW close socket safely (no more data being sent)
    if (socketRef.current) {
      try {
        socketRef.current.close();
      } catch (e) {
        console.error("Error closing socket:", e);
      }
    }
    socketRef.current = null;
  };

  useEffect(() => {
    connectWebSocketAndStartRecording();

    return () => {
      cleanup();
      clearTimeout(reconnectTimeoutRef.current);
      console.log("🧹 Component unmounted");
    };
  }, []);

  return (
    <div style={{ background: "#fff", color: "#000", padding: 10 }}>
      <h3>You're Saying:</h3>
      <p style={{ marginTop: "10px" }}>
        {captions.map((cap) => cap.text).join(" ")}
      </p>
    </div>
  );
};

export default DeepgramLiveCaptions;
