from django.urls import path
from .views import  RegisterView, LoginView, SubmitFinancialDataView, ChatView, VerifyTokenView

    
urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('submit/', SubmitFinancialDataView.as_view(), name="submit-financial-data"),
    path('chat/', ChatView.as_view(), name="chat"),
    path("verify-token", VerifyTokenView.as_view()),
]