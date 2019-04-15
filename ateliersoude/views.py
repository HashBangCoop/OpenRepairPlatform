from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import reverse


@login_required
def home(request):
    return HttpResponseRedirect(reverse("homepage"))
