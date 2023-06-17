from rest_framework import serializers
from .models import BookedEvent, Event, Category, Rating

class EventSerializer(serializers.ModelSerializer):
    rating = serializers.DecimalField(default=0, max_digits=3, decimal_places=2)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'price', 'start_time', 'created_by', 'guests', 'event_type', 'rating', 'seats')

class BookedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedEvent
        fields = ('id', 'event', 'user', 'status')
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('id', 'user', 'event', 'score')