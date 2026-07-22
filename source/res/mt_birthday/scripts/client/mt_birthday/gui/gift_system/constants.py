# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/gift_system/constants.py
from gifts import gifts_common
from constants_utils import ConstInjector

class GiftEventID(gifts_common.GiftEventID, ConstInjector):
    BIRTHDAY_2025 = 4
    BIRTHDAY_2026 = 5
    gifts_common.GiftEventID.ALL += (BIRTHDAY_2025, BIRTHDAY_2026)
