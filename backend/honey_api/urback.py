# from django.conf import settings
# from django.urls import path
# from . import views
# from django.conf.urls.static import static

# urlpatterns = [

#     # Home
#     path('', views.home, name='home'),

#     # Categories
#     path('categories/', views.category_list, name='category_list'),
#     path('categories/create/', views.create_category, name='create_category'),
#     path('categories/<str:slug>/', views.category_detail, name='category_detail'),
#     # Existing URLs
#     path('', views.home, name='home'),
#     path('categories/', views.category_list, name='category_list'),
#     path('categories/create/', views.create_category, name='create_category'),
#     path('categories/<str:slug>/', views.category_detail, name='category_detail'),
#     path('profile/', views.profile_view, name='profile'),
#     path('contact/', views.contact_view, name='contact'),
#     path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    
#     # Products
#     path('products/', views.product_list, name='product_list'),
#     # path('products/create/', views.create_product, name='create_product'),
#     path('products/<str:slug>/', views.product_detail, name='product_detail'),
    
#     # Reviews
#     path('reviews/create/', views.create_review, name='create_review'),
#     path('products/<str:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    
#     # Cart
#     path('cart/', views.get_cart, name='get_cart'),
#     path('cart/add/', views.add_to_cart, name='add_to_cart'),
#     path('cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
#     path('cart/clear/', views.clear_cart, name='clear_cart'),
    
#     # Orders
#     path('orders/', views.get_orders, name='get_orders'),
#     path('orders/create/', views.create_order, name='create_order'),
#     path('orders/<str:order_id>/', views.get_order_detail, name='get_order_detail')
# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)