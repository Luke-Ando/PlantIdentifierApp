import axios from "axios";
import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const uploadImage = () => {
    const formData = new FormData();
    formData.append("image", file);

    axios.post("https://plantidentifierapp.onrender.com/api/classify/", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    })
    .then(res => setResult(res.data))
    .catch(err => console.error(err));
  };

  return (
    <div>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button onClick={uploadImage}>Classify</button>

      {result && (
        <p>
          Class: {result.class}<br />
          Confidence: {result.confidence.toFixed(3)}
        </p>
      )}
    </div>
  );
}

export default App;
