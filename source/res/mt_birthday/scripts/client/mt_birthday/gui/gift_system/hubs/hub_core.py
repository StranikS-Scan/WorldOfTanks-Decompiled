# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/gift_system/hubs/hub_core.py
import typing
from gui.gift_system.hubs.base.hub_core import GiftEventBaseHub
from mt_birthday.gui.gift_system.hubs.stamper import GiftEventBirthdayStamper
from mt_birthday.gui.gift_system.hubs.relations_keeper import GiftEventBirthdayKeeper
from mt_birthday.gui.gift_system.hubs.birthday_messenger import GiftEventBirthdayMessenger
if typing.TYPE_CHECKING:
    from gui.gift_system.hubs.base.stamper import IGiftEventStamper
    from gui.gift_system.hubs.base.messenger import IGiftEventMessenger
    from mt_birthday.gui.gift_system.hubs.relations_keeper import IGiftEventBirthdayKeeper
    from helpers.server_settings import GiftEventConfig

class GiftEventBirthdayHub(GiftEventBaseHub):
    __slots__ = ()

    def getKeeper(self):
        return self._keeper

    def _createKeeper(self, eventSettings):
        return GiftEventBirthdayKeeper(eventSettings, self._onKeeperCleared)

    def _createStamper(self, eventSettings):
        return GiftEventBirthdayStamper(eventSettings, self._onStamperUpdate)

    def _createMessenger(self, eventSettings, isMessagesAllowed):
        return GiftEventBirthdayMessenger(eventSettings, isMessagesAllowed)
