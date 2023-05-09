from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CreateUserView, SendFriendRequestView, RespondToFriendRequestView,\
    RevokeFriendRequestView, GetIncomingFriendRequestsView, GetOutgoingFriendRequestsView, GetFriendsView,\
    GetStatusWithUserView, RemoveFriendView

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-user', CreateUserView.as_view(), name='create_user'),
    path('friends/send-request', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friends/respond-to-request', RespondToFriendRequestView.as_view(), name='respond_to_friend_request'),
    path('friends/revoke-request', RevokeFriendRequestView.as_view(), name='revoke_friend_request'),
    path('friends/get-incoming-requests', GetIncomingFriendRequestsView.as_view(),
         name='get_incoming_friend_requests'),
    path('friends/get-outgoing-requests', GetOutgoingFriendRequestsView.as_view(),
         name='get_outgoing_friend_requests'),
    path('friends/get-friends', GetFriendsView.as_view(), name='get_friends'),
    path('friends/get-status-with-user/<slug:username>', GetStatusWithUserView.as_view(), name='get_status_with_user'),
    path('friends/remove-friend', RemoveFriendView.as_view(), name='remove_friend'),
]
