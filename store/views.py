import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
from django.conf import settings
from django.urls import reverse

# Create your views here.

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Product, Cart

def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    in_cart = False
    cart_id = None
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user, product=product).first()
        if cart_item:
            in_cart = True
            cart_id = cart_item.id
    context = {
        'product': product,
        'related_products': related_products,
        'in_cart': in_cart,
        'cart_id': cart_id,
    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


# def category_products(request, slug):
#     category = get_object_or_404(Category, slug=slug)
#     products = Product.objects.filter(is_active=True, category=category)
#     categories = Category.objects.filter(is_active=True)
#     context = {
#         'category': category,
#         'products': products,
#         'categories': categories,
#     }
#     return render(request, 'store/category_products.html', context)

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    
    # Paginate the products
    page = request.GET.get('page')
    paginator = Paginator(products, 3)  # You can change the number of products per page (e.g., 12)
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    categories = Category.objects.filter(is_active=True)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/category_products.html', context)

# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('store:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
 
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
       
        'total_amount': amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    user = request.user
    addresses = Address.objects.filter(user=user)

    if not addresses.exists():
        return redirect('store:profile')

    if request.method == "POST":
        address_id = request.POST.get('address')
        address = get_object_or_404(Address, id=address_id, user=user)

        # Get user cart
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return redirect('store:cart')

        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        paystack_secret = settings.PAYSTACK_SECRET_KEY
        callback_url = request.build_absolute_uri(reverse('store:payment_success'))
        email = user.email
        amount_kobo = int(total_amount * 100)

        headers = {
            "Authorization": f"Bearer {paystack_secret}",
            "Content-Type": "application/json",
        }
        data = {
            "email": email,
            "amount": amount_kobo,
            "callback_url": callback_url,
            "metadata": {
                "user_id": user.id,
                "address_id": address.id
            }
        }

        response = requests.post('https://api.paystack.co/transaction/initialize', json=data, headers=headers)
        res_data = response.json()

        if res_data.get('status'):
            return redirect(res_data['data']['authorization_url'])
        else:
            return render(request, 'store/payment_error.html', {'error': res_data.get('message', 'Payment initialization failed.')})
    
    # GET: Show the checkout page with addresses
    return render(request, 'store/checkout.html', {'addresses': addresses})


# in store/views.py
from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@login_required
def payment_success(request):
    """
    This view is called by Paystack after successful payment.
    It should verify the transaction and then create orders for the user.
    """
    reference = request.GET.get('reference')
    if not reference:
        return redirect('store:checkout')

    # Verify payment with Paystack
    verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(verify_url, headers=headers)
    data = response.json()

    if data.get('status') and data['data']['status'] == 'success':
        user = request.user
        metadata = data['data'].get('metadata', {})
        address_id = metadata.get('address_id')

        address = Address.objects.filter(id=address_id, user=user).first()
        if not address:
            return redirect('accounts:profile')

        cart_items = Cart.objects.filter(user=user)
        for item in cart_items:
            Order.objects.create(
                user=user,
                address=address,
                product=item.product,
                quantity=item.quantity,
            )
            item.delete()

        return render(request, 'store/payment_success.html', {'data': data})
    else:
        return render(request, 'store/payment_error.html', {'error': 'Payment verification failed'})

@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})





def shop(request):
    return render(request, 'store/shop.html')





def test(request):
    return render(request, 'store/test.html')
