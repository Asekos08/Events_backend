from django.core.management.base import BaseCommand
import random
from faker import Faker
from django.contrib.auth import get_user_model
# from django.db import connection as django_connection
from users.models import FriendRequest
from events.models import Event, BookedEvent, Category
from users.choices import FriendRequestStatus
from events.choices import *
import requests
import concurrent.futures
import json


# import requests
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry


# session = requests.Session()
# retry = Retry(connect=3, backoff_factor=0.5)
# adapter = HTTPAdapter(max_retries=retry)
# session.mount('http://', adapter)
# session.mount('https://', adapter)

class Command(BaseCommand):
    help = 'Populate the database with dummy data'

    def handle(self, *args, **options):
        # Your script code goes here
        fake = Faker()
        User = get_user_model()

        # Create dummy users
        users = []
        for _ in range(3):
            username = fake.user_name()
            email = fake.email()
            password = "password"
            user = User.objects.create_user(username=username, email=email, password=password)
            users.append(user)

        # Create categories
        categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4']
        for category_name in categories:
            category = Category.objects.create(name=category_name)

        # Create events
        events = []
        for _ in range(20):
            title = fake.word()
            description = fake.sentence()
            price = random.randint(0, 100)
            created_by = random.choice(users)
            event_type = random.choice(EventType.values)
            event = Event.objects.create(
                title=title,
                description=description,
                price=price,
                created_by=created_by,
                event_type=event_type,
                seats=10
            )
            event.categories.set(random.sample(list(Category.objects.all()), random.randint(1, 3)))
            events.append(event)
        
        # title = fake.word()
        # description = fake.sentence()
        # price = 1000 
        # created_by = random.choice(users)
        # event_type = 'public'
        # event = Event.objects.create(
        #     title=title,
        #     description=description,
        #     price=price,
        #     created_by=created_by,
        #     event_type=event_type,
        #     seats=1
        # )
        # auth_users = []
        # auth_url = 'http://127.0.0.1:8000/login/'
        # url = 'http://127.0.0.1:8000/api/v1/booked_events/'

        # # session.get(auth_url)

        # for user in users:
        #     data = {
        #         'username': user.username,
        #         'password': 'password',
        #     }
        #     print(data)
        #     response = requests.post(auth_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        #     # print(response.json()['access'])
        #     auth_users.append(response.json()['access'])
        # def book_event(user_id):
        #     data = {
        #         'event': 1
        #     }
        #     # print(auth_users[user_id])
        #     # return auth_users[user_id]
        #     # f"Bearer {auth_users[user_id]}"
        #     response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {auth_users[user_id]}'})
        #     return response.json()
        
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     futures = [executor.submit(book_event, user_id) for user_id in range(len(users))]

        #     # Wait for all the requests to complete
        #     concurrent.futures.wait(futures)

        #     # Retrieve the results
        #     results = [future.result() for future in futures]

        
        # for user_id, result in zip(users, results):
        #     print(f"User {user_id} - {result}")

        # # Create booked events
        # for user in users:
        #     for _ in range(random.randint(0, 5)):
        #         event = random.choice(events)
        #         status = random.choice(EventStatus.values)
        #         booked_event = BookedEvent.objects.create(user=user, event=event, status=status)

        # Create friend requests
        for user in users:
            friends = random.sample(users, random.randint(1, 5))
            for friend in friends:
                if user != friend:
                    friend_request = FriendRequest.objects.create(sender=user, receiver=friend, status=FriendRequestStatus.PENDING)

        # print("Database population completed.")



        # Retrieve all users
        users = User.objects.all()
        print([user.username for user in users])
        # print("Users:")
        # for user in users:
        #     print(user.username)

        # Retrieve all events
        events = Event.objects.all()
        print(len(events))
        # print("Events:")
        # for event in events:
        #     print(event.title)

        # Retrieve all categories
        categories = Category.objects.all()
        print(len(categories))
        # print("Categories:")
        # for category in categories:
        #     print(category.name)

        # Retrieve all booked events
        booked_events = BookedEvent.objects.all()
        print(len(booked_events))
        # print("Booked Events:")
        # for booked_event in booked_events:
        #     print(f"User: {booked_event.user.username}, Event: {booked_event.event.title}, Status: {booked_event.status}")

        # Retrieve all friend requests
        friend_requests = FriendRequest.objects.all()
        print(len(friend_requests))
        # print("Friend Requests:")
        # for friend_request in friend_requests:
        #     print(f"Sender: {friend_request.sender.username}, Receiver: {friend_request.receiver.username}, Status: {friend_request.status}")

