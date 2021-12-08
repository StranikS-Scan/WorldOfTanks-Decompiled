# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/new_year/hub_core.py
import typing
from gui.gift_system.hubs.base.hub_core import GiftEventBaseHub
from gui.gift_system.hubs.new_year.ny_messenger import GiftEventNYMessenger
from gui.gift_system.hubs.new_year.relations_keeper import GiftEventNYKeeper
from gui.gift_system.hubs.new_year.stamper import GiftEventNYStamper
if typing.TYPE_CHECKING:
    from gui.gift_system.hubs.base.messenger import IGiftEventMessenger
    from gui.gift_system.hubs.base.stamper import IGiftEventStamper
    from gui.gift_system.hubs.new_year.relations_keeper import IGiftEventNYKeeper
    from helpers.server_settings import GiftEventConfig

class GiftEventNYHub(GiftEventBaseHub):
    __slots__ = ()

    def getKeeper(self):
        return self._keeper

    def _createKeeper(self, eventSettings):
        return GiftEventNYKeeper(eventSettings, self._onKeeperCleared)

    def _createMessenger(self, eventSettings, isMessagesAllowed):
        return GiftEventNYMessenger(eventSettings, isMessagesAllowed)

    def _createStamper(self, eventSettings):
        return GiftEventNYStamper(eventSettings, self._onStamperUpdate)
