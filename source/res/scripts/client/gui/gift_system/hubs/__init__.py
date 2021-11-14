# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/__init__.py
import typing
from gifts.gifts_common import GiftEventID
from gui.gift_system.hubs.base.hub_core import GiftEventBaseHub
from gui.gift_system.hubs.dev.hub_core import GiftEventDevHub
if typing.TYPE_CHECKING:
    from gui.gift_system.hubs.base.hub_core import IGiftEventHub
    from helpers.server_settings import GiftEventConfig
_HUB_BY_EVENT_ID = {GiftEventID.DEV_TEST: GiftEventDevHub}

def createGiftEventHub(eventID, eventSettings, isMessagesAllowed):
    return _HUB_BY_EVENT_ID.get(eventID, GiftEventBaseHub)(eventSettings, isMessagesAllowed)
