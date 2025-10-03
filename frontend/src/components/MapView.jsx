import { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvent } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import TopOverlay from './overlay/TopOverlay'
import BotLeft from "./overlay/BotLeft";
import BotRight from "./overlay/BotRight";
// Fix default marker icon paths for Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL("leaflet/dist/images/marker-icon-2x.png", import.meta.url).href,
  iconUrl: new URL("leaflet/dist/images/marker-icon.png", import.meta.url).href,
  shadowUrl: new URL("leaflet/dist/images/marker-shadow.png", import.meta.url).href,
});

function ClickHandler({ setMarker }) {
  useMapEvent("click", (e) => {
    setMarker([e.latlng.lat, e.latlng.lng]);
  });
  return null;
}

export default function MapView() {
  const [marker, setMarker] = useState(null);

  return (
    <div className="relative w-full h-screen">
      {/* Map background */}
      <MapContainer
        center={[54.526, -105.255]}
        zoom={4}
        minZoom={3}
        maxZoom={8}
        className="w-full h-full"
        maxBounds={[
          [5, -170],
          [85, -50],
        ]}
        maxBoundsViscosity={1.0}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
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

       {/* 🔹 Overlay slots */}
      <div className="absolute inset-0 z-[1000] pointer-events-none">
        {/* top overlay */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 pointer-events-auto">
          <TopOverlay />
        </div>

        {/* bottom-left overlay */}
        <div className="absolute bottom-4 left-4 pointer-events-auto">
          <BotLeft marker={marker} />
        </div>

        {/* bottom-right overlay */}
        <div className="absolute bottom-4 right-4 pointer-events-auto">
          <BotRight />
        </div>
      </div>
    </div>
  );
}
