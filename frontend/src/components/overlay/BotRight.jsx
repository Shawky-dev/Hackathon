import { Button } from "@/components/ui/button"; // or your button source
import {RotateCcw} from "lucide-react"
export default function BotRight({ setMarker, setRegionGeoJson, map,setRegionName }) {
  const handleReset = () => {
    if (!map) return;
    map.setView([54.526, -105.255], 4);
    setMarker(null);
    setRegionGeoJson(null);
    setRegionName(null);
  };

  return (
    <Button
      onClick={handleReset}
      className="shadow rounded-xl px-3 py-2"
    >
      <RotateCcw/>
      Reset View
    </Button>
  );
}
