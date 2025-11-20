from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Instruments)
admin.site.register(Instrumenttypes)
admin.site.register(Alarmconfiguration)
admin.site.register(Calibrationrecords)
admin.site.register(Calibrationtestpoints)
admin.site.register(Controlsystems)
admin.site.register(Failurerecords)
admin.site.register(Instrumentdetails)
admin.site.register(Maintenancerecords)
admin.site.register(Manufacturers)
admin.site.register(Processunits)
admin.site.register(Sites)
admin.site.register(Spareparts)
admin.site.register(Subsystems)
admin.site.register(Tripinstruments)
admin.site.register(Tripsinterlocks)