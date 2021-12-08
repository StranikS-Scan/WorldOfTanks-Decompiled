# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/new_year/stamper.py
import logging
from gui.gift_system.constants import NY_STAMP_CODE
from gui.gift_system.hubs.base.stamper import GiftEventBaseStamper
_logger = logging.getLogger(__name__)

class GiftEventNYStamper(GiftEventBaseStamper):
    __slots__ = ()
    _STAMPS = {NY_STAMP_CODE}
