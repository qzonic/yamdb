from rest_framework import permissions


class IsModeratorOrReadOnly(permissions.BasePermission):
    """ Права модератора """

    message = 'Нужны прав модератора или выше!'

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and request.user.is_moderator)
        )


class IsAdmin(permissions.BasePermission):
    """ Права админа """

    message = 'Нужны прав админа или выше!'

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated
                    and (request.user.is_admin
                         or request.user.is_superuser
                         )
                    )


class IsAuthor(permissions.BasePermission):
    """ Права автора """

    message = 'Изменять чужой контент запрещенно!'

    def has_object_permission(self, request, view, obj):
        return bool(request.user == obj.author)


class IsAdminOrReadOnly(permissions.BasePermission):
    """ Права админа или только для чтения """

    message = 'Нужны прав админа или выше!'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin)
                or (request.user.is_authenticated
                    and request.user.is_superuser)
                )


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """ Права суперюзера """

    message = 'Нужны права суперюзера!'

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_superuser)
        )


class IsAuthorOrReadOnly(permissions.BasePermission):

    message = 'Изменение чужого контента запрещено!'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator
                )


class ReviewAndCommentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
                or request.user.is_superuser
                )
