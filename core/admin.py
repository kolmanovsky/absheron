from django.contrib import admin
from .models import Text, Image, Tag


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at")
    search_fields = ("title", "body")
    list_filter = ("created_at", "tags")


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_by", "uploaded_at")
    list_filter = ("uploaded_at", "tags")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)