from django.db.models import Count
from django.shortcuts import render, redirect
from .models import *
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.views.generic import ListView,  View
from django.http import Http404, HttpResponse, JsonResponse
from stock.models import stock
from review.models import review
from .models import *
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from .forms import ContactForm
# Create your views here.
from django.db import connection

def index(request):
    
    items = products.objects.filter(featured=True)[0:8]
    
    data = products.objects.filter(itemreview__rating=5,itemreview__review_predict='positive').distinct()
    ban = Banner.objects.all()
    print(ban)
    context = {
        'items':items,
        'banner':ban,
        'data':data
    }
    return render(request, 'index.html', context)
    # return redirect('login')



def category_detail(request, id):
    cat = category.objects.get(pk=id)
    categories = category.objects.all()
    product = products.objects.filter(Category=id)
    page = request.GET.get('page', 1)
    paginator = Paginator(product, 6)
    try:
        pro = paginator.page(page)
    except PageNotAnInteger:
        pro = paginator.page(1)
    except EmptyPage:
        pro = paginator.page(paginator.num_pages)

    context = {
        'cats': cat,
        'categories':categories,
        'pro': pro
    }
    return render(request,'category.html', context)



def subcategory_detail(request, id):
    subcat = Sub_category.objects.get(pk=id)
    categories = category.objects.all()
    product = products.objects.filter(sub_category=id)
    page = request.GET.get('page', 1)
    paginator = Paginator(product, 6)
    try:
        pro = paginator.page(page)
    except PageNotAnInteger:
        pro = paginator.page(1)
    except EmptyPage:
        pro = paginator.page(paginator.num_pages)

    context = {
        'subcats': subcat,
        'categories':categories,
        'pro': pro
    }
    return render(request,'category.html', context)

def store(request):
    product = products.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(product, 6)
    try:
        pro = paginator.page(page)
    except PageNotAnInteger:
        pro = paginator.page(1)
    except EmptyPage:
        pro = paginator.page(paginator.num_pages)

    context = {
        'products': pro
    }
    return render(request , 'store.html', context)



class SearchProductView(ListView):
  template_name = "search.html"
  paginate_by = 8
  def get_context_data(self, *args, **kwargs):
    context = super(SearchProductView, self).get_context_data(*args, **kwargs)
    context['query'] = self.request.GET.get('q')
    return context

  def get_queryset(self, *args, **kwargs):
    request = self.request
    query = request.GET.get('q', None)
    if query is not None:
      return products.objects.search(query)
    return products.objects.featured()


def contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['Name']
            subject = f'Message from {form.cleaned_data["Name"]}'
            email = form.cleaned_data['Email']
            message = form.cleaned_data['Message']
            subject, from_email, to = subject, email, 'mohammad.mujeeb.051@gmail.com'
            print(subject)

            html_content = '<p>Name: </p>'+ name+ '<p>Email: </p>' + from_email  + '<p>Message: </p>'+ message
            try:
                send_mail(subject, message,  settings.EMAIL_HOST_USER, ['mohammad.mujeeb.051@gmail.com'], fail_silently=True ,html_message=html_content )
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('contact')
    context = {
        'form': form
    }
    return render(request, 'contact.html',context )

import json
def get_places(request):
  if request.is_ajax():
    q = request.GET.get('term', '')
    places = products.objects.search(q)
    results = []
    for pl in places:
      place_json = {}
      place_json = pl.title
      results.append(place_json)
    data = json.dumps(results)
  else:
    data = 'fail'
  mimetype = 'application/json'
  return HttpResponse(data, mimetype)

def detail(request, id):
    item = products.objects.get(pk = id)
    item_images = Image.objects.filter(product=id)
    stock_info = stock.objects.filter(product=id)
    rev = review.objects.filter(item__id=id)
    data = products.objects.filter(itemreview__rating=5, itemreview__review_predict='positive').distinct()
    rev_length = rev.count()
    page = request.GET.get('page', 1)
    paginator = Paginator(rev, 4)
    try:
        pro = paginator.page(page)
    except PageNotAnInteger:
        pro = paginator.page(1)
    except EmptyPage:
        pro = paginator.page(paginator.num_pages)

    context = {
        'item': item,
        'images':item_images,
        'st': stock_info,
        'rev': pro,
        'revlength':rev_length,
        'data': data
    }
    return render(request, 'product_detail.html', context)



def reload(request, id):
    size = request.GET.get('e_value')
    color = request.GET.get('c_value')
    final = 'test'
    st = None
    if color != "None" and size != "None":
        st = stock.objects.get(product=id, product_Size__title=size, product_Color__title=color)
    elif size != "None":
        st = stock.objects.get(product=id, product_Size__title=size)
    elif color != "None":
        st = stock.objects.get(product=id,  product_Color__title=color)
    else:
        st = stock.objects.get(product=id)

    data = {
       'final': st.quantity,
    }
    return JsonResponse(data)

def size_ajax(request, id):
    size = request.GET.get('e_value')
    color = request.GET.get('c_value')

    sizefinal = None
    st = None
    if color != "None" and size != "None":
        st = stock.objects.get(product=id, product_Size__title=size, product_Color__title=color)
    elif size != "None":
        st = stock.objects.get(product=id, product_Size__title=size)
    elif color != "None":
        st = stock.objects.get(product=id, product_Color__title=color)
    else:
        st = stock.objects.get(product=id)
    data = {
       'sizefinal': st.quantity
    }
    print(size)
    return JsonResponse(data)

def color_ajax(request, id):
    size = request.GET.get('e_value')
    color = request.GET.get('c_value')
    colorfinal = None
    st = None
    if color != "None" and size != "None":
        st = stock.objects.get(product=id, product_Size__title=size, product_Color__title=color)
    elif size != "None":
        st = stock.objects.get(product=id, product_Size__title=size)
    elif color != "None":
        st = stock.objects.get(product=id, product_Color__title=color)
    else:
        st = stock.objects.get(product=id)

    data = {
       'colorfinal': st.quantity
    }
    print(size)
    return JsonResponse(data)