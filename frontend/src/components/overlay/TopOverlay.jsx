import ForecastDisplay from "./ForcastDisplay";

export default function TopOverlay({ forecastData, onClose }) {
  if (!forecastData) return null; // nothing to show yet

  return (
    <div className="pointer-events-auto">
      <ForecastDisplay forecastData={forecastData} onClose={onClose} />
    </div>
  );
}
