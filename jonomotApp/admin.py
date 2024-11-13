from django.contrib import admin
from .models import *

admin.site.register(CustomUser)


admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(AllData)
admin.site.register(Category)
admin.site.register(PollView)
admin.site.register(OptionChoice)
admin.site.register(logo)