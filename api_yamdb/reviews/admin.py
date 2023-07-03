from django.contrib import admin
from .models import Title, Category, Genre, Review, Comment, User
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class UserResource(resources.ModelResource):

    class Meta:
        model = User


class TitleResource(resources.ModelResource):

    class Meta:
        model = Title


class CategoryResource(resources.ModelResource):

    class Meta:
        model = Category


class GenreResource(resources.ModelResource):

    class Meta:
        model = Genre


class ReviewResource(resources.ModelResource):

    class Meta:
        model = Review


class CommentResource(resources.ModelResource):

    class Meta:
        model = Comment


class UserAdmin(ImportExportModelAdmin):
    resource_classes = [UserResource]
    list_display = [f.name for f in User._meta.fields]


class TitleAdmin(ImportExportModelAdmin):
    resource_classes = [TitleResource]
    list_display = [f.name for f in Title._meta.fields]


class GenreAdmin(ImportExportModelAdmin):
    resource_classes = [GenreResource]
    list_display = [f.name for f in Genre._meta.fields]


class CategoryAdmin(ImportExportModelAdmin):
    resource_classes = [CategoryResource]
    list_display = [f.name for f in Category._meta.fields]


class ReviewAdmin(ImportExportModelAdmin):
    resource_classes = [ReviewResource]
    list_display = [f.name for f in Review._meta.fields]


class CommentAdmin(ImportExportModelAdmin):
    resource_classes = [CommentResource]
    list_display = [f.name for f in Comment._meta.fields]


admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
