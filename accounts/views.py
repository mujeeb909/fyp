from django.conf import settings
from django.shortcuts import render ,redirect
from .forms import *
from django.contrib.auth.models import User , auth
from django.contrib import messages
from django.http import JsonResponse
from order.models import Order, Address,OrderItem
from review.models import review
from stock.models import stock


def validate_username(request):
    username = request.GET.get('username', None)
    print(username)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'A user with this username already exists.'
    return JsonResponse(data)


def get_expire_at_browser_close(self):
    """
    Returns ``True`` if the session is set to expire when the browser
    closes, and ``False`` if there's an expiry date. Use
    ``get_expiry_date()`` or ``get_expiry_age()`` to find the actual expiry
    date/age, if there is one.
    """
    if self.get('_session_expiry') is None:
        return settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
    return self.get('_session_expiry') == 0


def login(request):
    request.session.get_expire_at_browser_close()
    if request.session.has_key('is_logged'):
        return redirect('/')
    if request.method == 'GET':
        form = loginForm()
    else:
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                request.session['is_logged'] = True
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('/')
            else:
                messages.info(request, 'Invalid Credentials')
                return redirect('/login')
    context = {
        'form': form
    }
    return render(request, 'login.html',context)


def logout(request):
    request.session.set_expiry(10)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order_item = OrderItem.objects.filter(
            user=request.user,
            ordered=False
        )
        for i in order_item:
            i.delete()
        order_qs.delete()
    auth.logout(request)
    return redirect('/')


def signup(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        f_profile = userprofileform(request.POST)
        if form.is_valid() and f_profile.is_valid():
            user = form.save()
            profile = f_profile.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Account created successfully')
            return redirect('/login')

    else:
        form = CustomUserForm()
        f_profile = userprofileform()

    context = {
        'form': form,
        'f_form':  f_profile
    }
    return render(request, 'signup.html',context)

def profile(request, id):
    user1 = User.objects.get(pk = id)
    user2 = UserDetail.objects.get(user__id = id)
    order = Order.objects.filter(user=request.user, ordered=True)[0:10]
    address = Address.objects.filter(user=request.user)
    try:
        review_exist = review.objects.filter(user=request.user)[0]
    except IndexError:
        review_exist = 'null'

    if request.method == 'POST':
        form = CustomUserupdateForm(request.POST, instance=user1)
        f_profile = userprofileform(request.POST, instance=user2)
        if form.is_valid() and f_profile.is_valid():
            user = form.save()
            profile = f_profile.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Account updated successfully')
            return redirect('/profile/%d/'%id)
    else:
        form = CustomUserupdateForm(instance = user1)
        f_profile = userprofileform(instance = user2)
    context = {
        'form': form,
        'f_form': f_profile,
        'order': order,
        'i': address,
        'review_exist': review_exist
    }
    return render(request,'profile.html', context)

