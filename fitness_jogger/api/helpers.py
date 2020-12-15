import requests
from django.conf import settings


def get_weather_conditons(point):
    try:
        lon, lat = point.tuple
        params = {'lat': lat, 'lon': lon, 'appid': settings.WEATHER_API_KEY}
        response = requests.get(
            f'http://{settings.WEATHER_API}', params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.Timeout:
        return None


def parse_query_string(query):
    LOWER_THAN = ' lt '
    GREATER_THAN = ' gt '
    EQUALS = ' eq '
    NOT_EQUALS = ' ne '
    OR = ' OR '
    AND = ' AND '

    query = query.replace('(', 'Q(')
    query = query.replace('Q(Q(', 'Q(').replace('))', ')')
    query = query.replace('{', '(').replace('}', ')')
    query = query.replace(LOWER_THAN, '__lt=')
    query = query.replace(GREATER_THAN, '__gt=')
    query = query.replace(EQUALS, '__exact=')
    query = query.replace(AND, ' & ').replace(OR, ' | ')

    ne_index = query.find(NOT_EQUALS)
    while ne_index != -1:
        query = query.replace(NOT_EQUALS, '__exact=', 1)
        query_ne_index = query.rfind('Q', 0, ne_index)
        query = query[:query_ne_index] + '~Q' + query[query_ne_index + 1:]
        ne_index = query.find(NOT_EQUALS)

    return query
