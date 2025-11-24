#run migrations first

from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'member_type', 'is_active']

#Register other models similarly...
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(Facility)
admin.site.register(Court)
admin.site.register(Availability)
admin.site.register(Slot)
admin.site.register(Booking)
admin.site.register(Blackout)
admin.site.register(Notification)
admin.site.register(AuditLog)
