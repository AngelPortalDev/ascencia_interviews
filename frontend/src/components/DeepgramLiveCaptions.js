import React, { useState, useRef, useEffect, useCallback } from "react";

const apiKey = process.env.REACT_APP_DEEPGRAM_API_KEY;

const DeepgramLiveCaptions = () => {
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [status, setStatus] = useState("");

  const wsRef = useRef(null);
  const recorderRef = useRef(null);
  const streamRef = useRef(null);
  const clearTimerRef = useRef(null);
  const pingIntervalRef = useRef(null);
  const intentionallyStopped = useRef(false);
  const intentionallyClosed = useRef(false);

  const cleanup = () => {
    intentionallyClosed.current = true;
    intentionallyStopped.current = true;

    if (recorderRef.current) {
      recorderRef.current.stop();
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }

    clearTimeout(clearTimerRef.current);
    clearInterval(pingIntervalRef.current);
  };

  const startTranscription = useCallback(async () => {
    if (!apiKey) {
      console.error("Deepgram API key is missing.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });
      recorderRef.current = mediaRecorder;

      const ws = new WebSocket(
        `wss://api.deepgram.com/v1/listen?model=nova-3&language=en&punctuate=true&interim_results=true`,
        ["token", apiKey]
      );
      wsRef.current = ws;

      ws.onopen = () => {
        intentionallyClosed.current = false;
        intentionallyStopped.current = false;
        console.log("WebSocket connected");
        // setStatus("Listening...");
        mediaRecorder.start(200);

        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ event: "ping" }));
          }
        }, 10000);
      };

      ws.onmessage = (evt) => {
        const msg = JSON.parse(evt.data);
        // console.log("msg",msg);
        const alt = msg.channel?.alternatives?.[0];
        if (alt?.transcript) {
          if (msg.is_final) {
            setTranscript(alt.transcript);
            setInterimTranscript("");

            clearTimeout(clearTimerRef.current);
            clearTimerRef.current = setTimeout(() => {
              setTranscript("");
            }, 2500);
          } else {
            setInterimTranscript(alt.transcript);
          }
        }
      };

      ws.onerror = (err) => {
        console.warn("WebSocket error:", err);
        // setStatus("Disconnected");
        cleanup();
        setTimeout(() => {
          intentionallyClosed.current = false;
          intentionallyStopped.current = false;
          startTranscription();
        }, 1500);
      };

      ws.onclose = () => {
        if (!intentionallyClosed.current) {
          console.warn("WebSocket closed unexpectedly.");
          // setStatus("Disconnected");
          cleanup();
          setTimeout(() => {
            intentionallyClosed.current = false;
            intentionallyStopped.current = false;
            startTranscription();
          }, 1500);
        } else {
          console.log("WebSocket closed intentionally.");
        }
      };

      mediaRecorder.ondataavailable = (ev) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(ev.data);
        }
      };

      mediaRecorder.onstop = () => {
        if (!intentionallyStopped.current) {
          console.warn("MediaRecorder stopped unexpectedly.");
          if (ws.readyState === WebSocket.OPEN) {
            mediaRecorder.start(200);
          }
        }
      };
    } catch (err) {
      console.error("Error starting transcription:", err);
      // setStatus("Initialization failed");
    }
  }, []);

  useEffect(() => {
    startTranscription();

    return () => {
      console.log("Cleaning up transcription on unmount");
      cleanup();
    };
  }, [startTranscription]);

  return (
    <div className="mainDeepfram">
      {/* Optional: Show a status message if not connected */}
      {/* {status !== "Listening..." && status !== "" && (
        <div style={{ fontSize: 14, color: "orange", marginBottom: 8 }}>
          {status}
        </div>
      )} */}

      {/* Captions Display */}
      <div>
          <h4>Listening...</h4>
          <div
            style={{
              borderRadius: "10px",
              padding: "16px",
              fontSize: "18px",
              lineHeight: "1.5",
              color: "#333",
              maxWidth: "700px",
              marginTop: "10px",
              boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
              fontFamily: "Arial, sans-serif",
              minHeight: "60px",
            }}
          >
            {transcript}
            <span style={{ opacity: 0.5 }}>{interimTranscript}</span>
          </div>
      </div>
     
    </div>
  );
};

export default DeepgramLiveCaptions;
