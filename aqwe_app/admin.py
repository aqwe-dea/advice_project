from django.contrib import admin
from .models import Advice, UserHistory, StripeSettings

admin.site.register(Advice)
admin.site.register(UserHistory)
admin.site.register(StripeSettings)
# Register your models here.
