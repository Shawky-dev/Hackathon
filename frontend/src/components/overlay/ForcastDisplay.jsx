export default function ForecastDisplay({ forecastData, onClose }) {
  if (!forecastData) return null;

  const getAQIStatus = (aqi) => {
    if (aqi <= 50) return { label: 'Good', color: 'text-green-600' };
    if (aqi <= 100) return { label: 'Moderate', color: 'text-yellow-600' };
    if (aqi <= 150) return { label: 'Unhealthy for Sensitive', color: 'text-orange-600' };
    return { label: 'Unhealthy', color: 'text-red-600' };
  };

  const currentAQI = forecastData.current_conditions?.aqi;
  const currentStatus = getAQIStatus(currentAQI);

  return (
    <div className="max-w-md">
      <div className="bg-white rounded-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">🌤️</span>
            <span className="font-semibold">Air Quality Forecast</span>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-blue-100 text-2xl leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Current Conditions */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="text-sm text-gray-600 mb-1">Current Conditions</div>
          <div className="flex items-center gap-3">
            <div className="text-3xl font-bold text-gray-900">
              {currentAQI || 'N/A'}
            </div>
            <div className="text-sm">
              <div className="font-medium text-gray-700">AQI</div>
              <div className={`text-xs font-semibold ${currentStatus.color}`}>
                {currentStatus.label}
              </div>
            </div>
          </div>
        </div>

        {/* Forecast */}
        <div className="p-4">
          <div className="text-sm text-gray-600 mb-3">Forecast</div>
          <div className="space-y-2">
            {forecastData.forecast?.map((item, idx) => {
              const date = new Date(item.datetime);
              const dateStr = date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                year: 'numeric'
              });
              const status = getAQIStatus(item.aqi);
              
              return (
                <div 
                  key={idx} 
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-sm">{dateStr}</div>
                    <div className={`text-xs font-semibold mt-0.5 ${status.color}`}>
                      {status.label}
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {item.aqi}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}