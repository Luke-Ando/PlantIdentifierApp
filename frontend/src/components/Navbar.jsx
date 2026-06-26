import logo from "/plantidentificationlogo.png";

export default function Navbar() {
  return (
    <div className="nav">
      <img src={logo} alt="logo" />
      <h1>Plant Identification</h1>
    </div>
  );
}