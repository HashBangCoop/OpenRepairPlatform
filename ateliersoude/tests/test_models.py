from django.test import TestCase
from plateformeweb.models import Organization, OrganizationPerson, OrganizationVisitor, OrganizationMember, OrganizationVolunteer
from users.models import CustomUser


def create_organization(_name="UnitTest",
                        _description="Organisation de test",
                        _active=True):
    return Organization.objects.create(name=_name,
                                       description=_description,
                                       active=_active)


def create_person(_role, _organization, _user):
    return OrganizationPerson.objects.create(role=_role,
                                      organization=_organization,
                                      user=_user)


def create_visitor():
    return OrganizationVisitor.objects.create()


def create_user(_email="Test@test.fr", _password="qsdfjklm2",
                _first_name="Test",
                _last_name="Unitaire"):
    return CustomUser.objects.create_user(email=_email,
                                          password=_password,
                                          first_name=_first_name,
                                          last_name=_last_name)


def create_user_no_password(_email="Testnopasswd@test.fr",
                            _first_name="Test",
                            _last_name="Unitaire 2"):
    return CustomUser.objects.create_user(email=_email,
                                          first_name=_first_name,
                                          last_name=_last_name)


def create_superuser(_email="Testsuperuser@test.fr", _password="qsdfjklm2",
                     _first_name="Test",
                     _last_name="Unitaire 3"):
    return CustomUser.objects.create_superuser(email=_email,
                                               password=_password,
                                               first_name=_first_name,
                                               last_name=_last_name)


class CustomUserModels(TestCase):
    def test_create_user(self):
        user1 = create_user()
        self.assertTrue(isinstance(user1, CustomUser))
        # Todo : test parameters / isactive etc
        # Todo : test email duplication
        # Todo : test special characters numbers etc
        # Todo : assert error no email

    # def test_create_user_no_password(self):

    def test_create_user_no_email(self):
        with self.assertRaises(ValueError):
            create_user(_email=None)

    def test_create_superuser(self):
        superuser1 = create_superuser()

        self.assertTrue(isinstance(superuser1, CustomUser))
        # Todo : test parameters
        # Todo : test is_staff, is_superuser

    def test_full_name(self):
        user = create_user()
        full_name = user.get_full_name()
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(full_name, "Test Unitaire")

    def test_short_name(self):
        user = create_user()
        first_name = user.get_short_name()
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(first_name, "Test")

    def test_absolute_url(self):
        user = create_user()
        absolute_url = user.get_absolute_url()
        self.assertEqual(absolute_url, "/users/1/")

    # def test_email_user(self):
    # def test__iter__(self):


class PlateformeWebModels(TestCase):
    def test_organization_creation(self):
        orga = create_organization(_name="UnitTest")
        self.assertTrue(isinstance(orga, Organization))
        self.assertEqual(orga.__str__(), orga.name)
        self.assertEqual(orga.__str__(), "UnitTest")

    def test_create_person(self):
        orga = create_organization(_name="UnitTestPerson Orga")
        self.assertEqual(orga.__str__(), "UnitTestPerson Orga")
        user = create_user()
        visitor = create_person(_role=OrganizationPerson.VISITOR,
                                _organization=orga,
                                _user=user)
        self.assertEqual(visitor.role, OrganizationPerson.VISITOR)

    # def test_place(self):
    # def test_condition(self):
    # def test_activity(self):
    # def test_event(self):
    # def test_published_event(self):
