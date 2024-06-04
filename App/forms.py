from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'style': 'width: 100px;'}),
            'last_name': forms.TextInput(attrs={'style': 'width: 100px;'}),
            'patronymic': forms.TextInput(attrs={'style': 'width: 100px;'}),
            'phone': forms.TextInput(attrs={'style': 'width: 100px;'}),
            'duration': forms.TextInput(attrs={'style': 'width: 100px;'}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        service = cleaned_data.get('service')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        workday = cleaned_data.get('workday')

        if not all([employee, service, start_time, end_time, workday]):
            return cleaned_data

        # Calculate the order duration
        order_duration = end_time - start_time

        # Get the employee duration if it exists, otherwise use the service duration
        employee_duration = employee.duration
        service_duration = service.duration
        expected_duration = employee_duration if employee_duration else service_duration

        # Validate the order duration matches the employee or service duration
        if order_duration != expected_duration:
            raise ValidationError({
                'end_time': _('The duration between start_time and end_time must match the employee or service duration.')
            })

        # Validate the order workday and times fit within the employee's work schedule
        if not self.employee_works_on_day_and_time(employee, workday, start_time, end_time):
            raise ValidationError({
                'start_time': _('The order times must fall within the employee\'s work schedule for the selected day.'),
                'end_time': _('The order times must fall within the employee\'s work schedule for the selected day.')
            })

        # Check if the employee is available during the specified times
        if not self.is_employee_available(employee, workday, start_time, end_time):
            raise ValidationError({
                'start_time': _('The employee is not available during the specified times.'),
                'end_time': _('The employee is not available during the specified times.')
            })

        return cleaned_data

    def employee_works_on_day_and_time(self, employee, workday, start_time, end_time):
        # Check if the employee works on the given day and time
        work_schedules = employee.work_schedules.filter(workday=workday)
        for schedule in work_schedules:
            if schedule.start_time <= start_time.time() <= schedule.end_time and schedule.start_time <= end_time.time() <= schedule.end_time:
                return True
        return False

    def is_employee_available(self, employee, workday, start_time, end_time):
        # Check if the employee has no overlapping orders during the specified times
        overlapping_orders = Order.objects.filter(
            employee=employee,
            workday=workday,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(id=self.instance.id)
        return not overlapping_orders.exists()