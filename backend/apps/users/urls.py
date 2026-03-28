# backend/apps/users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('csrf-token/', views.GetCSRFToken.as_view(), name='csrf-token'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserInfoUpdateView.as_view(), name='profile-update'),
    path('password-reset-request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # 余额相关路由
    path('recharge/', views.RechargeView.as_view(), name='recharge'),
    path('withdraw/', views.WithdrawView.as_view(), name='withdraw'),
    # 管理员专用路由
    path('admin/users/', views.AdminUserManagementView.as_view(), name='admin-users'),
    path('admin/users/<int:user_id>/<str:action>/', views.AdminUserManagementView.as_view(), name='admin-user-action'),
    path('admin/analytics/', views.AnalyticsDashboardView.as_view(), name='admin-analytics'),
    path('admin/user-stats/', views.UserStatsView.as_view(), name='user-stats'),
    # 信用分相关路由
    path('credit-score/', views.CreditScoreView.as_view(), name='credit-score'),
    path('credit-deductions/', views.CreditDeductionListView.as_view(), name='credit-deductions'),
    path('credit-appeal/<int:deduction_id>/', views.CreditAppealView.as_view(), name='credit-appeal'),
]