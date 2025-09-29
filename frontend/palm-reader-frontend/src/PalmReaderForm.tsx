
import React, { useRef, useState } from "react";
import { Hands, HAND_CONNECTIONS } from "@mediapipe/hands";
import type { Results } from "@mediapipe/hands";
import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";

export default function PalmReaderForm() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [result, setResult] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showCamera, setShowCamera] = useState(false);

  // Helper to send blob to backend
  const sendBlobToBackend = async (blob: Blob) => {
    const formData = new FormData();
    formData.append("file", blob, "hand.jpg");
    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("API error");
      const data = await response.json();
      setResult(data.prediction);
      if (data.image_path) {
        setImageUrl(`http://127.0.0.1:8000/${data.image_path.replace("../", "")}`);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to get prediction.");
    } finally {
      setLoading(false);
    }
  };

  // Helper: Check if hand is open palm (all fingers extended)
  function isOpenPalm(landmarks: any[]): boolean {
    // Thumb: tip (4) is to the right of MCP (2) for right hand, left for left hand
    // Fingers: tip (8,12,16,20) above pip (6,10,14,18) in y-axis
    if (!landmarks || landmarks.length !== 21) return false;
    // Thumb
    const thumbOpen = landmarks[4].x < landmarks[3].x;
    // Other fingers
    const fingersOpen = [8, 12, 16, 20].every((tip, i) => {
      const pip = tip - 2;
      return landmarks[tip].y < landmarks[pip].y;
    });
    return thumbOpen && fingersOpen;
  }

  // Start camera and only capture when open palm is detected
  const handleReadPalm = async () => {
    setError("");
    setResult(null);
    setImageUrl(null);
    setShowCamera(true);
    setLoading(true);

    let stream: MediaStream | null = null;
    let hands: Hands | null = null;
    let animationId: number | null = null;
    let detected = false;

    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      // Wait for video to be ready
      await new Promise((resolve) => {
        if (!videoRef.current) return resolve(null);
        if (videoRef.current.readyState >= 3) return resolve(null);
        videoRef.current.onloadeddata = () => resolve(null);
      });

      // Setup MediaPipe Hands
      hands = new Hands({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
      });
      hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.7,
      });

      hands.onResults((results: Results) => {
        if (!videoRef.current || !canvasRef.current) return;
        // Draw landmarks for feedback (optional)
        const ctx = canvasRef.current.getContext("2d");
        ctx?.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
          drawConnectors(ctx!, results.multiHandLandmarks[0], HAND_CONNECTIONS, { color: '#00FF00', lineWidth: 2 });
          drawLandmarks(ctx!, results.multiHandLandmarks[0], { color: '#FF0000', lineWidth: 1 });
          // Check for open palm
          if (isOpenPalm(results.multiHandLandmarks[0]) && !detected) {
            detected = true;
            // Capture frame
            captureAndSend();
          }
        }
      });

      // Animation loop for hand detection
      const detectLoop = async () => {
        if (!videoRef.current) return;
        await hands!.send({ image: videoRef.current });
        if (!detected) animationId = requestAnimationFrame(detectLoop);
      };

      // Helper to capture and send
      const captureAndSend = () => {
        if (!videoRef.current || !canvasRef.current) return;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        ctx?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        // Stop camera
        const tracks = (videoRef.current.srcObject as MediaStream)?.getTracks();
        tracks?.forEach((track) => track.stop());
        videoRef.current.srcObject = null;
        setShowCamera(false);
        // Convert to blob and send to backend
        canvas.toBlob((blob) => {
          if (!blob) {
            setError("Failed to capture image.");
            setLoading(false);
            return;
          }
          sendBlobToBackend(blob);
        }, "image/jpeg");
      };

      // Start detection loop
      animationId = requestAnimationFrame(detectLoop);

    } catch (err) {
      console.error("Camera error:", err);
      setError("Failed to access camera.");
      setLoading(false);
      setShowCamera(false);
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#FFF0C4] p-4">
      <div className="bg-[#3E0703] p-6 rounded-lg shadow-lg w-full max-w-md border-4 border-[#8C1007]">
        <h2 className="text-2xl font-bold mb-4 text-[#FFF0C4] text-center">
          Palm Reader
        </h2>

        {error && (
          <div className="mb-4 p-2 bg-red-200 text-red-800 rounded text-center">
            {error}
          </div>
        )}

        {/* Live Camera */}
        {showCamera && (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full rounded-lg border-2 border-[#8C1007] mb-4"
          />
        )}

        <canvas ref={canvasRef} className="hidden" />

        {!showCamera && (
          <button
            onClick={handleReadPalm}
            disabled={loading}
            className="w-full py-2 px-4 bg-[#8C1007] hover:bg-[#660B05] text-[#FFF0C4] font-bold rounded transition-colors duration-200 disabled:opacity-50 shadow-md"
          >
            {loading ? "Reading..." : "Read My Palm"}
          </button>
        )}

        {imageUrl && (
          <div className="mt-6 text-center">
            <img
              src={imageUrl}
              alt="Captured Hand"
              className="mx-auto mb-4 rounded-lg border-2 border-[#8C1007] shadow-md"
            />
          </div>
        )}

        {result && (
          <div className="mt-6 p-4 rounded bg-[#660B05] text-[#FFF0C4] text-center">
            {result}
          </div>
        )}
      </div>
    </div>
  );
}