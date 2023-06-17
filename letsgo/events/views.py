import os
from .tasks import send_payment_confirmation
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import EventSerializer, CategorySerializer, BookedEventSerializer, RatingSerializer
from drf_spectacular.utils import extend_schema
from .models import Event, BookedEvent, Category, Rating
from .permissions import IsEventOwner
from django.db.models import Q
from .parameters import get_event_list_parameter
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .permissions import IsEventOwner, IsBookedEventOwner
from django.db.models import Avg
from rest_framework import generics
import stripe
from django.db import transaction

stripe.api_key = os.environ.get('STRIPE_API_KEY')

@extend_schema(tags=['Events'])
class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        permission_classes = [AllowAny]
        if self.action == 'create' or self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsEventOwner]

        return [permission() for permission in permission_classes]

    @extend_schema(
        parameters= get_event_list_parameter,
        responses={200: EventSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(event_type="public") | 
                Q(created_by=self.request.user) | 
                Q(created_by__in=self.request.user.friends.all())
            )
        else:
            queryset = queryset.filter(event_type="public")

        queryset = queryset.annotate(rating=Avg('ratings__score')).order_by('-rating')

        search_query = self.request.query_params.get('search')
        privacy_filter = self.request.query_params.get('event_type')
        sort_order = self.request.query_params.get('sort')
        category_list_filter = self.request.query_params.getlist('categories')
        relation_filter = self.request.query_params.get('relation', 'all')

        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(created_by__username__icontains=search_query) 
            )

        # Apply field-based filter
        if privacy_filter:
            if self.request.user.is_authenticated:
                queryset = queryset.filter(event_type=privacy_filter
                                                ).filter(Q(created_by=self.request.user) | 
                                                         Q(created_by__in=self.request.user.friends.all())
)
            else:
                queryset = queryset.filter(event_type="public")
        
        
        if category_list_filter:
            categories = Category.objects.all().filter(pk__in = category_list_filter).values('event')
            queryset = queryset.filter(pk__in=categories)
        
        if relation_filter != 'all':
            user = self.request.user
            if relation_filter != 'user':
                booked_events = BookedEvent.objects.filter(user=user).values('event')
            elif relation_filter != 'friends':
                friends = user.friends.all().filter(private = False)
                booked_events = BookedEvent.objects.filter(user__in=friends).values('event')
            queryset = queryset.filter(pk__in=booked_events) 

        # Apply sorting according to price
        if sort_order:
            if sort_order == 'ascending':
                queryset = queryset.order_by('price')
            elif sort_order == 'descending':
                queryset = queryset.order_by('-price')

        return queryset
    
    
    def update(self, request, *args, **kwargs):
        request_keys = request.data.keys()
        actual_keys = self.serializer_class().get_fields().keys()
        result = [x for x in request_keys if x not in actual_keys]
        if result:
            return Response({'error': 'Invalid data'}, status=400)
        return super().update(request, *args, **kwargs)
    

    def create(self, request):
        request_keys = request.data.keys()
        actual_keys = self.serializer_class().get_fields().keys()
        result = [x for x in request_keys if x not in actual_keys]
        if result:
            return Response({'error': 'Invalid data'}, status=400)
        serializer = EventSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

@extend_schema(tags=['Booked Events'])
class BookedEventViewSet(ModelViewSet):
    queryset = BookedEvent.objects.all()
    serializer_class = BookedEventSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ('post', 'patch', 'get')

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action == 'partial_update' or self.action == 'update' or self.action == 'retrieve':
            permission_classes += [IsBookedEventOwner]
        return [permission() for permission in permission_classes]

    @transaction.atomic
    def create(self, request):
        if 'event' not in request.data:
            return Response("You did not put the event that want to register", status=status.HTTP_400_BAD_REQUEST)
        if not request.data['event'].isdigit():
            return Response("Event type is invalid", status=status.HTTP_400_BAD_REQUEST)
        if len(request.data) > 1:
            return Response("You put more information in the request.data than needed", status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        event_id = request.data['event']
        event = get_object_or_404(Event, pk=event_id)

        if self.queryset.filter((Q(user=user) & Q(event=event))).exists():
            return Response({'error': f'You already booked this event'}, status=404)

        if event.event_type == 'private':
            if user not in event.created_by.friends.all():
                return Response("You can not book this event, it is private event, who is author is not your friend")
        
        # Beginning of transaction
        with transaction.atomic():
            if event.seats <= event.booked_events.count():
                return Response({'error': 'No seats available for this event.'}, status=400)
            if event.price > 0:
                payment_intent = stripe.PaymentIntent.create(
                amount=event.price * 100,
                currency='usd',
                automatic_payment_methods={'enabled': True},
                metadata={
                    'event_id': event.id,
                    'user_id': user.id,
                }
            )
            booking_serializer = BookedEventSerializer(data=request.data, partial=True)
            booking_serializer.is_valid(raise_exception=True)
            booking_serializer.save(user=user)
        # End of transaction 
        send_payment_confirmation.delay(user.id)

        return Response({
            'booked_event': booking_serializer.data,
            'client_secret': payment_intent.client_secret,
        }, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        booked_event = get_object_or_404(BookedEvent)
        if booked_event.status == 'unregistered':
            # Return his money back
            booked_event.delete()
            return Response(f"You have unregistered from the event")
        if booked_event.status == 'participated':
            return Response(f"You can update only the registered event")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if 'status' not in request.data:
            return Response("You do not have status", status=status.HTTP_400_BAD_REQUEST)
        if 'event' in request.data:
            return Response("You can not update event", status.HTTP_400_BAD_REQUEST)
        if 'user' in request.data:
            return Response("You can not update user", status.HTTP_400_BAD_REQUEST)
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

@extend_schema(tags=['Rating'])
class RatingViewSet(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ('post', 'get')

    def create(self, request):
        user = request.user
        event = request.data['event']

        if self.queryset.filter((Q(user=user) & Q(event=event))).exists():
            return Response({'error': f'You already gave a rating to this event'}, status=404)

        booked_events = Event.objects.get(pk=event).booked_events.all()

        for booked_event in booked_events:
            if booked_event.user == user:
                request.data['user'] = user.id
                return super().create(request)  

        return Response("You did not book this event, that is why you can not rate it")
        


@extend_schema(tags=['Category'])
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ['get']
