from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from core.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'object_created', 'description']

    def get_changelist_instance(self, request):
        page_size = request.GET.get('page-size', 20)
        if page_size:
            self.list_per_page = int(page_size)
        return super().get_changelist_instance(request)


# Unregister the default User admin
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ('last_login', 'date_joined')
