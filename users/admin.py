from django.contrib import admin
from .models import Detection, Alert

admin.site.register(Detection)
admin.site.register(Alert)