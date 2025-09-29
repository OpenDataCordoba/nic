from django.contrib import admin
from core.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'object_created', 'description']

    def changelist_view(self, request, extra_context=None):
        page_size = request.GET.get('page_size')
        if page_size and page_size.isdigit():
            self.list_per_page = int(page_size)
        else:
            self.list_per_page = 20
        return super().changelist_view(request, extra_context)
