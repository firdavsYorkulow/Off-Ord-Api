from django.contrib import admin
from .models import Job, CommentModel, CommentLike, JobLike


# Register your models here.
# admin.site.register(Job)
# admin.site.register(Comment)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'job_type')
    search_fields = ('id', 'user__username', 'description', 'name')


@admin.register(CommentModel)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'body', 'post', 'created_time', 'active')
    search_fields = ('id', 'user__username', 'body')


@admin.register(JobLike)
class JobLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_time')
    search_fields = ('id', 'user__username')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'created_time')
    search_fields = ('id', 'user__username')
