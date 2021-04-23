from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate, logout
from rest_framework import status
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import UserSerializer, ChangePasswordSerializer, PublicUserSerializer, RecoveryPasswordSerializer, NotificationSerializer
from .models import User, Friend_Request, Notification
from .permissions import RightUserOnly
from datetime import timedelta, datetime
from django.utils import timezone


class NotificationsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = self.request.user
            serializer = NotificationSerializer(user.notifications)
            return Response( user.notifications.updates, status=status.HTTP_200_OK)
        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST) 


class FollowersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = self.request.user
            following = [follow.username for follow in user.following.all()]
            followers = [follower.username for follower in user.followers.all()]
            return Response({'following': following, 'followers': followers}, status=status.HTTP_200_OK)

        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST) 

    def post(self, request, username):
        try:
            user = self.request.user
            to_user = User.objects.get(username=username)
            if to_user.username != user.username:
                followers = user.following.all()
                if to_user in followers:
                    user.following.remove(to_user)
                    return Response({'message': f'You stopped following {to_user}'}, status=status.HTTP_200_OK)
        
                else:   
                    user.following.add(to_user)
                    return Response({'message': f'You started following {to_user}'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST) 
        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST) 


class FriendViews(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = self.request.user
            friends = user.get_friends()
            return Response({'friends': friends}, status=status.HTTP_200_OK)

        except Exception as errors:
                return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST) 

    def post(self, request, userID=None, requestID=None):
        if request.path.startswith('/api/send_friend_request/') and userID is not None:
            try:
                from_user = self.request.user
                to_user = User.objects.get(id=userID)

                if (User.objects.filter(friends=from_user).first() and User.objects.filter(friends=to_user).first()):
                    return Response({'message': 'You are already friends'}, status=status.HTTP_400_BAD_REQUEST)
                
                friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)

                if created:
                    updates = from_user.notifications.updates
                    friend_request = {"title": f'{from_user.username} enviou uma solicitação de amizade!', "link": f'friend_request_id={friend_request.id}'}
                    updates['notifications'].append(friend_request)
                    
                    user_notifications = Notification.objects.get(notifications_id=to_user.notifications.id)
                    user_notifications.updates = updates
                    user_notifications.save()
                    return Response({'message': 'Friend request sent'},status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Friend request was already sent'}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as errors:
                return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)  

        if request.path.startswith('/api/accept_friend_request/') and requestID is not None:
            try:
                friend_request = Friend_Request.objects.get(id=requestID)
                
                if friend_request.to_user == self.request.user:
                    friend_request.to_user.friends.add(friend_request.from_user)
                    friend_request.from_user.friends.add(friend_request.to_user)
                    friend_request.delete()
                    
                    from_user = User.objects.get(id=requestID)
                    to_user = self.request.user
                    updates = from_user.notifications.updates
                    friend_notification = {"title": f'{to_user.username} aceitou sua solicitação de amizade!', "link": f'friend_request_id={friend_request.id}'}
                    updates['notifications'].append(friend_notification)
                    
                    user_notifications = Notification.objects.get(notifications_id=from_user.notifications.id)
                    user_notifications.updates = updates
                    user_notifications.save()

                    return Response('friend request accepted', status=status.HTTP_200_OK)
                else:
                    return Response('friend request not accepted', status=status.HTTP_200_OK)

            except Exception as errors:
                return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)


class ExpiringTokenAuthentication(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    model = User

    def get(self, request):
        print(self.request.user.auth_token)
        try:
            token = Token.objects.get(key=self.request.user.auth_token)
        except Token.DoesNotExist:
            return Response({'error': "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED)

        if not token.user.is_active:
            return Response({'error': "User is not active"}, status=status.HTTP_401_UNAUTHORIZED)

        is_ispired = token.created - timezone.now()
        if is_ispired < (- timedelta(days = 5)):
            token.delete()
            return Response({'error': 'Token is expired'}, status=status.HTTP_401_UNAUTHORIZED)

        else:
           return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = []

    def get(self, request):
        try:
            self.request.user.auth_token.delete()
            logout(request)
            return Response({'message': 'logout successfully'}, status=status.HTTP_200_OK)

        except Exception as errors:
            logout(request)
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)  

    def post(self, request):
        user = authenticate(
            email=request.data['email'], password=request.data['password'])
        if user is not None:
            token = Token.objects.get_or_create(user=user)[0]
            update_last_login(None, user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class AccountView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = []

    def get(self, request):
        if self.request.user.is_authenticated:
            try:
                user = self.request.user
                serializer = UserSerializer(user)
                return Response(serializer.data)

            except Exception as errors:
                return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.all()
        serializer = PublicUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_notifications = Notification.objects.create(updates={"notifications": [{"title": "Bem vindo a rede do Stackle!", "link": "page=profile"}]})
            user = User.objects.create_user(**request.data, notifications=user_notifications)
            serializer = UserSerializer(user)
            user = authenticate(
            email=request.data['email'], password=request.data['password'])
            token = Token.objects.get_or_create(user=user)[0]

        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({**serializer.data, 'token': token.key}, status=status.HTTP_201_CREATED)
    
    def patch(self, request):
        try:
            user = self.request.user
            serializer = UserSerializer(user, data=request.data, partial=True)
            
            if serializer.is_valid():
                if (request.data.get('password') is not None):
                    return Response({'error': 'You cannot change your password here'}, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()
                return Response({'message': 'Account updated successfully'}, status=status.HTTP_200_OK)

            else:
                return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)
            
    def delete(self, request):
        try:
            user = self.request.user
            user.delete()
            return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    model = User

    def get_object(self, queryset=None):
        user = self.request.user
        return user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({ "old_password": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data.get("new_password"))
            user.save()
            user.auth_token.delete()
            logout(request)
            return Response({ 'message': 'Password updated successfully' }, status=status.HTTP_200_OK)


class RecoveryPasswordView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email__exact=request.data.get('email'))
            serializer = RecoveryPasswordSerializer(data=request.data)
            
            if serializer.is_valid():
                if not request.data.get('new_password') == request.data.get('confirm_password'):
                    return Response({ "message": "Please confirm you password correctly" }, status=status.HTTP_400_BAD_REQUEST)
                
                user.set_password(serializer.data.get("new_password"))
                user.save()
                return Response({ 'message': 'Password updated successfully' }, status=status.HTTP_200_OK)

        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)