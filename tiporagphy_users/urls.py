from django.urls import path
from tiporagphy_users.views import (
    CreateUserView,
    LoginPlatformView,
    LogoutPlatformView,
    CheckUserInGroup,
    UserManagementView,
)

urlpatterns = [
    path("<int:pk>", UserManagementView.as_view(), name="UserManagementView"),
    path("", CreateUserView.as_view(), name="CreateUserView"),
    path("log_in", LoginPlatformView.as_view(), name="LoginPlatformView"),
    path("log_out", LogoutPlatformView.as_view(), name="LogoutPlatformVie"),
    path("check", CheckUserInGroup.as_view(), name="CheckUserInGroup"),
]
