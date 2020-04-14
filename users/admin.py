from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    exclude = ('username',)
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'email',
                'password',
                'user_type',
                'first_name',
                'last_name',
                'phone_number',
                'business_name',
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
    )

    list_display = [
        'email',
        'is_staff',
        'user_type',
    ]
    search_fields = ["name"]
