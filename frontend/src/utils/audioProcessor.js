export function float32To16BitPCM(float32Array) {
  const buffer = new ArrayBuffer(float32Array.length * 2);
  const view = new DataView(buffer);
  let offset = 0;
  
  for (let i = 0; i < float32Array.length; i++, offset += 2) {
    let s = Math.max(-1, Math.min(1, float32Array[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  
  return buffer;
}

export const recorderWorkletCode = `
  class RecorderProcessor extends AudioWorkletProcessor {
    process(inputs) {
      const input = inputs[0][0];
      if (input) {
        this.port.postMessage(input);
      }
      return true;
    }
  }
  registerProcessor('recorder-processor', RecorderProcessor);
`;