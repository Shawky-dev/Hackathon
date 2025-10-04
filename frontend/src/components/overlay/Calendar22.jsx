import { ChevronDownIcon } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Label } from "@/components/ui/label"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
// If using Radix directly:
// import { Portal } from "@radix-ui/react-portal"

export function Calendar22() {
  const [open, setOpen] = useState(false)
  const [date, setDate] = useState(undefined)

  return (
    <div className="flex flex-col gap-3 relative z-20">
      <Label htmlFor="date" className="px-1">
        Select prediction date
      </Label>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            id="date"
            className="w-48 justify-between font-normal"
          >
            {date ? date.toLocaleDateString() : "Select date"}
            <ChevronDownIcon />
          </Button>
        </PopoverTrigger>

        {/* PopoverContent fix: make it render above everything */}
        <PopoverContent
          className="w-auto overflow-hidden p-0 z-[9999]"
          align="start"
          sideOffset={4}
        >
          <Calendar
            mode="single"
            selected={date}
            captionLayout="dropdown"
            onSelect={(date) => {
              setDate(date)
              setOpen(false)
            }}
          />
        </PopoverContent>
      </Popover>
    </div>
  )
}
