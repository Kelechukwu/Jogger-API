from django.test import TestCase

from api.models import User, USER


class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(email="test@email")

    def test_user_default_role(self):
        """This test verifies that the default user role is  USER"""
        user = User.objects.get(email="test@email")
        self.assertEqual(user.role, USER)
