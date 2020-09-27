from django.contrib import admin

from .models import Question, Nonuser, Scratch, Item

admin.site.register(Question)
admin.site.register(Nonuser)
admin.site.register(Scratch)
admin.site.register(Item)
