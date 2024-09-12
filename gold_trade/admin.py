from django.contrib import admin
from .models import UserProfile, Transaction


# Admin class for UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance']
    search_fields = ('user__username',)  # Allow searching by username


# Admin class for Transaction
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'gold_amount', 'price_per_gram', 'timestamp']
    list_filter = ('transaction_type',)  # Allow filtering by transaction type
    search_fields = ('user__username',)  # Allow searching by username
    ordering = ('-timestamp',)  # Order transactions by most recent first


# Register the models with the admin site
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transaction, TransactionAdmin)
