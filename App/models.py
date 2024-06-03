from django.db import models
from django.utils.html import format_html
from django.core.validators import RegexValidator

class BusinessType(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Business(models.Model):
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, related_name='businesses') 
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='businesses/logos')
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self):
        return self.name
    

class BusinessImage(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='businesses/images')
    
    def image_tag(self):
        return format_html('<img src="%s" width="100px" />' % (self.image.url))
    image_tag.short_description = 'Image'


class Service(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    duration = models.DurationField()
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subservices'
    )

    def __str__(self):
        return self.name
    

class EmployeeRole(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Employee(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='employees')
    role = models.ForeignKey(EmployeeRole, on_delete=models.CASCADE, related_name='role')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)
    duration = models.DurationField()
    service = models.ManyToManyField(Service, related_name='employees')
    image = models.ImageField(upload_to='employees/images', null=True, blank=True)
    phone = models.CharField(
        unique=True,
        max_length=17,
        validators=[
            RegexValidator(
                regex=r'^998[0-9]{2}[0-9]{7}$',
                # message="Only Uzbekistan numbers are confirmed"
            )
        ]
    )

    def __str__(self):
        return self.last_name + self.first_name
    
    def image_tag(self):
        return format_html('<img src="%s" width="100px" />' % (self.image.url))
    image_tag.short_description = 'Image'


class EmployeeWorkSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_schedules')
    workday = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    
    def __str__(self):
        return f"{self.employee}'s schedule for {self.get_workday_display()} ({self.start_time} - {self.end_time})"

# #  App.BusinessType App.Business App.BusinessImage App.Service App.EmployeeRole App.Employee App.EmployeeWorkSchedule