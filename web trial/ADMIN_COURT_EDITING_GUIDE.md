# Admin Court Editing Guide

## Overview
The admin interface now provides multiple ways to edit courts, from quick inline edits to full-featured court management.

## Court Management Workflow

### 1. Facility Admin Page
**Path**: `/admin/booking_sys/facility/`

#### View All Courts
- See all facilities listed
- Each facility shows count of courts

#### Edit a Facility
- Click on facility name
- Scroll to "Courts" section
- See all courts in StackedInline format (more readable than table)

### 2. Quick Court Editing (Inline)
Within the Facility editor, the Courts section shows:

```
┌─ COURT ─────────────────────────────────┐
│ Court Name: [input]  Sport: [input]      │
│ 📝 Edit Full Details [button]           │
├─────────────────────────────────────────┤
│ Capacity: [input]   Status: [dropdown]   │
│ Image URL: [input]                       │
│ Notes: [textarea]                        │
│ ✓ Delete                                │
└─────────────────────────────────────────┘
```

**Available Actions**:
- ✏️ Edit all basic court info directly
- 📝 Click "Edit Full Details" for full court editor
- ➕ Add another court with "+ Add another Court"
- ✓ Delete courts with checkbox
- Save all changes with facility

### 3. Full Court Editor
**Path**: `/admin/booking_sys/court/[id]/`

Opens in new tab when you click "Edit Full Details" from inline.

#### Features:
- **Basic Information**
  - Court ID (read-only)
  - Facility (dropdown)
  - Court Name
  - Sport Type
  - Capacity

- **Media**
  - Image URL

- **Status**
  - Court Status (Available/Maintenance/Closed)

- **Additional Information**
  - Notes (large text area)

- **Inlines** (nested editing):
  - **Availability Schedules** - Operating hours for each day
  - **Time Slots** - Bookable time windows
  - **Blackout Periods** - Maintenance/closed periods

- **Actions**:
  - Mark as available/maintenance/closed
  - Set up availability and slots (if missing)

### 4. Court List View
**Path**: `/admin/booking_sys/court/`

Quick overview of all courts with:
- Court Name
- Facility Link
- Sport Type
- Capacity
- Status
- Active Bookings Count

**Actions available**:
- Mark courts as available/maintenance/closed
- Set up availability and slots for multiple courts

## Workflow Examples

### Example 1: Edit Court Operating Hours
1. Go to `/admin/booking_sys/facility/`
2. Click on facility
3. Find court in Courts section
4. Click "📝 Edit Full Details"
5. In Availability section, click existing day or add new
6. Edit open_time and close_time
7. Save

### Example 2: Add New Time Slots
1. Go to `/admin/booking_sys/facility/`
2. Click on facility
3. Find court in Courts section
4. Click "📝 Edit Full Details"
5. Scroll to Time Slots section
6. Click "+ Add another Time Slot"
7. Select day, start time, end time, slot type
8. Save

### Example 3: Mark Court for Maintenance
1. Go to `/admin/booking_sys/facility/`
2. Click on facility
3. In Courts section, change Status to "Under Maintenance"
4. Save

### Example 4: Quick Bulk Actions
1. Go to `/admin/booking_sys/court/`
2. Select multiple courts
3. Choose action from dropdown (Mark available/setup schedule)
4. Click "Go"

## Tips & Tricks

### ✅ Best Practices
- Set up availability first, then slots
- Use consistent time slot durations (e.g., all 2-hour slots)
- Mark peak hours with "Peak" slot type
- Set off-peak rates with "Off-Peak" slot type
- Add blackout periods for maintenance

### ⚡ Speed Tips
- Use inline editor for quick changes (no page navigation)
- Use full editor only when adjusting availability/slots
- Use list actions for bulk changes across multiple courts
- Set up default schedule automatically (signal does this)

### 🔍 Troubleshooting
- **Court not showing in booking**: Check status="available" AND has availability AND has slots
- **Can't see "Edit Full Details" button**: Save the court inline first
- **Changes not showing**: Clear browser cache or refresh
- **Want to reset schedule**: Use "Set up availability and slots" action

## Admin Hierarchy

```
Django Admin (/admin/)
├── Facility
│   └── [Edit Facility]
│       └── Courts (Inline)
│           ├── [Quick Edit Fields]
│           ├── [Edit Full Details] → Full Court Editor
│           │   ├── Availability (Inline)
│           │   ├── Time Slots (Inline)
│           │   └── Blackout Periods (Inline)
│           └── [+ Add another Court]
├── Court
│   └── [List View with Actions]
│       └── [Select & Bulk Actions]
├── Availability
│   └── [List all availability schedules]
└── Slot
    └── [List all time slots]
```

## Related Admin Pages

Quick Navigation:
- Facilities: `/admin/booking_sys/facility/`
- Courts: `/admin/booking_sys/court/`
- Availability: `/admin/booking_sys/availability/`
- Slots: `/admin/booking_sys/slot/`
- Blackout Periods: `/admin/booking_sys/blackout/`
