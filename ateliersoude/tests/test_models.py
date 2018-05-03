from django.test import TestCase


class UserModels(TestCase):
    def abc(self):
        print("oij")


class PlateformeWebModels(TestCase):
    def test_abc(self):
        self.assertEqual("abc", "abc")
        print("oij")
        return True
