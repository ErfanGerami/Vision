from django.contrib import admin
from .models import *
from django import forms


class StaffMemberInline(admin.TabularInline):
    model = StaffMember
    extra = 0


@admin.register(StaffTeam)
class StaffTeamAdmin(admin.ModelAdmin):
    inlines = [StaffMemberInline]


class MemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0
    can_delete = True


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fields = ('username', 'password',
              'verification_completed', 'payment_number', 'register_completed')
    inlines = [MemberInline]
