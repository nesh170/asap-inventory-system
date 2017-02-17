from django.contrib import admin
from .models import Item,Tag, Field, IntField, FloatField, ShortTextField, LongTextField

# Register your models here.
admin.site.register(Item)
admin.site.register(Tag)
admin.site.register(Field)
admin.site.register(IntField)
admin.site.register(FloatField)
admin.site.register(ShortTextField)
admin.site.register(LongTextField)
