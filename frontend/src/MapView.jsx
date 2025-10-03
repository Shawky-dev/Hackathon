import { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvent } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix default marker icon paths for Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL("leaflet/dist/images/marker-icon-2x.png", import.meta.url).href,
  iconUrl: new URL("leaflet/dist/images/marker-icon.png", import.meta.url).href,
  shadowUrl: new URL("leaflet/dist/images/marker-shadow.png", import.meta.url).href,
});

// Component to handle clicks
function ClickHandler({ setMarker }) {
  useMapEvent("click", (e) => {
    setMarker([e.latlng.lat, e.latlng.lng]); // Replace previous marker
  });
  return null;
}

export default function MapView() {
  const [marker, setMarker] = useState(null); // Only one marker

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer
        center={[54.526, -105.255]} // Center of North America
        zoom={4}                    // Default zoom
        minZoom={3}                 // Prevent zooming out too far
        maxZoom={8}                 // Prevent zooming in too close
        style={{ height: "100%", width: "100%" }}
        maxBounds={[
          [5, -170],   // Southwest corner
          [85, -50],   // Northeast corner
        ]}
        maxBoundsViscosity={1.0} // Prevent dragging outside bounds
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <ClickHandler setMarker={setMarker} />

        {marker && (
          <Marker position={marker}>
            <Popup>
              Latitude: {marker[0].toFixed(4)}, Longitude: {marker[1].toFixed(4)}
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
