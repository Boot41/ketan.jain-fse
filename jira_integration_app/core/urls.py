from django.urls import path
from .views import LoginView, ChatView, InitialGreetingView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('greeting/', InitialGreetingView.as_view(), name='greeting'),
]
