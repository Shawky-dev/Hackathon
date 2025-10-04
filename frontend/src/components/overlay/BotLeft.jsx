import { Calendar22 } from "./Calendar22"
import { Button } from "@/components/ui/button"
import { Brain } from "lucide-react"
import { useCallback, useState } from "react"

export default function BotLeft({ marker, regionName, onRequestForecast }) {
  const [date, setDate] = useState(null)

  const handleDate = useCallback((newDate) => {
    setDate(newDate)
  }, [])

  const handleClick = () => {
    if (onRequestForecast && date) {
      onRequestForecast(date)
    } else {
      console.warn("Please select a date before requesting a forecast.")
    }
  }

  return (
    <div className="w-full max-w-sm flex flex-col gap-y-2 z-10">
      {/* Header row */}
      <div className="flex w-full flex-row items-end justify-between gap-x-2">
        <div className="flex-1">
          <Calendar22 date={date} handleDate={handleDate} />
        </div>
        <Button
          className="flex items-center gap-x-1 w-auto"
          onClick={handleClick}
          disabled={!marker || !date}
        >
          <span>Predict</span>
          <Brain className="w-4 h-4" />
        </Button>
      </div>

      {/* Info box */}
      <div className="w-full bg-white h-auto p-3 rounded-xl flex flex-col gap-y-2 shadow-md overflow-visible">
        <p className="font-bold">Marker Info:</p>
        <div className="flex flex-col gap-x-2">
          {regionName && <p>{regionName},</p>}
          {marker ? (
            <div className="flex flex-row gap-x-2">
              <p>Lat: {marker[0].toFixed(4)}</p>
              <p>Lng: {marker[1].toFixed(4)}</p>
            </div>
          ) : (
            <p>Click on the map to drop a marker.</p>
          )}
        </div>
      </div>
    </div>
  )
}
