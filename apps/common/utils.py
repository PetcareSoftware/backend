from datetime import datetime, time
from django.utils import timezone


def aware_datetime_for_slot(date, start_time: time):
    naive = datetime.combine(date, start_time)
    return timezone.make_aware(naive, timezone.get_current_timezone())
