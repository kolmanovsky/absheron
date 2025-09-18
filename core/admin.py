from django.contrib import admin
from .models import Text, Image, Tag, Node, NodeText, NodeImage
from django import forms
from ckeditor.widgets import CKEditorWidget

class TextAdminForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = "__all__"
        widgets = {
            "body": CKEditorWidget(config_name="default"),
        }

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    form = TextAdminForm
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

class NodeTextInline(admin.TabularInline):
    model = NodeText
    extra = 0

class NodeImageInline(admin.TabularInline):
    model = NodeImage
    extra = 0
    
@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("title", "parent", "position", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [NodeTextInline, NodeImageInline]
    ordering = ("parent__id", "position", "title")