from django.contrib import admin
from .models import Mine,CoalType,Scale,CardValue

# Register your models here.
admin.site.register(Mine)
admin.site.register(Scale)
admin.site.register(CoalType)
admin.site.register(CardValue)
