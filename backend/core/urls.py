from django.urls import path
from .views import LoginView, TokenRefreshView, ChatView, InitialGreetingView

urlpatterns = [
    path('api/token/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/chat/', ChatView.as_view(), name='chat'),
    path('api/greeting/', InitialGreetingView.as_view(), name='initial_greeting'),
]