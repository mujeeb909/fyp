from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder

from .models import *
import json
# Register your models here.
class ReviewAdmin(admin.ModelAdmin):
    change_form_template  = 'admin/review/change_form.html'

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     response = super(ReviewAdmin, self).change_view(
    #         request, object_id, form_url, extra_context=extra_context,
    #     )
    #     rev = review.objects.get(pk=object_id)
    #     response.extra_context['review'] = rev
    #
    #     return response

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['review'] = review.objects.get(pk=object_id)
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


admin.site.register(review, ReviewAdmin)