# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/gift_system/hubs/stamper.py
from gui.gift_system.hubs.base.stamper import GiftEventBaseStamper
from mt_birthday.birthday_constants import BIRTHDAY_STAMP_CODE, BIRTHDAY_STAMP_CODE_SPECIAL

class GiftEventBirthdayStamper(GiftEventBaseStamper):
    __slots__ = ()
    _STAMPS = {BIRTHDAY_STAMP_CODE, BIRTHDAY_STAMP_CODE_SPECIAL}
