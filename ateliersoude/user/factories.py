from factory.django import DjangoModelFactory
from faker import Factory

from ateliersoude.user.models import Organization

faker = Factory.create()


class OrganizationFactory(DjangoModelFactory):
    active = faker.boolean()
    name = faker.word()

    class Meta:
        model = Organization
