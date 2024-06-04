import logging
import nested_admin
from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *
from .forms import *


# logger = logging.getLogger(__name__)


class EmployeeWorkScheduleInline(nested_admin.NestedTabularInline):
    model = EmployeeWorkSchedule
    extra = 0
    classes = ['collapse']

class EmployeeInline(nested_admin.NestedTabularInline):
    model = Employee
    form = EmployeeForm
    extra = 0
    inlines = [EmployeeWorkScheduleInline]
    readonly_fields = ['image_tag']
    fieldsets = [
        (None, {
            'fields': ('role', 'last_name', 'first_name', 'patronymic', 'phone', 'duration', 'service', 'image', 'image_tag')
        })
    ]
    
class ServiceInline(nested_admin.NestedTabularInline):
    model = Service
    extra = 0
    

class BusinessImageInline(nested_admin.NestedTabularInline):
    model = BusinessImage
    extra = 1
    readonly_fields = ['image_tag']

@admin.register(EmployeeRole)
class EmployeeRoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    
@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    list_display_links = ['id','name']


@admin.register(Business)
class BusinessAdmin(nested_admin.NestedModelAdmin):
    # list_select_related = ['business_type', 'images']
    list_display = ['id','name', 'business_type', 'latitude', 'longitude']
    list_display_links = ['id','name']
    readonly_fields = ['logo_tag']
    inlines = [
        BusinessImageInline,
        ServiceInline,
        EmployeeInline
    ]
    fieldsets = [
        (None, {
            'fields': ('creater', 'business_type', 'name', 'description', 'logo', 'logo_tag', 'latitude', 'longitude')
        }),
    ]
    
    def logo_tag(self, obj):
        if obj.logo:
            return format_html('<img src="%s" style="max-width: 200px; max-height: 200px;" />' % obj.logo.url)
        return None
    logo_tag.short_description = 'Logo Tag'
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = ['user', 'business', 'employee', 'service', 'workday', 'start_time', 'end_time']
    fieldsets = [
        (None, {
            'fields': ('user', 'business', 'employee', 'service', 'workday', 'start_time', 'end_time')
        }),
    ]
    