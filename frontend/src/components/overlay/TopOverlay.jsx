import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function TopOverlay() {
  return (
    <div className="flex gap-2 bg-white shadow-lg rounded-xl p-3">
      <Input placeholder="Search location..." className="w-64" />
      <Button>Go</Button>
    </div>
  );
}
