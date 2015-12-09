from django.contrib import admin
from .models import Mine,CoalType,UserMine

# Register your models here.
admin.site.register(Mine)
admin.site.register(CoalType)
admin.site.register(UserMine)
