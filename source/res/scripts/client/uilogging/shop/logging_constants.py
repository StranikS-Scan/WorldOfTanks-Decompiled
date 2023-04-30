# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/shop/logging_constants.py
from enum import Enum
FEATURE = 'shop'

class ShopLogActions(Enum):
    CLOSED = 'closed'
    DISPLAYED = 'displayed'
    VEHICLE_BUY_VIEW_PURCHASE_BUTTON_CLICKED = 'vehicle_buy_view_purchase_button_clicked'
    VEHICLE_PACK_PURCHASE_CONFIRMATION_ACCEPTED = 'vehicle_pack_purchase_confirmation_accepted'


class ShopLogKeys(Enum):
    SHOP = 'shop'
    SHOP_VIEW = 'shop_view'
    SHOP_OVERLAY = 'shop_overlay'
    STYLE_PREVIEW = 'style_preview'
    VEHICLE_BUY_VIEW = 'vehicle_buy_view'
    VEHICLE_PREVIEW = 'vehicle_preview'
    VEHICLE_PACK_PREVIEW = 'vehicle_pack_preview'
    VEHICLE_PACK_PURCHASE_CONFIRMATION = 'vehicle_pack_purchase_confirmation'


class ShopLogButtons(Enum):
    TO_PREVIEW_BUTTON = 'to_preview_button'


class ShopLogItemStates(Enum):
    CLIENT_PRODUCT = 'client_product'
    PLATFORM_PRODUCT = 'platform_product'
    WITHOUT_CREW = 'without_crew'
    WITH_SLOT = 'with_slot'
    WITH_AMMO = 'with_ammo'


class ShopCloseItemStates(Enum):
    CLOSE_BUTTON = 'close_button'
    BACK_BUTTON = 'back_button'
