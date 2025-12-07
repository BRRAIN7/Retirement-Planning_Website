from django.urls import path
from .views import  RegisterView, LoginView, SubmitFinancialDataView, ChatView

    
urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('submit/', SubmitFinancialDataView.as_view(), name="submit-financial-data"),
    path('chat/', ChatView.as_view(), name="chat"),
]