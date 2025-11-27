# Court Creation & Booking Guide

## Problem Solved
When courts were created, they weren't appearing on the booking page because they lacked **Availability Schedules** and **Time Slots**.

## How It Works Now

### Automatic Setup (Recommended)
When you create a new court:
1. **Via Web Form** (`/manage/court/create/`):
   - Fill in the court details
   - Submit the form
   - ✅ Availability and slots are **automatically created**

2. **Via Django Admin** (Inline in Facility):
   - Go to `/admin/booking_sys/facility/`
   - Click on a facility
   - Scroll to "Courts" section
   - Add a new court
   - Save
   - ✅ Availability and slots are **automatically created**

### Editing Courts in Admin

#### Quick Edit (Inline in Facility):
1. Go to `/admin/booking_sys/facility/`
2. Click on a facility to edit
3. Scroll to "Courts" section
4. You can now:
   - ✏️ Edit court name, sport type, capacity, status, image, notes directly
   - 📝 Click "Edit Full Details" button to open the full court editor
   - ➕ Add new courts with the "+ Add another Court" button
   - ✅ Changes save with the facility

#### Full Court Editor (Advanced):
From the inline, click "📝 Edit Full Details" button to access:
- **Basic Court Info**: Name, facility, sport, capacity
- **Media**: Image URL
- **Status**: Availability status
- **Availability**: Operating hours for each day of week
- **Time Slots**: Bookable time windows with types (regular/peak/off-peak)
- **Blackout Periods**: Maintenance windows

### Default Schedule Generated
Every new court automatically gets:
- **Operating Hours**: 6 AM to 10 PM (all days)
- **Time Slots**: 5 slots per day at 2-hour intervals:
  - 08:00 - 10:00
  - 10:30 - 12:30
  - 13:00 - 15:00
  - 15:30 - 17:30
  - 18:00 - 20:00

### Manual Adjustments
After a court is created, you can customize:

1. **Availability** (Operating Hours):
   - Via inline "Edit Full Details" button, OR
   - Go to `/admin/booking_sys/availability/`
   - Edit the availability records for specific days
   - Change open/close times as needed

2. **Slots** (Bookable Time Windows):
   - Via inline "Edit Full Details" button, OR
   - Go to `/admin/booking_sys/slot/`
   - Edit specific slots or create custom ones
   - Organize slots by day of week and time
   - Set slot types (regular/peak/off-peak)

## Setup Commands

### 1. Command Line Setup (if needed)
```bash
python manage.py setup_court_schedule
```
This sets up availability and slots for any court missing them.

### 2. Admin Action
1. Go to `/admin/booking_sys/court/`
2. Select courts that need scheduling
3. Choose "Set up availability and slots for selected courts" from Actions dropdown
4. Click "Go"

## Courts Now Display When:
✅ Court has status = "available"
✅ Court has Availability record for the selected day
✅ Court has at least one Slot for the selected day
✅ Slot status = "available"

## Troubleshooting

**Court not showing in booking page?**
1. Check if court has status "available"
2. Check if Availability records exist for that day
3. Check if Slots exist for that day
4. Run the setup command or use admin action to auto-populate

**Can't customize schedule?**
- Edit individual Availability records in `/admin/booking_sys/availability/`
- Edit individual Slots in `/admin/booking_sys/slot/`
- Add new slots through admin inlines
