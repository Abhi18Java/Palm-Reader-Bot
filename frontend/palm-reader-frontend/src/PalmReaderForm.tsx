import React, { useRef, useState } from "react";
import bgMystic from "./assets/mystic-bg.png";
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
  const [countdown, setCountdown] = useState<number | null>(null);

  // ✅ Send blob to backend
  const sendBlobToBackend = async (blob: Blob) => {
    console.log("Sending request to backend...");
    const formData = new FormData();
    formData.append("file", blob, "hand.jpg");
    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });
      console.log("Response status:", response.status);
      if (!response.ok) throw new Error("API error");
      const data = await response.json();
      console.log("Response data:", data);
      setResult(data.prediction);
      if (data.image_path) {
        const imageUrl = `http://127.0.0.1:8000${data.image_path}`;
        console.log("Setting image URL:", imageUrl);
        setImageUrl(imageUrl);
      }
    } catch (err) {
      console.error(err);
      setError("Baba kuch samajh nahi paaye beta, haath dhang se dikhaiye! 😏");
    } finally {
      setLoading(false);
    }
  };

  // ✅ Detect open palm (more flexible)
  function isOpenPalm(landmarks: any[]): boolean {
    if (!landmarks || landmarks.length !== 21) return false;

    let extendedCount = 0;

    if (Math.abs(landmarks[4].x - landmarks[3].x) > 0.02) {
      extendedCount++;
    }

    [8, 12, 16, 20].forEach((tip) => {
      const pip = tip - 2;
      if (landmarks[tip].y < landmarks[pip].y + 0.01) {
        extendedCount++;
      }
    });

    return extendedCount >= 3;
  }

  // ✅ Capture snapshot
  const captureAndSend = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    ctx?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    const tracks = (videoRef.current.srcObject as MediaStream)?.getTracks();
    tracks?.forEach((track) => track.stop());
    videoRef.current.srcObject = null;
    setShowCamera(false);

    canvas.toBlob((blob) => {
      if (!blob) {
        setError("Failed to capture image.");
        setLoading(false);
        return;
      }
      sendBlobToBackend(blob);
    }, "image/jpeg");
  };

  // ✅ Countdown
  const startCountdown = () => {
    let timeLeft = 3;
    setCountdown(timeLeft);

    const timer = setInterval(() => {
      timeLeft -= 1;
      if (timeLeft > 0) {
        setCountdown(timeLeft);
      } else {
        clearInterval(timer);
        setCountdown(null);
        captureAndSend();
      }
    }, 1000);
  };

  // ✅ Start palm reading
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
    let stableFrames = 0;

    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      await new Promise((resolve) => {
        if (!videoRef.current) return resolve(null);
        if (videoRef.current.readyState >= 3) return resolve(null);
        videoRef.current.onloadeddata = () => resolve(null);
      });

      hands = new Hands({
        locateFile: (file) =>
          `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
      });
      hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 0,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      hands.onResults((results: Results) => {
        if (!videoRef.current || !canvasRef.current) return;
        const ctx = canvasRef.current.getContext("2d");
        ctx?.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);

        if (
          results.multiHandLandmarks &&
          results.multiHandLandmarks.length > 0
        ) {
          drawConnectors(
            ctx!,
            results.multiHandLandmarks[0],
            HAND_CONNECTIONS,
            { color: "#00FF00", lineWidth: 2 }
          );
          drawLandmarks(ctx!, results.multiHandLandmarks[0], {
            color: "#FF0000",
            lineWidth: 1,
          });

          if (isOpenPalm(results.multiHandLandmarks[0]) && !detected) {
            stableFrames++;
            if (stableFrames >= 2) {
              detected = true;
              startCountdown();
            }
          } else {
            stableFrames = 0;
          }
        }
      });

      const detectLoop = async () => {
        if (!videoRef.current) return;
        await hands!.send({ image: videoRef.current });
        if (!detected) animationId = requestAnimationFrame(detectLoop);
      };

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
    <div
      style={{
        minHeight: "100vh",
        width: "100vw",
        backgroundImage: `url(${bgMystic})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
      }}
    >
      <div
        style={{
          textAlign: "center",
          width: "100%",
          maxWidth: "650px",
          position: "relative",
        }}
      >
        {/* Title */}
        <h1
          style={{
            fontFamily: "'UnifrakturCook', cursive, serif",
            fontWeight: 700,
            fontSize: "3.2rem",
            color: "#FFF1F1",
            letterSpacing: "2px",
            marginBottom: "2rem",
            textShadow: "0 2px 24px #6F00FF, 0 0 8px #FFD700",
          }}
        >
          PALM READER
        </h1>
        <h2>

        </h2>

        {/* Error */}
        {error && (
          <div
            style={{
              marginBottom: "1rem",
              padding: "0.75rem",
              background: "rgba(233,179,251,0.85)",
              color: "#3B0270",
              borderRadius: "0.5rem",
            }}
          >
            {error}
          </div>
        )}

        {/* Camera */}
        {showCamera && (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={{
              width: "100%",
              borderRadius: "0.75rem",
              border: "2px solid #6F00FF",
              marginBottom: "1rem",
            }}
          />
        )}
        <canvas ref={canvasRef} className="hidden" />

        {/* Button */}
        {!showCamera && (
          <button
            onClick={handleReadPalm}
            disabled={loading}
            style={{
              width: "100%",
              maxWidth: "340px",
              padding: "0.9rem 1.5rem",
              fontSize: "1.25rem",
              fontWeight: "bold",
              borderRadius: "2rem",
              background: "linear-gradient(90deg, #E9B3FB 0%, #F7B977 100%)",
              color: "#3B0270",
              border: "none",
              boxShadow: "0 2px 16px rgba(233,179,251,0.25)",
              margin: "2rem auto 0 auto",
              opacity: loading ? 0.6 : 1,
              cursor: loading ? "not-allowed" : "pointer",
              letterSpacing: "1px",
              transition: "all 0.3s ease",
            }}
          >
            {loading ? "Reading..." : "हाथ देख बाबा"}
          </button>
        )}

        {/* Captured Image */}
        {imageUrl && (
          <div style={{ marginTop: "2rem", textAlign: "center" }}>
            <img
              src={imageUrl}
              alt="Captured Hand"
              style={{
                display: "block",
                margin: "0 auto 1.5rem auto",
                borderRadius: "1rem",
                border: "3px solid #6F00FF",
                boxShadow: "0 4px 16px rgba(107,0,255,0.25)",
                maxWidth: "450px",    // ⬅️ increased from 300px to 450px
                width: "90%",         // ⬅️ scales nicely on smaller screens
              }}
            />
          </div>
        )}

        {/* Prediction Result Box */}
        {result && (
          <div
            style={{
              marginTop: "2.5rem",
              padding: "2rem",
              borderRadius: "1rem",
              background: "#2a1e4c",
              border: "1px solid rgba(255, 215, 0, 0.4)",
              color: "#FFF1F1",
              textAlign: "left",
              lineHeight: "1.8",
              fontSize: "1.05rem",
              boxShadow: "0 4px 24px rgba(111, 0, 255, 0.25)",
              fontFamily: "'Poppins', sans-serif",
              whiteSpace: "pre-line",
              letterSpacing: "0.3px",
              maxHeight: "60vh",
              overflowY: "auto",
              scrollbarWidth: "none",
              msOverflowStyle: "none",
              width: "90vw",
              maxWidth: "1000px",
              marginLeft: "auto",
              marginRight: "auto",
              position: "relative",
              left: "50%",
              transform: "translateX(-50%)",
            }}
          >
            <h2
              style={{
                fontFamily: "'UnifrakturCook', cursive",
                color: "#FFD700",
                fontSize: "1.8rem",
                marginBottom: "1rem",
                textAlign: "center",
                textShadow: "0 0 12px #FFD700",
              }}
            >
              🔮 Baba’s Reading 🔮
            </h2>
            <div style={{ padding: "0 0.75rem" }}>{result}</div>
          </div>
        )}

      </div>

      {/* Countdown Overlay */}
      {countdown !== null && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
            color: "white",
            fontSize: "5rem",
            fontWeight: "bold",
          }}
        >
          {countdown}
        </div>
      )}
    </div>
  );
}
