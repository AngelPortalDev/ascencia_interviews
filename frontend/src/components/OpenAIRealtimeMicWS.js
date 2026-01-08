// import React, { useState, useRef, useEffect } from 'react';
// // import './App.css';
// import { float32To16BitPCM, recorderWorkletCode } from '../utils/audioProcessor.js';

// function OpenAIRealtimeMicWS() {
//   const [isRecording, setIsRecording] = useState(false);
//   const [caption, setCaption] = useState('Transcription will appear here...');
//   const [status, setStatus] = useState('Connecting...');
//   const [isPartial, setIsPartial] = useState(false);

//   const socketRef = useRef(null);
//   const audioContextRef = useRef(null);
//   const mediaStreamRef = useRef(null);
//   const isCleaningUpRef = useRef(false);

//   useEffect(() => {
//     startRecording();

//     return () => {
//       stopRecording();
//     };
//   }, []);

//   const startRecording = async () => {
//     try {
//       setStatus('Connecting to server...');
//       const ws = new WebSocket('wss://dev.ascencia-interview.com/ws/transcription/');
//       socketRef.current = ws;
//       console.log('WebSocket URL:', ws);
//       console.log('WS created');
//       console.log('Initial readyState:', ws.readyState);

//       ws.onopen = async () => {
//         setStatus('🎤 Recording...');
//         setIsRecording(true);

//         const stream = await navigator.mediaDevices.getUserMedia({ 
//           audio: {
//             echoCancellation: true,
//             noiseSuppression: true,
//             sampleRate: 16000
//           } 
//         });
//         mediaStreamRef.current = stream;

//         const audioContext = new AudioContext({ sampleRate: 16000 });
//         audioContextRef.current = audioContext;
//         const source = audioContext.createMediaStreamSource(stream);

//         await audioContext.audioWorklet.addModule(
//           URL.createObjectURL(
//             new Blob([recorderWorkletCode], { type: 'application/javascript' })
//           )
//         );

//         const recorderNode = new AudioWorkletNode(audioContext, 'recorder-processor');

//         recorderNode.port.onmessage = (e) => {
//           if (ws.readyState === WebSocket.OPEN) {
//             ws.send(float32To16BitPCM(e.data));
//           }
//         };

//         source.connect(recorderNode);
//         recorderNode.connect(audioContext.destination);
//       };



//       ws.onmessage = (e) => {
//         const data = JSON.parse(e.data);
//         if (data.text) {
//           console.log("User said:", data.text);
//           setCaption(data.text);
//           setIsPartial(data.type === 'partial');
//         }
//       };

//       ws.onerror = (err) => {
//         console.error('WebSocket error:', err);
//         setStatus('Connection error');
//       };

//       ws.onclose = (e) => {
//         setStatus('Connection closed');
//         stopRecording();
//         console.log('WS CLOSED ');
//         console.log('code:', e.code);
//         console.log('reason:', e.reason);
//         console.log('wasClean:', e.wasClean);
//       };

//     } catch (err) {
//       console.error('Error starting recording:', err);
//       setStatus('Failed to start recording');
//     }
//   };

//   const stopRecording = () => {
//     // Prevent multiple cleanup calls
//     if (isCleaningUpRef.current) {
//       console.log('[Cleanup] Already cleaning up, skipping...');
//       return;
//     }
    
//     isCleaningUpRef.current = true;

//     // Stop media stream tracks
//     if (mediaStreamRef.current) {
//       try {
//         mediaStreamRef.current.getTracks().forEach(track => {
//           try {
//             track.stop();
//           } catch (e) {
//             console.log('[Cleanup] Track stop:', e.message);
//           }
//         });
//         mediaStreamRef.current = null;
//       } catch (e) {
//         console.log('[Cleanup] Media stream:', e.message);
//       }
//     }

//     // Close AudioContext safely
//     if (audioContextRef.current) {
//       try {
//         // Check if it's already closed before trying to close
//         if (audioContextRef.current.state !== 'closed') {
//           audioContextRef.current.close()
//             .then(() => {
//               console.log('[Cleanup] AudioContext closed successfully');
//             })
//             .catch((e) => {
//               console.log('[Cleanup] AudioContext close error:', e.message);
//             });
//         } else {
//           console.log('[Cleanup] AudioContext already closed');
//         }
//         audioContextRef.current = null;
//       } catch (e) {
//         console.log('[Cleanup] AudioContext:', e.message);
//       }
//     }

//     // Close WebSocket
//     if (socketRef.current) {
//       try {
//         if (socketRef.current.readyState === WebSocket.OPEN || 
//             socketRef.current.readyState === WebSocket.CONNECTING) {
//           socketRef.current.close();
//         }
//         socketRef.current = null;
//       } catch (e) {
//         console.log('[Cleanup] WebSocket:', e.message);
//       }
//     }

//     setIsRecording(false);
//     setStatus('Recording stopped');
    
//     // Reset cleanup flag after a short delay
//     setTimeout(() => {
//       isCleaningUpRef.current = false;
//     }, 1000);
//   };

//   return (
//     <div className="App">
//       <div className="container">
//       <h1>You're Saying:</h1>

//         {/* <div className="status">{status}</div> */}

//         <div className="caption-container">
//           <p className={`caption ${isPartial ? 'partial' : ''}`}>
//             {caption}
//           </p>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default OpenAIRealtimeMicWS;

// import React, { useState, useRef, useEffect } from 'react';
// import { float32To16BitPCM, recorderWorkletCode } from '../utils/audioProcessor.js';

// function OpenAIRealtimeMicWS() {
//   const [isRecording, setIsRecording] = useState(false);
//   const [caption, setCaption] = useState('Transcription will appear here...');
//   const [status, setStatus] = useState('Idle');
//   const [isPartial, setIsPartial] = useState(false);

//   const socketRef = useRef(null);
//   const audioContextRef = useRef(null);
//   const mediaStreamRef = useRef(null);

//   const isCleaningUpRef = useRef(false);
//   const hasStartedRef = useRef(false); // Prevent double start in Strict Mode
//   const reconnectTimeoutRef = useRef(null);

//   /* ---------------------- EFFECT ---------------------- */
//   useEffect(() => {
//     if (hasStartedRef.current) return;
//     hasStartedRef.current = true;

//     startRecording();

//     return () => {
//       stopRecording();
//       if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
//     };
//   }, []);

//   /* ---------------------- START ---------------------- */
//   const startRecording = async () => {
//     try {
//       if (socketRef.current) return;

//       setStatus('Connecting to server...');

//       const ws = new WebSocket('wss://dev.ascencia-interview.com/ws/transcription/');
//       socketRef.current = ws;

//       // console.log('WS created');

//       ws.onopen = async () => {
//         // console.log('WS OPEN');
//         setStatus('🎤 Recording...');
//         setIsRecording(true);

//         const stream = await navigator.mediaDevices.getUserMedia({
//           audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 16000 },
//         });
//         mediaStreamRef.current = stream;

//         const audioContext = new AudioContext({ sampleRate: 16000 });
//         audioContextRef.current = audioContext;

//         const source = audioContext.createMediaStreamSource(stream);

//         await audioContext.audioWorklet.addModule(
//           URL.createObjectURL(new Blob([recorderWorkletCode], { type: 'application/javascript' }))
//         );

//         const recorderNode = new AudioWorkletNode(audioContext, 'recorder-processor');

//         recorderNode.port.onmessage = (e) => {
//           if (ws.readyState === WebSocket.OPEN) {
//             ws.send(float32To16BitPCM(e.data));
//           }
//         };

//         source.connect(recorderNode);
//         recorderNode.connect(audioContext.destination);
//       };

//       ws.onmessage = (e) => {
//         try {
//           const data = JSON.parse(e.data);
//           if (data?.text) {
//             setCaption(data.text);
//             setIsPartial(data.type === 'partial');
//           }
//         } catch (err) {
//           console.error('Failed to parse WS message:', err);
//         }
//       };

//       ws.onerror = (err) => {
//         console.error('WebSocket error:', err);
//         setStatus('Connection error. Retrying...');
//       };

//       ws.onclose = (e) => {
//         // console.log('WS CLOSED', e.code, e.wasClean);
//         setStatus('Connection closed. Reconnecting...');

//         // Attempt reconnect after short delay
//         if (!isCleaningUpRef.current) {
//           reconnectTimeoutRef.current = setTimeout(() => {
//             // console.log('[Reconnect] Attempting to reconnect...');
//             startRecording();
//           }, 2000);
//         }
//       };
//     } catch (err) {
//       console.error('Start error:', err);
//       setStatus('Failed to start');
//     }
//   };

//   /* ---------------------- STOP ---------------------- */
//   const stopRecording = () => {
//     if (isCleaningUpRef.current) return;
//     isCleaningUpRef.current = true;

//     // console.log('[Cleanup] Stopping recording');

//     // Stop mic
//     if (mediaStreamRef.current) {
//       mediaStreamRef.current.getTracks().forEach((t) => t.stop());
//       mediaStreamRef.current = null;
//     }

//     // Close audio context
//     if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
//       audioContextRef.current.close().catch(() => {});
//       audioContextRef.current = null;
//     }

//     // Close WebSocket
//     if (socketRef.current) {
//       if (socketRef.current.readyState === WebSocket.OPEN) {
//         socketRef.current.close(1000, 'Client stop');
//       }
//       socketRef.current = null;
//     }

//     setIsRecording(false);
//     setStatus('Stopped');

//     // Cleanup reconnect timeout
//     if (reconnectTimeoutRef.current) {
//       clearTimeout(reconnectTimeoutRef.current);
//       reconnectTimeoutRef.current = null;
//     }

//     setTimeout(() => {
//       isCleaningUpRef.current = false;
//     }, 500);
//   };

//   /* ---------------------- UI ---------------------- */
//   return (
//     <div className="App">
//       <div className="container">
//         <h1>You&apos;re Saying:</h1>

//         <p className={`caption ${isPartial ? 'partial' : ''}`}>{caption}</p>

//         {/* <p className="status">{status}</p> */}
//       </div>
//     </div>
//   );
// }

// export default OpenAIRealtimeMicWS;

import React, { useEffect, useRef, useState } from 'react';
import { float32To16BitPCM, recorderWorkletCode } from '../utils/audioProcessor.js';

function OpenAIRealtimeMicWS() {
  const [caption, setCaption] = useState('Transcription will appear here...');
  const [isPartial, setIsPartial] = useState(false);
  const [status, setStatus] = useState('Idle');

  const socketRef = useRef(null);
  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const processorRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const cleaningUpRef = useRef(false);

  useEffect(() => {
    startRecording();
    return () => stopRecording();
  }, []);

  const startRecording = async () => {
    try {
      if (socketRef.current) return;

      setStatus('Connecting...');

      const ws = new WebSocket(
        'wss://dev.ascencia-interview.com/ws/transcription/'
      );
      socketRef.current = ws;

      ws.onopen = async () => {
        setStatus('🎤 Recording...');

        // 🎙️ Mic
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            channelCount: 1,
          },
        });
        mediaStreamRef.current = stream;

        // 🔊 AudioContext (NEVER force sampleRate)
        const AudioContextClass =
          window.AudioContext || window.webkitAudioContext;
        const audioContext = new AudioContextClass();
        audioContextRef.current = audioContext;

        await audioContext.resume();

        const sampleRate = audioContext.sampleRate;
        console.log('Actual sample rate:', sampleRate);

        // 🔑 Send sample rate FIRST
        ws.send(
          JSON.stringify({
            type: 'sample_rate',
            value: sampleRate,
          })
        );

        const source = audioContext.createMediaStreamSource(stream);

        // ===============================
        // AudioWorklet (Chrome / Edge)
        // ===============================
        if (audioContext.audioWorklet && window.AudioWorkletNode) {
          try {
            await audioContext.audioWorklet.addModule(
              URL.createObjectURL(
                new Blob([recorderWorkletCode], {
                  type: 'application/javascript',
                })
              )
            );

            const recorderNode = new AudioWorkletNode(
              audioContext,
              'recorder-processor'
            );

            recorderNode.port.onmessage = (e) => {
              if (ws.readyState === WebSocket.OPEN) {
                ws.send(float32To16BitPCM(e.data));
              }
            };

            source.connect(recorderNode);
            recorderNode.connect(audioContext.destination);
            processorRef.current = recorderNode;
            return;
          } catch (err) {
            console.warn('AudioWorklet failed, falling back', err);
          }
        }

        // ===============================
        // ScriptProcessor (Firefox / Safari)
        // ===============================
        const processor = audioContext.createScriptProcessor(4096, 1, 1);

        processor.onaudioprocess = (e) => {
          const input = e.inputBuffer.getChannelData(0);
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(float32To16BitPCM(input));
          }
        };

        source.connect(processor);
        processor.connect(audioContext.destination);
        processorRef.current = processor;
      };

      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data?.text) {
          setCaption(data.text);
          setIsPartial(data.type === 'partial');
        }
      };

      ws.onclose = () => {
        if (cleaningUpRef.current) return;
        setStatus('Reconnecting...');
        reconnectTimeoutRef.current = setTimeout(startRecording, 2000);
      };
    } catch (err) {
      console.error(err);
      setStatus('Failed to start');
    }
  };

  const stopRecording = () => {
    cleaningUpRef.current = true;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    processorRef.current?.disconnect?.();
    processorRef.current = null;

    mediaStreamRef.current?.getTracks().forEach((t) => t.stop());
    mediaStreamRef.current = null;

    audioContextRef.current?.close().catch(() => {});
    audioContextRef.current = null;

    socketRef.current?.close();
    socketRef.current = null;

    setStatus('Stopped');
    setTimeout(() => (cleaningUpRef.current = false), 300);
  };

  return (
    <div className="App">
      <h1>You&apos;re Saying:</h1>
      <p className={`caption ${isPartial ? 'partial' : ''}`}>{caption}</p>
      <small>{status}</small>
    </div>
  );
}

export default OpenAIRealtimeMicWS;
