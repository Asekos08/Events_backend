from drf_spectacular.utils import OpenApiParameter

get_event_list_parameter = [
            OpenApiParameter(name='id', description='search by id', required=False, type=int),
            OpenApiParameter(name='section', description='search friends by the section value', required=False, type=str, default='receiver')
        ]


