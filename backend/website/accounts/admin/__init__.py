# Make sure that Django can discover the panel
# components
from accounts.admin.accounts import AccountAdmin  # noqa: 401
from accounts.admin.transactions import AdminTransactionAdmin  # noqa: 401

__all__ = [
    AccountAdmin,
    AdminTransactionAdmin,
]
