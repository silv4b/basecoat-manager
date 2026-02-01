from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm

@login_required
def product_list(request):
    products = Product.objects.filter(user=request.user)

    # Search
    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q) | products.filter(description__icontains=q)

    # Status Filter
    status = request.GET.get('status')
    if status == 'public':
        products = products.filter(is_public=True)
    elif status == 'private':
        products = products.filter(is_public=False)

    # Price Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Stock Filter
    min_stock = request.GET.get('min_stock')
    max_stock = request.GET.get('max_stock')
    if min_stock:
        products = products.filter(stock__gte=min_stock)
    if max_stock:
        products = products.filter(stock__lte=max_stock)

    products = products.order_by('-created_at')

    return render(request, 'products/product_list.html', {
        'products': products,
        'q': q,
        'status': status,
        'min_price': min_price,
        'max_price': max_price,
        'min_stock': min_stock,
        'max_stock': max_stock,
    })

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return redirect('product_list')

def public_product_list(request):
    products = Product.objects.filter(is_public=True)

    # Search
    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q) | products.filter(description__icontains=q)

    # Price Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Stock Filter
    min_stock = request.GET.get('min_stock')
    max_stock = request.GET.get('max_stock')
    if min_stock:
        products = products.filter(stock__gte=min_stock)
    if max_stock:
        products = products.filter(stock__lte=max_stock)

    products = products.order_by('-created_at')

    return render(request, 'products/product_list.html', {
        'products': products,
        'title': 'Public Catalog',
        'is_public_view': True,
        'q': q,
        'min_price': min_price,
        'max_price': max_price,
        'min_stock': min_stock,
        'max_stock': max_stock,
    })
