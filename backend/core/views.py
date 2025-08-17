
from django.shortcuts import render, redirect
from .models import Product
from .forms import ContactForm

def index(request):
    products = Product.objects.all()[:4]
    return render(request, 'index.html', {'products': products})

def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})
