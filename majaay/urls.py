from django.urls import path
from . import views 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



urlpatterns = [













    path('login/', views.seller_login, name='seller_login'),
    path('logout/', views.seller_logout, name='seller_logout'),
    path('seller/register/', views.seller_register, name='seller_register'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/product/add/', views.product_create, name='product_create'),
    path('categories/', views.category_list, name='category_list'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('products/<int:pk>/', views.product_detail_and_order, name='product_detail'),
    # manager urls
    path('manager/sellers/pending/', views.pending_sellers, name='pending_sellers'),
    path('manager/sellers/approve/<int:pk>/', views.approve_seller, name='approve_seller'),
    path('manager/products/pending/', views.pending_products, name='pending_products'),
    path('manager/products/approve/<int:pk>/', views.approve_product, name='approve_product'),

    path('buyers/manage/', views.manage_buyers, name='manage_buyers'),
    path('sellers/manage/', views.manage_sellers, name='manage_sellers'),


























]
