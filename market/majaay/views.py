from django.shortcuts import get_object_or_404

def category_products(request, slug):
    from .models import Category, Product
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, approved=True)
    # Annotate each product with a price_with_markup attribute
    from decimal import Decimal, ROUND_HALF_UP
    for p in products:
        p.price_with_markup = int((p.price * Decimal('1.05')).to_integral_value(rounding=ROUND_HALF_UP))
    return render(request, 'majaay/category_products.html', {'category': category, 'products': products})
from django.contrib.auth.decorators import user_passes_test

def product_detail_and_order(request, pk):
    from .models import Product, OrderForm
    product = Product.objects.filter(pk=pk, approved=True).first()
    if not product:
        from django.http import Http404
        raise Http404()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            return render(request, 'majaay/order_thanks.html', {'order': order})
    else:
        form = OrderForm()
    return render(request, 'majaay/product_detail.html', {'product': product, 'form': form})

# Manager/Owner: Manage buyers
@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def manage_buyers(request):
    from .models import Order
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'majaay/manage_buyers.html', {'orders': orders})

# Manager/Owner: Manage sellers
@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def manage_sellers(request):
    from .models import SellerProfile
    sellers = SellerProfile.objects.all().order_by('-registration_date')
    return render(request, 'majaay/manage_sellers.html', {'sellers': sellers})
from django.contrib.auth.decorators import user_passes_test

def product_detail_and_order(request, pk):
    from .models import Product, OrderForm
    product = Product.objects.filter(pk=pk, approved=True).first()
    if not product:
        from django.http import Http404
        raise Http404()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            return render(request, 'majaay/order_thanks.html', {'order': order})
    else:
        form = OrderForm()
    return render(request, 'majaay/product_detail.html', {'product': product, 'form': form})

# Manager/Owner: Manage buyers
@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def manage_buyers(request):
    from .models import Order
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'majaay/manage_buyers.html', {'orders': orders})

# Manager/Owner: Manage sellers
@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def manage_sellers(request):
    from .models import SellerProfile
    sellers = SellerProfile.objects.all().order_by('-registration_date')
    return render(request, 'majaay/manage_sellers.html', {'sellers': sellers})
# Seller login/logout views
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect

def seller_login(request):
    if request.user.is_authenticated:
        return redirect('seller_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_seller():
            login(request, user)
            return redirect('seller_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a seller account.')
    return render(request, 'majaay/seller_login.html')

def seller_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
# Home page view
from .models import Category

from django.shortcuts import redirect
def home(request):
    return redirect('product_list')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings

from .models import Product, SellerProfile
from .models import SellerRegistrationForm, ProductForm, OrderForm

# Create your views here.
def seller_register(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log user in (optional) or redirect to a 'registration complete' page
            from django.contrib.auth import login
            login(request, user)
            return redirect('seller_dashboard')
    else:
        form = SellerRegistrationForm()
    return render(request, 'majaay/seller_register.html', {'form': form})


@login_required
def seller_dashboard(request):
    # Only sellers allowed
    if not request.user.is_seller():
        return redirect('/')
    products = request.user.products.all()
    return render(request, 'majaay/seller_dashboard.html', {'products': products})


@login_required
def product_create(request):
    if not request.user.is_seller():
        return redirect('login')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'majaay/product_form.html', {'form': form})


def category_list(request):
    from .models import Category
    categories = Category.objects.all().order_by('name')
    return render(request, 'majaay/category_list.html', {'categories': categories})

def product_list(request):
    from .models import Category
    categories = Category.objects.all().order_by('name')
    qs = Product.objects.filter(approved=True)
    selected_category = None
    category_slug = request.GET.get('category')
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()
        qs = qs.filter(category__slug=category_slug)
    return render(request, 'majaay/product_list.html', {
        'products': qs,
        'categories': categories,
        'selected_category': selected_category,
    })


def product_detail_and_order(request, pk):
    product = get_object_or_404(Product, pk=pk, approved=True)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            # notify manager/owner by email
            send_mail(
                'New order received',
                f'Order #{order.pk} for {product.title}\nBuyer: {order.buyer_name} {order.buyer_phone}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
            )
            return render(request, 'majaay/order_thanks.html', {'order': order})
    else:
        form = OrderForm()
    return render(request, 'majaay/product_detail.html', {'product': product, 'form': form})


# Manager views
@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def pending_sellers(request):
    sellers = SellerProfile.objects.filter(approved=False)
    return render(request, 'majaay/pending_sellers.html', {'sellers': sellers})


@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def approve_seller(request, pk):
    profile = get_object_or_404(SellerProfile, pk=pk)
    profile.approved = True
    profile.save()
    # optional: email seller
    send_mail(
        'Seller account approved',
        'Your seller account on Ma Diaay has been approved. You can now upload products and sell.',
        settings.DEFAULT_FROM_EMAIL,
        [profile.user.email],
    )
    return redirect('pending_sellers')


@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def pending_products(request):
    prods = Product.objects.filter(approved=False)
    return render(request, 'majaay/pending_products.html', {'products': prods})


@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def approve_product(request, pk):
    p = get_object_or_404(Product, pk=pk)
    p.approved = True
    p.save()
    return redirect('pending_products')

