from django.contrib import admin
from .models import Hub, Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "hub", "published_at"]
    search_fields = ["title", "published_at", "hub"]


admin.site.register(Hub)
admin.site.register(Article, ArticleAdmin)
