from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Relationship, User
from .serializers import CreateUserSerializer, FriendRequestSerializer, RespondToFriendRequestSerializer


class CreateUserView(APIView):
    @staticmethod
    def post(request) -> Response:
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            user = serializer.save()
            update_last_login(None, user)
            token = TokenObtainPairSerializer.get_token(user)
            return Response({'refresh': str(token), 'access': str(token.access_token)}, status=201)
        if serializer.errors.get('username') and serializer.errors.get('username')[0].code == 'unique':
            return Response(serializer.errors, status=409)
        else:
            return Response(serializer.errors, status=400)


class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request: Request) -> Response:
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            another_user_username = serializer.validated_data['username']
            another_user = User.objects.filter(username=another_user_username).first()
            if not another_user:
                return Response({'details': f'User {another_user_username} does not exist'}, status=404)
            if another_user == request.user:
                return Response({'username': "You can not send friend request to yourself"}, status=400)
            relationship = Relationship.objects.filter(from_user=request.user, to_user=another_user).first()
            if relationship:
                if relationship.status:
                    return Response({'username': f'You are already friends with {another_user_username}'}, status=400)
                return Response(status=200)
            reversed_relationship = Relationship.objects.filter(from_user=another_user, to_user=request.user)
            if reversed_relationship:
                # Find friend request from <another_user>, so automatically accept it
                reversed_relationship.update(status=True)
                Relationship.objects.create(from_user=request.user, to_user=another_user, status=True)
                return Response(status=202)
            else:
                Relationship.objects.create(from_user=request.user, to_user=another_user)
                return Response(status=201)
        return Response(serializer.errors, status=400)


class RespondToFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request: Request) -> Response:
        serializer = RespondToFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            another_user_username = serializer.validated_data['username']
            another_user = User.objects.filter(username=another_user_username).first()
            if not another_user:
                return Response({'details': f'User {another_user_username} does not exist'}, status=404)
            relationship = Relationship.objects.filter(from_user=another_user, to_user=request.user).first()
            if not relationship or relationship.status:
                return Response({'details': f'Friend request from {another_user_username} does not exist'}, status=404)
            if serializer.validated_data['action']:
                relationship.status = True
                relationship.save()
                Relationship.objects.create(from_user=request.user, to_user=another_user, status=True)
                return Response(status=202)
            else:
                relationship.delete()
                return Response(status=200)
        return Response(serializer.errors, status=400)


class RevokeFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request: Request) -> Response:
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            another_user_username = serializer.validated_data['username']
            another_user = User.objects.filter(username=another_user_username).first()
            if not another_user:
                return Response({'details': f'User {another_user_username} does not exist'}, status=404)
            relationship = Relationship.objects.filter(from_user=request.user, to_user=another_user).first()
            if not relationship or relationship.status:
                return Response({'details': f'Friend request to {another_user_username} does not exist'}, status=404)
            relationship.delete()
            return Response(status=200)
        return Response(serializer.errors, status=400)


class GetIncomingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request: Request) -> Response:
        usernames = list(map(
            lambda relationship: relationship.from_user.username,
            Relationship.objects.select_related('from_user').filter(to_user=request.user, status=False).all()
        ))
        return Response({'usernames': usernames}, status=200)


class GetOutgoingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request: Request) -> Response:
        usernames = list(map(
            lambda relationship: relationship.to_user.username,
            Relationship.objects.select_related('to_user').filter(from_user=request.user, status=False).all()
        ))
        return Response({'usernames': usernames}, status=200)


class GetFriendsView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request: Request) -> Response:
        usernames = list(map(
            lambda relationship: relationship.to_user.username,
            Relationship.objects.select_related('to_user').filter(from_user=request.user, status=True).all()
        ))
        return Response({'usernames': usernames}, status=200)


class GetStatusWithUserView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request: Request, username: str) -> Response:
        another_user = User.objects.filter(username=username).first()
        if not another_user:
            return Response({'details': f'User {username} does not exist'}, status=404)
        relationship = Relationship.objects.filter(from_user=request.user, to_user=another_user).first()
        if relationship:
            if relationship.status:
                return Response({'status': 'friends'}, status=200)
            return Response({'status': 'outgoing_request_sent'}, status=200)
        reversed_relationship = Relationship.objects.filter(from_user=another_user, to_user=request.user).first()
        if reversed_relationship:
            return Response({'status': 'have_incoming_request'}, status=200)
        return Response({'status': 'nothing'}, status=200)


class RemoveFriendView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request: Request):
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            another_user_username = serializer.validated_data['username']
            another_user = User.objects.filter(username=another_user_username).first()
            if not another_user:
                return Response({'details': f'User {another_user_username} does not exist'}, status=404)
            relationship = Relationship.objects.filter(from_user=request.user,
                                                       to_user=another_user,
                                                       status=True).first()
            if relationship:
                relationship.delete()
                Relationship.objects.filter(from_user=another_user, to_user=request.user, status=True).delete()
                return Response(status=202)
            return Response(status=200)
        return Response(serializer.errors, status=400)
