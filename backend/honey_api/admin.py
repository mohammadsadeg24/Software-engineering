# # backend/honey_api/admin.py
# from django.contrib import admin
# from django.urls import path
# from django.http import HttpResponse
# from .mongo_models import products  # your MongoDB collection

# class MongoAdmin(admin.AdminSite):
#     site_header = "Mongo Admin"

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('mongo-products/', self.admin_view(self.show_products), name='mongo-products'),
#         ]
#         return custom_urls + urls

#     def show_products(self, request):
#         data = list(products.find())
#         return HttpResponse(str(data))

# mongo_admin = MongoAdmin(name='mongoadmin')
