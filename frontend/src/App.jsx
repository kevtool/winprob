import { Routes, Route } from "react-router-dom";
import BetsPage from "./pages/BetsPage";
import PredictorPage from "./pages/PredictorPage";
import StatsPage from "./pages/StatsPage";
import Header from "./components/Header";


export default function App() {
  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<BetsPage />} />
        <Route path="/bets" element={<BetsPage />} />
        <Route path="/predictor" element={<PredictorPage />} />
        <Route path="/stats" element={<StatsPage />} />
      </Routes>
    </>
  );
}