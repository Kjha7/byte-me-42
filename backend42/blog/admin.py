# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Post, Profile, Like, Follow

admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Like)
admin.site.register(Follow)