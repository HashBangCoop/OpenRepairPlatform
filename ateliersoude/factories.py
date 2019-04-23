import factory

from factory.django import DjangoModelFactory

from ateliersoude.user.models import CustomUser

USER_PASSWORD = "hackme"


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))

    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        self.set_password(USER_PASSWORD)
        self.save()
