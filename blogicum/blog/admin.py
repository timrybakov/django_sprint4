from django.contrib import admin
from .models import Post, Category, Location


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'category',
        'location',
        'pub_date',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category',
        'location',
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
