import { ChevronDownIcon } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

export function Calendar22({ handleDate }) {
  const [open, setOpen] = useState(false)
  const [dateTime, setDateTime] = useState(undefined)

  const handleSelectDate = (selectedDate) => {
    if (!selectedDate) return
    let updatedDate = selectedDate

    // If a time was already set, preserve it
    if (dateTime) {
      updatedDate.setHours(dateTime.getHours(), dateTime.getMinutes(), 0, 0)
    }

    setDateTime(updatedDate)
    handleDate(updatedDate)
    setOpen(false)
  }

  const handleTimeChange = (e) => {
    const value = e.target.value
    if (!dateTime) return

    const [hours, minutes] = value.split(":").map(Number)
    const updated = new Date(dateTime)
    updated.setHours(hours, minutes, 0, 0)

    setDateTime(updated)
    handleDate(updated)
  }

  const formattedLabel = dateTime
    ? `${dateTime.toLocaleDateString()} ${dateTime.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })}`
    : "Select date & time"

  return (
    <div className="flex flex-col gap-3 relative z-20">
      <Label htmlFor="date" className="px-1">
        Select prediction date & time
      </Label>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            id="date"
            className="w-60 justify-between font-normal"
          >
            {formattedLabel}
            <ChevronDownIcon />
          </Button>
        </PopoverTrigger>

        <PopoverContent
          className="w-auto overflow-hidden p-3 space-y-3 z-[9999]"
          align="start"
          sideOffset={4}
        >
          <Calendar
            mode="single"
            selected={dateTime}
            captionLayout="dropdown"
            onSelect={handleSelectDate}
          />

          <div className="flex flex-col gap-2">
            <Label htmlFor="time" className="text-sm font-medium">
              Time
            </Label>
            <Input
              type="time"
              id="time"
              step="60"
              value={
                dateTime
                  ? `${String(dateTime.getHours()).padStart(2, "0")}:${String(
                      dateTime.getMinutes()
                    ).padStart(2, "0")}`
                  : "12:00"
              }
              onChange={handleTimeChange}
              className="w-32"
            />
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
}
