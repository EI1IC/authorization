from django.urls import path
from . import views, admin_views

urlpatterns = [
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/profile/", views.ProfileView.as_view(), name="profile"),
    path("mock/posts/", views.PostMockView.as_view(), name="posts"),
    path("admin/rules/", admin_views.AdminRulesView.as_view(), name="admin_rules"),
    path("admin/assign-role/", admin_views.AdminAssignRoleView.as_view(), name="admin_assign"),
]