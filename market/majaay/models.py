from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
import hashlib, base64


class User(AbstractUser):
    ROLE_OWNER = 'owner'
    ROLE_MANAGER = 'manager'
    ROLE_SELLER = 'seller'
    ROLE_BUYER = 'buyer'
    ROLE_CHOICES = [
        (ROLE_OWNER, 'Owner'),
        (ROLE_MANAGER, 'Manager'),
        (ROLE_SELLER, 'Seller'),
        (ROLE_BUYER, 'Buyer'),
    ]

    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default=ROLE_BUYER)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    def is_seller(self):
        return self.role == self.ROLE_SELLER

    def is_manager(self):
        return self.role == self.ROLE_MANAGER


class SellerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_profile')
    approved = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    # mark if we already generated the "product-based" password once
    product_password_generated = models.BooleanField(default=False)
    last_temp_password_sent_at = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=True)

    def __str__(self):
        return f"Seller: {self.user.get_full_name() or self.user.username}"


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # seller's price
    displayed_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='products/%Y/%m/%d/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)  # managers approve products

    def save(self, *args, **kwargs):
        # displayed price is seller price + 5%
        try:
            self.displayed_price = (Decimal(self.price) * Decimal('1.05')).quantize(Decimal('0.01'))
        except Exception:
            self.displayed_price = self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} — {self.seller.username}"


class Order(models.Model):
    # For simplicity: one product per order. You can expand to Order + OrderItem for carts.
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    buyer_name = models.CharField(max_length=255)
    buyer_phone = models.CharField(max_length=50)
    buyer_address = models.TextField()
    buyer_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)  # managers/processors mark True when handled

    def __str__(self):
        return f"Order #{self.pk} — {self.product.title} by {self.buyer_name}"


# ------------------------- helpers.py -------------------------

def generate_password_from_product(product: Product) -> str:
    """Generate a short deterministic password from product.created_at and price.
    WARNING: Deterministic passwords can be predictable; we recommend sending as a ONE-TIME password
    and asking users to change it immediately.
    """
    ts = product.created_at.strftime('%Y%m%d%H%M%S') if product.created_at else timezone.now().strftime('%Y%m%d%H%M%S')
    raw = f"{ts}_{int(Decimal(product.price) * 100)}"  # e.g. '20250810123045_4999'
    h = hashlib.sha256(raw.encode()).digest()
    pwd = base64.urlsafe_b64encode(h)[:12].decode()  # 12 chars
    return pwd


# ------------------------- signals.py -------------------------
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Product)
def product_post_save(sender, instance: Product, created, **kwargs):
    # When a seller uploads their FIRST product, generate a password from that product + email it.
    seller = instance.seller
    try:
        profile = seller.seller_profile
    except SellerProfile.DoesNotExist:
        profile = None

    if created and profile and (not profile.product_password_generated):
        # generate password
        new_pwd = generate_password_from_product(instance)
        seller.set_password(new_pwd)
        seller.save()
        profile.product_password_generated = True
        profile.last_temp_password_sent_at = timezone.now()
        profile.must_change_password = True
        profile.save()

        # Email seller the new password (remember: console backend for dev)
        subject = 'Ma Diaay — Your seller account password'
        message = f"Hello {seller.get_full_name() or seller.username},\n\n" \
                  f"A password has been generated for your seller account after your product upload.\n" \
                  f"Temporary password: {new_pwd}\n\n" \
                  "Please log in and change this password as soon as possible."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [seller.email])


# ------------------------- forms.py -------------------------
from django import forms
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class SellerRegistrationForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'first_name', 'address', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = UserModel.ROLE_SELLER if hasattr(UserModel, 'ROLE_SELLER') else 'seller'
        # generate a temporary random password for initial registration
        import secrets
        temp = secrets.token_urlsafe(8)
        user.set_password(temp)
        if commit:
            user.save()
            # create SellerProfile
            SellerProfile.objects.create(user=user)
            # send temp password by email
            send_mail(
                'Ma Diaay — Account created',
                f'Hello {user.get_full_name() or user.username},\nYour temporary password: {temp}\nYou will receive a product-based password on first product upload.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        return user


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'category', 'price', 'image']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['buyer_name', 'buyer_phone', 'buyer_address', 'buyer_email']