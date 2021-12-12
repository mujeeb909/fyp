from django.core.mail import send_mail
from django.http import BadHeaderError, HttpResponse
from django.shortcuts import render , redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.views.generic import ListView,  View
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from store.models import products, Color , Size
from stock.models import stock
# Create your views here.
from .forms import *
import random
import string
import pickle
import stripe

from .models import *


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


class OrderSummaryView(LoginRequiredMixin, View):
    login_url = "/login/"
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'ordersummary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order!")
            return redirect("/")


def update_cart(request, id):
    order_item = OrderItem.objects.get(pk=id , user= request.user ,ordered=False)
    order_item.quantity += 1
    order_item.save()
    messages.info(request, "This item quantity was updated.")
    return redirect('ordersummary')


@login_required(login_url='/login')
def add_to_cart(request, id):
    color =None
    size=None
    qty = None
    if 'color' in request.POST:
        color = request.POST['color']
    else:
        color = False

    if 'size' in request.POST:
        size = request.POST['size']
    else:
        size = False

    item = products.objects.get(id=id)
    color_qs = item.product_color.filter(title=color).first()
    size_qs = item.product_size.filter(title=size).first()

    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False, color= color_qs , size=size_qs)
    request.session['order_item'] = id

    # print(order_item)==admin
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    #print(order_qs) ==return queryset[]
    # if there is a order
    if order_qs.exists():
        order = order_qs[0]
        # if order.items.filter(item__id= item.id ,color__id= color_qs.id, size__id=size_qs.id).exists():
        if order.items.filter(id=order_item.id).exists():
            print(order.items.filter(item__id=order_item.id))
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect('ordersummary')
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect('ordersummary')

    # if there is no order..first time order and first item
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
    return redirect('ordersummary')


@login_required(login_url='/login')
def remove_single_item_from_cart(request, id):
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        order_item = OrderItem.objects.filter(
            pk=id,
            user=request.user,
            ordered=False
        )[0]
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "The item quantity was updated")
        return redirect('ordersummary')
    else:
        messages.info(request, "This item was not in your cart")
        return redirect('ordersummary')


@login_required(login_url='/login')
def remove_from_cart(request, id):
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(
            pk=id,
            user=request.user,
            ordered=False
        )[0]
        order_item.delete()
        messages.warning(request, "Item deleted successfully")
        return redirect("ordersummary")
    else:
        messages.info(request, "You do not have an active order")
        return redirect('ordersummary')



def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            total = order.get_total()

            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
                'total':total
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("checkout")


    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    shipping_address = None
                    if is_valid_form([shipping_address1, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'C':
                    return redirect('paymentcod', payment_option='CashOnDelivery')
                elif payment_option == 'S':
                  return redirect('payment', payment_option='stripe')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("ordersummary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        order_qs = Order.objects.filter(
            user=self.request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            order_item = OrderItem.objects.filter(
                user=self.request.user,
                ordered=False
            )
            for i in order_item:
                if i.color and i.size:
                    st = stock.objects.get(product=i.item.id, product_Color=i.color, product_Size=i.size)
                elif i.color:
                    st = stock.objects.get(product=i.item.id, product_Color=i.color)
                elif i.size:
                    st = stock.objects.get(product=i.item.id, product_Size=i.size)
                else:
                    st = stock.objects.get(product=i.item.id)
                st.quantity -= i.quantity
                st.save()
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total())
            try:
                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()
                html_content = "Your order has been placed successfully. Your order reference code is " + str(order.ref_code)
                email_user = self.request.user.email
                try:
                    send_mail("Order Confirmation", "Thanks for using our Services", settings.EMAIL_HOST_USER, [email_user],
                              fail_silently=True, html_message=html_content)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')

                self.request.session['order_id'] = order.id
                messages.success(self.request, "Your order was successful!")
                return redirect("order_complete")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/payment/stripe/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/payment/stripe/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/payment/stripe/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/payment/stripe/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/payment/stripe/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/payment/stripe/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/payment/stripe/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")



class PaymentViewCod(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)

        if order.billing_address:
            context = {
                'order': order,
            }
            return render(self.request, "paymentcod.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        order_qs = Order.objects.filter(
            user=self.request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            order_item = OrderItem.objects.filter(
                user=self.request.user,
                ordered=False
            )
            for i in order_item:
                if i.color and i.size:
                    st = stock.objects.get(product=i.item.id, product_Color=i.color, product_Size=i.size)
                elif i.color:
                    st = stock.objects.get(product=i.item.id, product_Color=i.color)
                elif i.size:
                    st = stock.objects.get(product=i.item.id, product_Size=i.size)
                else:
                    st = stock.objects.get(product=i.item.id)
                st.quantity -= i.quantity
                st.save()

        form = PaymentCodForm(self.request.POST)
        if form.is_valid():
            default = form.cleaned_data.get('default')
            if default:
                payment = PaymentCod()
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                order.ordered = True
                order.paymentCod = payment
                order.ref_code = create_ref_code()
                order.save()
                html_content = "Your order has been placed successfully. Your order reference code is " + str(
                    order.ref_code)
                email_user = self.request.user.email
                try:
                    send_mail("Order Confirmation", "Thanks for using our Services", settings.EMAIL_HOST_USER,
                              [email_user],
                              fail_silently=True, html_message=html_content)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                self.request.session['order_id'] = order.id
                return redirect("order_complete")
            else:
                messages.warning(self.request, "Select the order checkbox first")


def order_complete(request):
    order_id = request.session['order_id']
    order = Order.objects.get(id=order_id, user=request.user, ordered=True)
    context = {
        'order': order
    }
    return render(request, 'order_complete.html', context)

def cancel_order(request, id):
    order_id = request.session['order_id']
    order = Order.objects.get(id=id, user=request.user, ordered=True)
    order_item = order.items.all()
    for i in order_item:
        if i.color and i.size:
            st = stock.objects.get(product=i.item.id, product_Color=i.color, product_Size=i.size)
        elif i.color:
            st = stock.objects.get(product=i.item.id, product_Color=i.color)
        elif i.size:
            st = stock.objects.get(product=i.item.id, product_Size=i.size)
        else:
            st = stock.objects.get(product=i.item.id)
        st.quantity += i.quantity
        st.save()
    order.delete()
    messages.warning(request, "order cancel successfully")
    return redirect('/')