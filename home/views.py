import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q, OuterRef, Subquery, Max



@login_required
def home(request):
    return render(request, 'home/home.html', {})

