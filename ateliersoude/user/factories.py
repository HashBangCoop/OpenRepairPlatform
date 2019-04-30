import factory
from factory.django import DjangoModelFactory

from faker import Factory

from ateliersoude.user.models import Organization, CustomUser

faker = Factory.create()
USER_PASSWORD = "hackme"


class OrganizationFactory(DjangoModelFactory):
    active = faker.boolean()
    name = faker.word()

    class Meta:
        model = Organization


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: "user{0}@example.com".format(n))

    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        self.set_password(USER_PASSWORD)
        self.save()
