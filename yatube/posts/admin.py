from django.contrib import admin
from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    list_display_links = ('pk', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'post', 'created', 'author', )
    search_fields = ('text',)
    list_display_links = ('author', 'post',)
    list_filter = ('created',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('author',)
    list_display_links = ('author', 'user')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
