from django.urls import path
from . import views
from .views import UsersListView, UsersChangeRoleView

urlpatterns = [
    path('users', UsersListView.as_view()),
    path('users/<int:pk>', UsersListView.as_view()),
    path('users/change', UsersChangeRoleView.as_view()),
]