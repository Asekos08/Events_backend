from drf_spectacular.utils import OpenApiParameter
from .models import Category
from typing import List

get_event_list_parameter = [
            OpenApiParameter(name='search', description='search parameter', required=False, type=str),
            OpenApiParameter(name='event_type', description='event type parameter', required=False, type=str),
            OpenApiParameter(name='sort', description='sorting parameter. Either "ascending" or "descending"', required=False, type=str, default= 'ascending'),
            OpenApiParameter(name='categories', description='categories parameter', required=False, type={'type': 'array', 'minItems': 0}),
            OpenApiParameter(name='relation', description='realtion parameter. Either "all", "friends", or "user"', required=False, type=str, default= 'all'),
        ]


