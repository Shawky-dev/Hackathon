import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";

export default function BotLeft({ marker, regionName }) {
  return (
    <Card className="w-64 shadow-lg rounded-xl">
      <CardHeader>
        <CardTitle>Marker Info</CardTitle>
      </CardHeader>
      <CardContent>
        {regionName ? (
          <p>{regionName}</p>   
        ) : (
          <p></p>
        )}

        {marker ? (
          <p>
            Lat: {marker[0].toFixed(4)} <br />
            Lng: {marker[1].toFixed(4)}
          </p>
        ) : (
          <p>Click on the map to drop a marker.</p>
        )}
      </CardContent>
    </Card>
  );
}
