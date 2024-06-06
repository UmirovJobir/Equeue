import logging
import nested_admin
from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *
from .forms import *


# logger = logging.getLogger(__name__)

@admin.register(ServiceName)
class ServiceNameAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'business_type']
    list_display_links = ['id', 'name', 'business_type']
    list_filter = ['business_type']
    search_fields = ['name']


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
    readonly_fields = ['pk']
    raw_id_fields = ['service_name']
    fields = ['pk', 'service_name', 'duration', 'parent']


class BusinessImageInline(nested_admin.NestedTabularInline):
    model = BusinessImage
    extra = 1
    readonly_fields = ['image_tag']

@admin.register(EmployeeRole)
class EmployeeRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'business_type']
    list_display_links = ['id', 'name']
    readonly_fields = ['id']
    fields = ['id', 'business_type', 'name']
    
@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    list_display_links = ['id','name']


@admin.register(Business)
class BusinessAdmin(nested_admin.NestedModelAdmin):
    # list_select_related = ['business_type', 'images']
    list_display = ['id','name', 'business_type', 'logo_tag']
    list_display_links = ['id','name']
    readonly_fields = ['id', 'logo_tag']
    raw_id_fields = ['creator']
    inlines = [
        BusinessImageInline,
        ServiceInline,
        EmployeeInline
    ]
    fieldsets = [
        (None, {
            'fields': ('id', 'creator', 'business_type', 'name', 'description', 'logo', 'logo_tag', 'latitude', 'longitude')
        }),
    ]
    
    
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = ['user', 'business', 'employee', 'service', 'workday', 'start_time', 'end_time']
    fieldsets = [
        (None, {
            'fields': ('user', 'business', 'employee', 'service', 'workday', 'start_time', 'end_time')
        }),
    ]
    