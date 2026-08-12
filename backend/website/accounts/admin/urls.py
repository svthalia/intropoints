from django.contrib import admin
from django.urls import path

from accounts.admin.views import ReverseTransactionView

urlpatterns = [
    path(
        "<path:object_id>/revert/<int:transaction_id>/",
        admin.site.admin_view(ReverseTransactionView.as_view()),
        name="revert-transaction",
    ),
]
