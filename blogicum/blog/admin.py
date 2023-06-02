from django.contrib import admin

from .models import Post, Category, Location


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'category',
        'location',
        'pub_date',
        'is_published',
        'created_at',
        'comment_count'
    )
    list_editable = (
        'is_published',
        'category',
        'location',
    )

    @admin.display(description='Количество комментариев')
    def comment_count(self, obj):
        return obj.comments.count()


@admin.register(Category)
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


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
