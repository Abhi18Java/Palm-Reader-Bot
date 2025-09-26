import React, { useRef, useState } from "react";

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

  // Start camera and auto-capture after 2 seconds
  const handleReadPalm = async () => {
    setError("");
    setResult(null);
    setImageUrl(null);
    setShowCamera(true);
    setLoading(true);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
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

      // Wait 2 seconds for user to show hand
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Capture frame
      if (videoRef.current && canvasRef.current) {
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
      } else {
        setError("Camera not ready.");
        setLoading(false);
        setShowCamera(false);
      }
    } catch (err) {
      console.error("Camera error:", err);
      setError("Failed to access camera.");
      setLoading(false);
      setShowCamera(false);
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