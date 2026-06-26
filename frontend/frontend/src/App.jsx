import { useState } from "react";
import "./App.css";

import Navbar from "./components/Navbar";
import ImageUploader from "./components/ImageUploader";
import ResultBox from "./components/ResultBox";
import Footer from "./components/Footer";

import { useServerStatus } from "./hooks/useServerStatus";
import { classifyImage } from "./services/api";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const {
    serverReady,
    serverLoading,
    retryPing,
  } = useServerStatus();

  const uploadImage = () => {
    if (!file) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    classifyImage(file)
      .then((res) => setResult(res.data))
      .catch(() => setError("Failed to classify image."))
      .finally(() => setLoading(false));
  };

  return (
    <div className="page">

      <Navbar />

      <div className="section">
        <div className="inner">
          <p className="descriptionText">
            An AI image classifier built to identify native & invasive Australian plants.
          </p>
        </div>
      </div>

      <div className="section">

        <ImageUploader
          setFile={setFile}
          preview={preview}
          setPreview={setPreview}
          setResult={setResult}
          setError={setError}
          setLoading={setLoading}
          uploadImage={uploadImage}
          loading={loading}
          serverLoading={serverLoading}
          serverReady={serverReady}
          retryPing={retryPing}
          error={error}
        >
          <ResultBox result={result} />
        </ImageUploader>

      </div>

      <Footer />

    </div>
  );
}

export default App;