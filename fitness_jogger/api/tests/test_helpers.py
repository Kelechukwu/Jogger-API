from django.test import TestCase
from api.helpers import parse_query_string

class QueryParserTestCase(TestCase):
    def test_it_supports_basic_keywords(self):
        """This verifies that the URL query parser includes
           or, and, eq (equals), ne (not equals), gt (greater than),
           lt (lower than)
        """

        query = "(date eq '2016-05-01') AND ((distance gt 20) OR (distance lt 10))"
        expectation = "Q(date__exact='2016-05-01') & Q(distance__gt=20) | Q(distance__lt=10)"

        django_Q_string =  parse_query_string(query)

        self.assertEqual(django_Q_string, expectation)