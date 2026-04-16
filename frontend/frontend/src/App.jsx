import axios from "axios";
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import "./App.css";
import logo from "./assets/logo.png";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // ✅ RESTORED ORIGINAL WORKING DRAG & DROP HANDLER
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const f = acceptedFiles[0];
    setFile(f);
    setPreview(URL.createObjectURL(f));

    setResult(null);
    setError(null);
    setLoading(false);
  }, []);

  // ✅ RESTORED ORIGINAL DROPZONE CONFIG
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [] },
    multiple: false
  });

  const uploadImage = () => {
    if (!file) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("image", file);

    axios
      .post("http://127.0.0.1:8000/api/classify/", formData)
      .then((res) => setResult(res.data))
      .catch(() => setError("Failed to classify image."))
      .finally(() => setLoading(false));
  };

  return (
    <div className="page">

      {/* NAVBAR */}
      <div className="nav">
        <img src={logo} alt="logo" />
        <h1>Plant Identifier</h1>
      </div>

      {/* DESCRIPTION */}
      <div className="section">
        <div className="inner">
          <p className="descriptionText">
            An AI image classifier built to identify native & invasive Australian plants.
          </p>
        </div>
      </div>

      {/* MAIN CARD */}
      <div className="section">
        <div className="card">

          {/* DRAG & DROP — RESTORED */}
          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? "active" : ""}`}
          >
            <input {...getInputProps()} />
            <p>
              {isDragActive
                ? "Drop the Image Here"
                : "Drag & Drop an Image Here or Tap to Select"}
            </p>
          </div>

          {preview && <img src={preview} alt="preview" className="preview" />}

          <button onClick={uploadImage} className="button">
            {loading ? "Classifying..." : "Classify Plant"}
          </button>

          {error && <p className="error">{error}</p>}

          {/* UPDATED AI RESULT DISPLAY */}
          {result && (
            <div className="resultBox">
              <h3 className="resultTitle">Result</h3>

              <p><strong>Species:</strong> {result.species}</p>
              {/* <p><strong>Species Confidence:</strong> {(result.species_confidence * 100).toFixed(1)}%</p> */}

              <p><strong>Status:</strong> {result.status}</p>
              {/* <p><strong>Status Confidence:</strong> {(result.status_confidence * 100).toFixed(1)}%</p> */}
            </div>
          )}

          <p>Classifications are predictions only and are prone to errors.</p>
        </div>
      </div>

      {/* FOOTER */}
      <div className="footer">
        <div className="inner">
          <p className="footerText">
            Created by Luke A — Powered by React & Django
          </p>
          <p className="footerText">
            Classifier Built with Tensorflow and Trained on Images from the <a href="https://ala.org.au/">Atlas of Living Australia</a>
          </p>
        </div>
      </div>

    </div>
  );
}

export default App;
