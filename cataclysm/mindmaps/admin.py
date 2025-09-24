from django.contrib import admin
from .models import MindMap, MindMapNode

class MindMapNodeInline(admin.TabularInline):
    model = MindMapNode
    extra = 1

@admin.register(MindMap)
class MindMapAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "updated_at")
    inlines = [MindMapNodeInline]

@admin.register(MindMapNode)
class MindMapNodeAdmin(admin.ModelAdmin):
    list_display = ("label", "mindmap", "parent", "x", "y")
    list_filter = ("mindmap",)
    search_fields = ("label",)
