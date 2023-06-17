from django.db import models
from users.models import User
from .choices import EventStatus, EventType
from django.core.exceptions import ValidationError


class Event(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    price = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, related_name='created_events', default=None, on_delete=models.CASCADE, blank=True, null=True)
    guests = models.ManyToManyField(User, default=None, blank=True)
    categories = models.ManyToManyField('Category', default=None)
    event_type = models.CharField(choices= EventType.choices, default='public', max_length=10)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField(auto_now=True)
    seats = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class BookedEvent(models.Model):
    user = models.ForeignKey(User, related_name = "booked_events", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name = "booked_events", on_delete=models.CASCADE)
    status = models.CharField(max_length = 20, choices=EventStatus.choices, default='registered')
    

    def __str__(self):
        return f'{self.user.username} <-> {self.status} <-> {self.event.title}'


def validate_rating(value):
    if value <= 0 or value > 5:
        raise ValidationError("score has to be between 1 and 5")    

class Rating(models.Model):
    user = models.ForeignKey(User, related_name = "ratings", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name = "ratings", on_delete=models.CASCADE)
    score = models.IntegerField(validators=[validate_rating])
    
    def __str__(self):
        return f'{self.user.username} rate for {self.event}'
