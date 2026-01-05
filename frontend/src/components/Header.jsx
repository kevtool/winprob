import { NavLink } from "react-router-dom";
import "./Header.css";

export default function Header() {
  return (
    <header className="header">
      <nav>
        {/* <NavLink to="/">Home</NavLink> */}
        <NavLink to="/bets">Matches</NavLink>
        <NavLink to="/predictor">Predictor</NavLink>
        <NavLink to="/stats">Stats</NavLink>
      </nav>
    </header>
  );
}