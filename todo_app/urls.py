from django.urls import path
from .views import Signin, Login, Refresh, Signout, Todo,Index

urlpatterns = [
    path('', Index, name='index'),
    path('signin/', Signin.as_view(), name='user-signin'),
    path('login/', Login.as_view(), name='user-login'),
    path('refresh/', Refresh.as_view(), name='user-refresh'),
    path('signout/', Signout.as_view(), name="user-signout"),
    path('todo/', Todo.as_view(), name="user-todo"),
    path('todo/<int:pk>/', Todo.as_view(), name="user-todo-detail"),
]
