from django.db import models
from django.utils.timezone import now


class CodeManager(models.Manager):
    def actives(self):
        current = now()
        queryset = self.get_queryset()
        return queryset.filter(time_start__lte=current, time_end__gt=current, is_active=True)
