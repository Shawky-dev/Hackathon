import { useState, useEffect, useCallback } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  GeoJSON,
  useMapEvent,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import TopOverlay from "./overlay/TopOverlay";
import BotLeft from "./overlay/BotLeft";
import BotRight from "./overlay/BotRight";

// 🧭 Fix default marker icon paths for Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL("leaflet/dist/images/marker-icon-2x.png", import.meta.url).href,
  iconUrl: new URL("leaflet/dist/images/marker-icon.png", import.meta.url).href,
  shadowUrl: new URL("leaflet/dist/images/marker-shadow.png", import.meta.url).href,
});

// 🖱️ Handles clicks on the map
function ClickHandler({ setMarker }) {
  useMapEvent("click", (e) => {
    setMarker([e.latlng.lat, e.latlng.lng]);
  });
  return null;
}

// Expose map object
function MapHelper({ onMapReady }) {
  const map = useMap();
  useEffect(() => {
    if (onMapReady) onMapReady(map);
  }, [map, onMapReady]);
  return null;
}

export default function MapView() {
  const [loading, setLoading] = useState(false);
  const [marker, setMarker] = useState(null);
  const [regionGeoJson, setRegionGeoJson] = useState(null);
  const [map, setMap] = useState(null);
  const [regionName, setRegionName] = useState("");
  const [error, setError] = useState(null);
  const [regionId, setRegionId] = useState(0);

  // 📍 Fetch region boundary with improved error handling and rate limiting
  const fetchRegion = useCallback(async (markerPos) => {
    const [lat, lon] = markerPos;
    
    try {
      setLoading(true);
      setError(null);

      // 1️⃣ Reverse geocode to get region name
      const reverseUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
      const reverseResponse = await fetch(reverseUrl, {
        headers: { "User-Agent": "ReactApp" },
      });

      if (!reverseResponse.ok) {
        throw new Error(`HTTP ${reverseResponse.status}`);
      }

      const data = await reverseResponse.json();

      // Enhanced region detection with more fallbacks
      const detectedRegion =
        data.address.state ||
        data.address.region ||
        data.address.province ||
        data.address.county ||
        data.address.city_district ||
        data.address.city ||
        data.address.town ||
        data.address.village ||
        null;

      setRegionName(detectedRegion || "Unknown");

      if (!detectedRegion) {
        setError("No region boundary found for this location");
        setRegionGeoJson(null);
        return;
      }

      console.log("Detected region:", detectedRegion);

      // 2️⃣ Rate limiting: Wait 1 second between requests
      await new Promise(resolve => setTimeout(resolve, 1000));

      // 3️⃣ Search for region's GeoJSON boundary
      const searchUrl = `https://nominatim.openstreetmap.org/search?format=geojson&polygon_geojson=1&q=${encodeURIComponent(
        detectedRegion
      )}`;
      const searchResponse = await fetch(searchUrl, {
        headers: { "User-Agent": "ReactApp" },
      });

      if (!searchResponse.ok) {
        throw new Error(`HTTP ${searchResponse.status}`);
      }

      const geoData = await searchResponse.json();

      if (geoData.features?.length > 0) {
        setRegionGeoJson(geoData.features[0].geometry);
        setRegionId(prev => prev + 1);
        setError(null);
      } else {
        setError(`No boundary data available for ${detectedRegion}`);
        setRegionGeoJson(null);
      }
    } catch (err) {
      console.error("Error fetching region:", err);
      
      if (err.message.includes("429")) {
        setError("Too many requests. Please wait a moment and try again.");
      } else if (err.message.includes("Failed to fetch")) {
        setError("Network error. Please check your connection.");
      } else {
        setError("Could not load region boundary. Please try again.");
      }
      
      setRegionGeoJson(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Trigger region fetch when marker changes
  useEffect(() => {
    if (!marker) return;
    fetchRegion(marker);
  }, [marker, fetchRegion]);

  return (
    <div className="relative w-full h-screen">
      {/* 🗺️ Map */}
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
        <MapHelper onMapReady={setMap} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* 🖱️ Capture map clicks */}
        <ClickHandler setMarker={setMarker} />

        {/* 📍 Marker */}
        {marker && (
          <Marker position={marker}>
            <Popup>
              <div className="text-sm">
                <strong>Location</strong><br />
                Lat: {marker[0].toFixed(4)}<br />
                Lon: {marker[1].toFixed(4)}
                {regionName && (
                  <>
                    <br /><strong>Region:</strong> {regionName}
                  </>
                )}
              </div>
            </Popup>
          </Marker>
        )}

        {/* 🟥 Outline region boundary */}
        {regionGeoJson && (
          <GeoJSON
            key={regionId}
            data={regionGeoJson}
            style={{
              color: "red",
              weight: 3,
              fillOpacity: 0.1,
            }}
          />
        )}
      </MapContainer>

      {/* 🌀 Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-black/40 text-white flex items-center justify-center z-[2000]">
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 border-4 border-white/30 border-t-white rounded-full animate-spin"></div>
            <div className="text-lg font-semibold">
              Detecting region boundary...
            </div>
          </div>
        </div>
      )}

      {/* ⚠️ Error Message */}
      {error && !loading && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-[2000] max-w-md pointer-events-auto">
          <div className="bg-red-500 text-white px-4 py-3 rounded-lg shadow-lg flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <div className="flex-1">
              <p className="font-semibold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-white hover:text-red-100 text-xl leading-none"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* 🔹 Overlay slots */}
      <div className="absolute inset-0 z-[1000] pointer-events-none">
        <div className="absolute top-4 left-1/2 -translate-x-1/2 pointer-events-auto">
          <TopOverlay />
        </div>

        <div className="absolute bottom-4 left-4 pointer-events-auto">
          <BotLeft marker={marker} regionName={regionName} />
        </div>

        <div className="absolute bottom-4 right-4 pointer-events-auto">
          <BotRight 
            setMarker={setMarker} 
            setRegionGeoJson={setRegionGeoJson}
            setRegionName={setRegionName} 
            map={map} 
          />
        </div>
      </div>
    </div>
  );
}