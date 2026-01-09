from django.shortcuts import render
from .models import Product
from django.contrib.auth.decorators import login_required
from .models import Order
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

@login_required
def checkout(request):
    if request.method == 'POST':
        Order.objects.create(
            user=request.user,
            completed=True
        )
        request.session['cart'] = []
        return redirect('success')

    return render(request, 'store/checkout.html')



@login_required
def home(request):
    products = Product.objects.all()
    cart = request.session.get('cart', [])
    cart_count = len(cart)

    return render(request, 'store/home.html', {
        'products': products,
        'cart_count': cart_count
    })


def product_page(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'store/product.html', {'product': product})
def cart(request):
    cart = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart)
    return render(request, 'store/cart.html', {'products': products})
from django.shortcuts import redirect

def add_to_cart(request, id):
    cart = request.session.get('cart', [])
    cart.append(id)
    request.session['cart'] = cart
    return redirect('cart')
def remove_from_cart(request, id):
    cart = request.session.get('cart', [])
    if id in cart:
        cart.remove(id)
    request.session['cart'] = cart
    return redirect('cart')
def order_success(request):
    return render(request, 'store/success.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'store/signup.html', {'form': form})
