from django.contrib import admin
from .models import Mine,CoalType,Scale,Card,Balance,UserScaleInfo

# Register your models here.
admin.site.register(Mine)
admin.site.register(Scale)
admin.site.register(CoalType)
admin.site.register(Card)
admin.site.register(Balance)
admin.site.register(UserScaleInfo)
