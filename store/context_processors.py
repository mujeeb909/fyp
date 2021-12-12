from .models import *

def get_category(request):
    cat = category.objects.all()
    sub = Sub_category.objects.all()
    return {
        'cat': cat,
        'sub': sub
    }
