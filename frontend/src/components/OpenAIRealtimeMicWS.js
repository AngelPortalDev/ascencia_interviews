import React, { useState, useRef, useEffect } from 'react';
// import './App.css';
import { float32To16BitPCM, recorderWorkletCode } from '../utils/audioProcessor.js';

function OpenAIRealtimeMicWS() {
  const [isRecording, setIsRecording] = useState(false);
  const [caption, setCaption] = useState('Transcription will appear here...');
  const [status, setStatus] = useState('Connecting...');
  const [isPartial, setIsPartial] = useState(false);

  const socketRef = useRef(null);
  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const isCleaningUpRef = useRef(false);

  useEffect(() => {
    startRecording();

    return () => {
      stopRecording();
    };
  }, []);

  const startRecording = async () => {
    try {
      setStatus('Connecting to server...');
      const ws = new WebSocket('wss://dev.ascencia-interview.com/ws/transcription/');
      socketRef.current = ws;
      console.log('WebSocket URL:', ws);

      ws.onopen = async () => {
        setStatus('🎤 Recording...');
        setIsRecording(true);

        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 16000
          } 
        });
        mediaStreamRef.current = stream;

        const audioContext = new AudioContext({ sampleRate: 16000 });
        audioContextRef.current = audioContext;
        const source = audioContext.createMediaStreamSource(stream);

        await audioContext.audioWorklet.addModule(
          URL.createObjectURL(
            new Blob([recorderWorkletCode], { type: 'application/javascript' })
          )
        );

        const recorderNode = new AudioWorkletNode(audioContext, 'recorder-processor');

        recorderNode.port.onmessage = (e) => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(float32To16BitPCM(e.data));
          }
        };

        source.connect(recorderNode);
        recorderNode.connect(audioContext.destination);
      };

      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.text) {
          console.log("User said:", data.text);
          setCaption(data.text);
          setIsPartial(data.type === 'partial');
        }
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        setStatus('Connection error');
      };

      ws.onclose = () => {
        setStatus('Connection closed');
        stopRecording();
      };

    } catch (err) {
      console.error('Error starting recording:', err);
      setStatus('Failed to start recording');
    }
  };

  const stopRecording = () => {
    // Prevent multiple cleanup calls
    if (isCleaningUpRef.current) {
      console.log('[Cleanup] Already cleaning up, skipping...');
      return;
    }
    
    isCleaningUpRef.current = true;

    // Stop media stream tracks
    if (mediaStreamRef.current) {
      try {
        mediaStreamRef.current.getTracks().forEach(track => {
          try {
            track.stop();
          } catch (e) {
            console.log('[Cleanup] Track stop:', e.message);
          }
        });
        mediaStreamRef.current = null;
      } catch (e) {
        console.log('[Cleanup] Media stream:', e.message);
      }
    }

    // Close AudioContext safely
    if (audioContextRef.current) {
      try {
        // Check if it's already closed before trying to close
        if (audioContextRef.current.state !== 'closed') {
          audioContextRef.current.close()
            .then(() => {
              console.log('[Cleanup] AudioContext closed successfully');
            })
            .catch((e) => {
              console.log('[Cleanup] AudioContext close error:', e.message);
            });
        } else {
          console.log('[Cleanup] AudioContext already closed');
        }
        audioContextRef.current = null;
      } catch (e) {
        console.log('[Cleanup] AudioContext:', e.message);
      }
    }

    // Close WebSocket
    if (socketRef.current) {
      try {
        if (socketRef.current.readyState === WebSocket.OPEN || 
            socketRef.current.readyState === WebSocket.CONNECTING) {
          socketRef.current.close();
        }
        socketRef.current = null;
      } catch (e) {
        console.log('[Cleanup] WebSocket:', e.message);
      }
    }

    setIsRecording(false);
    setStatus('Recording stopped');
    
    // Reset cleanup flag after a short delay
    setTimeout(() => {
      isCleaningUpRef.current = false;
    }, 1000);
  };

  return (
    <div className="App">
      <div className="container">
      <h1>You're Saying:</h1>

        {/* <div className="status">{status}</div> */}

        <div className="caption-container">
          <p className={`caption ${isPartial ? 'partial' : ''}`}>
            {caption}
          </p>
        </div>
      </div>
    </div>
  );
}

export default OpenAIRealtimeMicWS;