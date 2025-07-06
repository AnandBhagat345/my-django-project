from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
from django.shortcuts import get_object_or_404


# Create your views here.
def index(request):
    # products = Product.objects.all()
    # n = len(products)
    # nslides = ceil(n / 4)
    # params = {'no_of_slides': nslides, 'range': range(nslides), 'products': products}
    # allProds=[[products, range(1, nslides) , nslides],
    #           [products, range(1, nslides) , nslides]]

    allProds = []
    catprods = Product.objects.values('category', 'id')  # Get categories
    cats = {item['category'] for item in catprods}       # Unique categories
    
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = ceil(n / 4)
        allProds.append([prod, range(1, nslides), nslides]) 
    params ={'allProds':allProds}
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request,'shop/about.html')

def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        print(name,email,phone,desc)
        contact = Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()
        thank = True

    return render(request,'shop/contact.html', {'thank':thank})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '').strip()
        email = request.POST.get('email', '').strip()

        if not orderId or not email:
            return JsonResponse({'error': 'Both Order ID and Email are required.'})
        try:
            orders = Orders.objects.get(order_id=orderId, email=email)
        except Orders.DoesNotExist:
            return JsonResponse({'error': 'No order found with the provided details.'})
            
        
        updates = OrderUpdate.objects.filter(order_id=orderId).order_by('timestamp')
        update_data = [{'text': u.update_desc, 'time': str(u.timestamp)} for u in updates]
            
            
        try:
            items = json.loads(orders.item_json)
        except json.JSONDecodeError:
            item = {}
                
        return JsonResponse({
            'updates': update_data,
            'items': items  # product id => {name, qty, price}
        } , safe = True)
    
    
    return render(request, 'shop/tracker.html')

def search(request):
    return render(request,'shop/search.html')

def productview(request,myid):
    product = get_object_or_404(Product,id=myid)
    half_price = product.price/2
   
    return render(request,'shop/prodview.html',{'product':product, 'half_price': half_price})

def checkout(request):
        if request.method == "POST":
            item_json = request.POST.get('itemjson', '')
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            city = request.POST.get('city', '')
            address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
            state = request.POST.get('state', '')
            zip_code = request.POST.get('zip_code', '')
            phone = request.POST.get("phone",'')
           
           # print(name,email,city,address,state,zip_code,phone)
            order = Orders(item_json=item_json,name=name,email=email,city=city,address=address,state=state,zip_code=zip_code,phone=phone)
            order.save()
            update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
            update.save()
            thank = True
            id = order.order_id
            return render(request,'shop/checkout.html', {'thank':thank, 'id':id})
        return render(request,'shop/checkout.html')

def cart(request):
    return render(request,'shop/cart.html')

def order_history(request):
    return render(request,'shop/order_history.html')

def profile(request):
    return render(request,'shop/profile.html')
