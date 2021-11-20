from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Well)
admin.site.register(models.WellType)
admin.site.register(models.ProjectGroup)
admin.site.register(models.Code)
admin.site.register(models.Appl_mpz)
admin.site.register(models.Appl_mpz_data)
admin.site.register(models.Byer)
admin.site.register(models.Appl_byer)
admin.site.register(models.Appl_by_data)