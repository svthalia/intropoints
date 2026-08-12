# ruff: noqa: I001
# Make sure that Django can discover the panel
# components
from stores.admin.stores import StoreAdminPanel
from stores.admin.items import ItemAdminPanel
from stores.admin.purchases import PurchaseAdminPanel
from stores.admin.receipts import UsedItemReceiptAdminPanel

# --------------------- #
# Module initialization #
# --------------------- #

__all__ = [StoreAdminPanel, ItemAdminPanel, PurchaseAdminPanel, UsedItemReceiptAdminPanel]
