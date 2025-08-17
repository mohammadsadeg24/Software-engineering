from django.contrib import admin
from .models import Category, Product, ContactMessage

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ContactMessage)
