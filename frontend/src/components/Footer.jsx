const AUTHOR = import.meta.env.VITE_AUTHOR_NAME;

export default function Footer() {
  return (
    <div className="footer">
      <div className="inner">
        <p className="footerText">
          © {new Date().getFullYear()} {AUTHOR} — All Rights Reserved
        </p>

        <p className="footerText">
          Classifier built with Tensorflow and trained on images from the{" "}
          <a href="https://ala.org.au/">Atlas of Living Australia</a>.
        </p>
      </div>
    </div>
  );
}