from django.urls import path
from .views import LoginView, AccountView, ChangePasswordView, RecoveryPasswordView, FriendViews, ExpiringTokenAuthentication, NotificationsView, FollowersView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('refresh-token/', ExpiringTokenAuthentication.as_view()),
    path('logout/', LoginView.as_view()),
    path('users/', AccountView.as_view()),
    path('users/notifications/', NotificationsView.as_view()),
    path('users/password_change/', ChangePasswordView.as_view()),
    path('users/password_recovery/', RecoveryPasswordView.as_view()),
    path('send_friend_request/<int:userID>/', FriendViews.as_view(), name='send_friend_request'),
    path('accept_friend_request/<int:requestID>/', FriendViews.as_view(), name='accept friend request'),
    path('users/friends/', FriendViews.as_view()),
    path('users/followers/', FollowersView.as_view()),
    path('users/follow/<str:username>', FollowersView.as_view(), name='follow'),
    path('users/unfollow/<str:username>', FollowersView.as_view(), name='unfollow'),
]
