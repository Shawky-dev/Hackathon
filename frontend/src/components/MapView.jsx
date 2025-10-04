import { useState, useEffect, useCallback, useRef } from "react";
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

import ForecastDisplay from "./overlay/ForcastDisplay";
import TopOverlay from "./overlay/TopOverlay";
import BotLeft from "./overlay/BotLeft";
import BotRight from "./overlay/BotRight";
import api from "@/api/axios";

// 🧭 Fix default marker icon paths for Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL(
    "leaflet/dist/images/marker-icon-2x.png",
    import.meta.url
  ).href,
  iconUrl: new URL("leaflet/dist/images/marker-icon.png", import.meta.url)
    .href,
  shadowUrl: new URL("leaflet/dist/images/marker-shadow.png", import.meta.url)
    .href,
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
  const [forecastData, setForecastData] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false); // 🆕 Separate loading state for forecast
  const [pollingStatus, setPollingStatus] = useState(""); // 🆕 Show polling status
  const [showForecast, setShowForecast] = useState(false);


  const pollingIntervalRef = useRef(null); // 🆕 Store polling interval

  // 🆕 Stop polling function
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
      console.log("Polling stopped");
    }
  }, []);

  // 🆕 Check forecast status (polling function)
  const checkForecastStatus = useCallback(async (requestId) => {
    try {
      const response = await api.post("forecast/check-forecast-request", {
        requestId,
      });

      if (response.status === 200) {
        // ✅ Forecast is ready
        stopPolling();
        setForecastLoading(true); // Data is loaded
        setPollingStatus("Forecast data received!");

        // Display data in console
        console.log("=== FORECAST DATA RECEIVED ===");
        console.log("Current Conditions:", response.data.current_conditions);
        console.log("Forecast:", response.data.forecast);
        console.log("Full Response:", response.data);
        console.log("==============================");

        setForecastData(response.data);
        setShowForecast(true);

      } else if (response.status === 202) {
        // ⏳ Still processing
        console.log("Polling... Forecast still being processed");
        setPollingStatus("Processing forecast...");
      }
    } catch (err) {
      console.error("Error polling forecast status:", err);
      stopPolling();
      setError("Failed to check forecast status");
      setForecastLoading(false);
    }
  }, [stopPolling]);

  // 🆕 Start polling
  const startPolling = useCallback((requestId) => {
    console.log(requestId)
    console.log("Starting to poll for forecast status...");
    setPollingStatus("Checking forecast status...");

    // Poll immediately
    checkForecastStatus(requestId);

    // Then poll every 5 seconds
    pollingIntervalRef.current = setInterval(() => {
      checkForecastStatus(requestId);
    }, 5000);
  }, [checkForecastStatus]);

  // 🌤️ Forecast API logic with polling
  const handleRequestForecast = useCallback(
    async (date) => {
      if (!marker) {
        setError("Please select a location first.");
        return;
      }

      try {
        setForecastLoading(false); // Reset loading state
        setForecastData(null); // Clear previous data
        setError(null);
        setPollingStatus("Requesting forecast...");

        const [lat, long] = marker;

        // 1️⃣ Request forecast
        const res = await api.post("forecast/request-forecast", {
          long,
          lat,
          date,
        });

        console.log("Forecast Request Response:", res.data);

        // 2️⃣ Set loading to false after request is sent
        setForecastLoading(false);

        // 3️⃣ Start polling with the requestId
        if (res.data.requestId) {
          startPolling(res.data.requestId);
        } else {
          setError("No request ID received");
        }

      } catch (err) {
        console.error("Forecast error:", err);
        setError("Failed to request forecast data.");
        setForecastLoading(false);
      }
    },
    [marker, startPolling]
  );

  // 🧹 Cleanup polling on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  // 📍 Fetch region boundary
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
      await new Promise((resolve) => setTimeout(resolve, 1000));

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
        setRegionId((prev) => prev + 1);
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

  // Zoom to region boundary when it loads
  useEffect(() => {
    if (!regionGeoJson || !map) return;

    try {
      const geoJsonLayer = L.geoJSON(regionGeoJson);
      const bounds = geoJsonLayer.getBounds();

      if (bounds.isValid()) {
        map.fitBounds(bounds, {
          padding: [50, 50],
          maxZoom: 8,
          animate: true,
          duration: 1,
        });
      }
    } catch (err) {
      console.error("Error zooming to region:", err);
    }
  }, [regionGeoJson, map]);

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
                <strong>Location</strong>
                <br />
                Lat: {marker[0].toFixed(4)}
                <br />
                Lon: {marker[1].toFixed(4)}
                {regionName && (
                  <>
                    <br />
                    <strong>Region:</strong> {regionName}
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

      {/* 🌀 Loading Overlay (for region boundary) */}
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



      {/* 🆕 Forecast Polling Status */}
      {pollingStatus && !forecastLoading && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-[2000] pointer-events-auto">
          <div className="bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span className="text-sm font-medium">{pollingStatus}</span>
          </div>
        </div>
      )}
{/* 
      {forecastLoading && forecastData && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-[2000] pointer-events-auto">
          <div className="bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
            <span className="text-xl">✓</span>
            <span className="text-sm font-medium">Forecast data loaded! Check console.</span>
            <button
              onClick={() => {
                setForecastLoading(false);
                setPollingStatus("");
              }}
              className="ml-2 text-white hover:text-green-100 text-xl leading-none"
            >
              ×
            </button>
          </div>
        </div>
      )} */}

      {/* 🔹 Overlay slots */}
      <div className="absolute inset-0 z-[1000] pointer-events-none">
        <div className="absolute top-4 left-1/2 -translate-x-1/2 pointer-events-auto">
          <TopOverlay
            forecastData={showForecast ? forecastData : null}
            onClose={() => setShowForecast(false)}
          />
        </div>


        <div className="absolute bottom-4 left-4 pointer-events-auto">
          <BotLeft
            marker={marker}
            regionName={regionName}
            onRequestForecast={handleRequestForecast}
          />
        </div>

        <div className="absolute top-4 right-4 pointer-events-auto">
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