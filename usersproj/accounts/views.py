from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile, Roles, Access, UserRole
from .serializers import UserSerializer, UserRegistrationSerializer
from .permissions import check_permission


class UsersListView(APIView):
    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided"}, status=401)

        pk = kwargs.get("pk", None)
        if pk is not None:

            try:
                obj = UserProfile.objects.get(pk=pk)
            except UserProfile.DoesNotExist:
                return Response({"detail": "User profile does not exist"}, status=404)

            if obj == request.user:
                allowed = (check_permission(request.user, 'users', "read") or
                           check_permission(request.user, 'users', "read_all"))
            else:
                allowed = check_permission(request.user, 'users', "read_all")

            if not allowed:
                return Response({"detail": "Permission denied"}, status=403)

            serializer = UserSerializer(obj)
            return Response({'user': serializer.data})

        if not check_permission(request.user, 'users', "read_all"):
             return Response({"detail": "Permission denied"}, status=403)

        objs = UserProfile.objects.all()
        return Response({"users": UserSerializer(objs, many=True).data})

    def post(self, request):
        if request.data.get("password_confirmation", None) is None:
            return Response({"error": "Password confirmation required"}, status=400)

        if request.data.get("password") != request.data.get("password_confirmation"):
            return Response({"error": "Passwords must match"}, status=400)

        obj = UserRegistrationSerializer(data=request.data)

        obj.is_valid(raise_exception=True)
        obj.save()

        return Response({"user": UserSerializer(obj.instance).data})

    def put(self, request, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided"}, status=401)

        pk = kwargs.get("pk", None)

        if pk is None:
            return Response({"error": "Method PUT is not allowed"}, status=400)

        try:
            instance = UserProfile.objects.get(pk=pk)
        except:
            return Response({"error": "User does not exist"}, status=404)

        if instance == request.user:
            allowed = (check_permission(request.user, 'users', 'update') or
                       check_permission(request.user, 'users', 'update_all'))
        else:
            allowed = check_permission(request.user, 'users', 'update_all')

        if not allowed:
            return Response({"detail": "Permission denied"}, status=403)

        if request.data.get("password", None) is not None:

            if request.data.get("password_confirmation", None) is None:
                return Response({"error": "Password confirmation required"}, status=400)

            if request.data.get("password") != request.data.get("password_confirmation"):
                return Response({"error": "Passwords must match"}, status=400)

        serializer = UserRegistrationSerializer(data=request.data, instance=instance, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'user': serializer.data})

    def delete(self, request, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided"}, status=401)

        pk = kwargs.get("pk", None)

        if pk is None:
            return Response({"error": "Method DELETE is not allowed"}, status=400)

        try:
            instance = UserProfile.objects.get(pk=pk)
        except:
            return Response({"error": "User does not exist"}, status=404)

        if instance == request.user:
            allowed = (check_permission(request.user, 'users', 'delete') or
                       check_permission(request.user, 'users', 'delete_all'))
        else:
            allowed = check_permission(request.user, 'users', 'delete_all')

        if not allowed:
            return Response({"detail": "Permission denied"}, status=403)

        serializer = UserRegistrationSerializer(instance=instance, data={'is_active': False}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'user': serializer.data})


class UsersChangeRoleView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided"}, status=401)

        admin_role = Roles.objects.get(name='admin')
        if not UserRole.objects.filter(user=request.user, role=admin_role).exists():
            return Response({"detail": "Permission denied"}, status=403)

        user_id = request.query_params.get('userid')
        new_role_name = request.query_params.get('newrole')

        if not user_id or not new_role_name:
            return Response({"detail": "Both 'userid' and 'newrole' query parameters are required"}, status=400)

        user = get_object_or_404(UserProfile, pk=user_id)
        new_role = get_object_or_404(Roles, name=new_role_name)

        UserRole.objects.filter(user=user).update(role=new_role)

        return Response({"detail": f"Role '{new_role_name}' assigned to user {user_id}"}, status=200)

