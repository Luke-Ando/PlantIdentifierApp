export default function ResultBox({ result }) {
  if (!result) return null;

  return (
    <div className="resultBox">
      <h3 className="resultTitle">Result</h3>

      <p>
        <strong>Species:</strong> {result.species}
      </p>

      <p>
        <strong>Confidence:</strong>{" "}
        {(result.species_confidence * 100).toFixed(1)}%
      </p>

      <p>
        <strong>Status:</strong>{" "}
        <span
          className={
            result.status === "NATIVE"
              ? "statusNative"
              : "statusInvasive"
          }
        >
          {result.status}
        </span>
      </p>

      <div className="top3Box">
        <h4>Top 3 Predictions</h4>

        <ul>
          {result.top_3?.map((item, i) => (
            <li key={i}>
              {item.species} — {(item.confidence * 100).toFixed(1)}%
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}