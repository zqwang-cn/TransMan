from django.contrib import admin
from .models import Mine,CoalType,Scale,Card,Balance,UserScaleInfo,TransRec,OutRec

# Register your models here.
admin.site.register(Mine)
admin.site.register(Scale)
admin.site.register(CoalType)
admin.site.register(Card)
admin.site.register(Balance)
admin.site.register(UserScaleInfo)
class ReadonlyAdmin(admin.ModelAdmin):
    readonly_fields=('setoff_time','qrcode')
admin.site.register(TransRec,ReadonlyAdmin)
admin.site.register(OutRec,ReadonlyAdmin)
