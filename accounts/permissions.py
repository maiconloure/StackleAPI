from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.authtoken.models import Token

class RightUserOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET' or request.method == 'POST':
            return True

