# apps/products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListCreateView.as_view(), name='product-list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<int:product_id>/purchase/', views.PurchaseProductView.as_view(), name='purchase-product'),
    path('my-products/', views.MyProductsView.as_view(), name='my-products'),
    path('bought-products/', views.BoughtProductsView.as_view(), name='bought-products'),
    path('sold-products/', views.SoldProductsView.as_view(), name='sold-products'),
    # 心愿相关路由
    path('wishes/', views.WishItemListView.as_view(), name='wish-list'),
    path('my-wishes/', views.UserWishItemsView.as_view(), name='my-wishes'),
    # 聊天相关路由
    path('chat/messages/', views.ChatMessageView.as_view(), name='chat-messages'),
    path('chat/conversation/<int:user_id>/', views.ChatConversationView.as_view(), name='chat-conversation'),
    path('chat/unread/', views.UnreadMessagesView.as_view(), name='chat-unread'),
    path('contact/seller/<int:product_id>/', views.ContactSellerView.as_view(), name='contact-seller'),
    path('contact/wish-user/<int:wish_id>/', views.ContactWishUserView.as_view(), name='contact-wish-user'),
    # 商品评价路由
    path('<int:product_id>/evaluate/', views.ProductEvaluationView.as_view(), name='product-evaluate'),
    # 卖家负面评价路由
    path('negative-evaluations/', views.SellerNegativeEvaluationsView.as_view(), name='seller-negative-evaluations'),
    # 申诉相关路由
    path('appeal/<int:evaluation_id>/', views.AppealEvaluationView.as_view(), name='appeal-evaluation'),
    path('admin/appeals/', views.AdminAppealManagementView.as_view(), name='admin-appeals'),
    # 管理员专用路由
    path('admin/', views.AdminProductManagementView.as_view(), name='admin-products'),
    path('admin/wishes/', views.AdminWishManagementView.as_view(), name='admin-wishes'),
]