from django.contrib import admin
from .models import *
# Register your models here.


class LinkInline(admin.TabularInline):
    model = Link
    extra = 0
    can_delete = True


@admin.register(Content)
class StaffTeamAdmin(admin.ModelAdmin):
    inlines = [LinkInline]
