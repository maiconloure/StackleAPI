from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.authtoken.models import Token

class RightUserOnly(BasePermission):
    def has_object_permission(self, request, view, post):
        request.user.has_perm('posts.author', post)