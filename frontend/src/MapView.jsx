import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function MapView() {
  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer
        center={[54.5260, -105.2551]} // Roughly center of North America
        zoom={4}
        style={{ height: "100%", width: "100%" }}
      >
        {/* Base map tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Example marker in New York */}
        <Marker position={[40.7128, -74.0060]}>
          <Popup>
            Example marker in <b>New York</b>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
