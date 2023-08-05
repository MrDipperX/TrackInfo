from django import template
from track_manage.models import *
from track_manage import insert_db
import os
from datetime import datetime, timedelta

register = template.Library()


@register.simple_tag()
def get_type_list() -> set:
    wagon_types = PassengerTrack.objects.values_list('wagon_type', flat=True)
    return set(wagon_types)


@register.simple_tag()
def get_model_list() -> set:
    wagon_models = PassengerTrack.objects.values_list('wagon_model', flat=True)
    return set(wagon_models)


@register.simple_tag()
def get_state_list() -> set:
    states_of_use = PassengerTrack.objects.values_list('state_of_use', flat=True)
    return set(states_of_use)


@register.simple_tag()
def wagon_count() -> int:
    return PassengerTrack.objects.all().count()


@register.simple_tag()
def dr_time_count() -> int:
    now = datetime.now() - timedelta(days=730)
    return PassengerTrack.objects.filter(last_dr__lte=now).count()


@register.simple_tag()
def kr2_time_count() -> int:
    now = datetime.now() - timedelta(days=3650)
    return PassengerTrack.objects.filter(last_kr_2__lte=now).count()


@register.simple_tag()
def kvr_time_count() -> int:
    now = datetime.now() - timedelta(days=7300)
    return PassengerTrack.objects.filter(last_kvr__lte=now).count()


@register.simple_tag()
def good_wagons() -> int:
    kvr = datetime.now() - timedelta(days=7300)
    kr1 = datetime.now() - timedelta(days=1825)
    kr2 = datetime.now() - timedelta(days=3650)
    dr = datetime.now() - timedelta(days=730)
    return PassengerTrack.objects.filter(last_dr__gte=dr, last_kvr__gte=kvr, last_kr_1__gte=kr1, last_kr_2__gte=kr2)\
        .count()


@register.simple_tag()
def min_id() -> int:
    return -(PassengerTrack.objects.values_list('id', flat=True).order_by("id").first() - 1)


@register.simple_tag()
def empty_table() -> bool:
    if PassengerTrack.objects.all().count() == 0:
        return False
    return True

