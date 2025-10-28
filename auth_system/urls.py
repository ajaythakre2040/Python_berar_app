from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from auth_system.views.auth_view import (
    
    DealerLoginView,
    LeadLoginView,
    LeadTwoFactorVerifyView,
    UserListCreateView,
    LoginView,
    TwoFactorVerifyView,
    ResendOTPView,
    LogoutView,
    # ResetUserPasswordView,
    # UnblockLoginAttemptsView,
)


urlpatterns = [
    # Authentication URLs
    path("user/", UserListCreateView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("verify-otp/", TwoFactorVerifyView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("lead-login/", LeadLoginView.as_view(), name="lead-login"),
    path("lead-verify-otp/", LeadTwoFactorVerifyView.as_view(), name="lead-verify-otp"),
    path("dealer-login/", DealerLoginView.as_view(), name="dealer-login"),
    # path("reset-user-password/", ResetUserPasswordView.as_view(), name="reset"),
    # path(
    #     "unblock-login-attempts/",
    #     UnblockLoginAttemptsView.as_view(),
    #     name="unblock-login-attempts",
    # ),
]
