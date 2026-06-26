import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

export default function ImageUploader({
  setFile,
  preview,
  setPreview,
  setResult,
  setError,
  setLoading,
  uploadImage,
  loading,
  serverLoading,
  serverReady,
  retryPing,
  error,
  children
}) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const f = acceptedFiles[0];

    setFile(f);
    setPreview(URL.createObjectURL(f));

    setResult(null);
    setError(null);
    setLoading(false);
  }, [setFile, setPreview, setResult, setError, setLoading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [] },
    multiple: false
  });

  return (
    <div className="card">

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

      {preview && (
        <img
          src={preview}
          alt="preview"
          className="preview"
        />
      )}

      {serverLoading ? (
        <div className="waitingButton">
          Waiting for server...
        </div>
      ) : !serverReady ? (
        <button
          className="retryButtonState"
          onClick={retryPing}
        >
          Server Unreachable — Retry
        </button>
      ) : (
        <button
          onClick={uploadImage}
          className="button"
          disabled={loading}
        >
          {loading ? "Classifying..." : "Classify Plant"}
        </button>
      )}

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      {children}

      <p className="disclaimer">
        Classifications are predictions only and are prone to errors.
        This tool has not been trained to recognise all plant species.
      </p>
    </div>
  );
}