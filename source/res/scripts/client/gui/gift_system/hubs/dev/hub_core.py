# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/dev/hub_core.py
import logging
import typing
from gui.gift_system.hubs.base.hub_core import GiftEventBaseHub
from gui.gift_system.hubs.dev import IDevMessagesPusher
from gui.gift_system.hubs.dev.stamper import GiftEventDevStamper
from gui.gift_system.hubs.dev.gifter import GiftEventDevGifter
from gui.gift_system.hubs.dev.messenger import GiftEventDevMessenger
from gui.gift_system.hubs.dev.relations_keeper import GiftEventDevKeeper
if typing.TYPE_CHECKING:
    from gui.gift_system.hubs.base.stamper import IGiftEventStamper
    from gui.gift_system.hubs.base.gifter import IGiftEventGifter
    from gui.gift_system.hubs.base.messenger import IGiftEventMessenger
    from gui.gift_system.hubs.base.relations_keeper import IGiftEventKeeper
    from gui.gift_system.wrappers import SendGiftResponse
    from helpers.server_settings import GiftEventConfig
_logger = logging.getLogger(__name__)

class GiftEventDevHub(GiftEventBaseHub, IDevMessagesPusher):
    __slots__ = ()

    def __init__(self, eventSettings, isMessagesAllowed):
        super(GiftEventDevHub, self).__init__(eventSettings, isMessagesAllowed)
        _logger.info('%s is created with settings %s', self, self._settings)
        self._pushClientMessage('{}\nis created'.format(self))

    def __repr__(self):
        return 'GiftEventDevHub id={}, state={}'.format(self._settings.eventID, self._settings.giftEventState)

    def destroy(self):
        _logger.info('%s is destroyed', self)
        self._pushClientMessage('{}\nis destroyed'.format(self))
        super(GiftEventDevHub, self).destroy()

    def _createGifter(self, eventSettings):
        return GiftEventDevGifter(eventSettings, self._onGifterResponse)

    def _createKeeper(self, eventSettings):
        return GiftEventDevKeeper(eventSettings, self._onKeeperCleared)

    def _createMessenger(self, eventSetting, isMessagesAllowed):
        return GiftEventDevMessenger(eventSetting, isMessagesAllowed)

    def _createStamper(self, eventSettings):
        return GiftEventDevStamper(eventSettings, self._onStamperUpdate)

    def _onGifterResponse(self, responseData):
        _logger.info('%s received gifter response %s', self, responseData)
        self._pushClientMessage('{}\nreceived gifter response'.format(self))
        super(GiftEventDevHub, self)._onGifterResponse(responseData)

    def _onKeeperCleared(self):
        _logger.info('%s received keeper clearing', self)
        self._pushClientMessage('{}\nreceived keeper clearing'.format(self))
        super(GiftEventDevHub, self)._onKeeperCleared()

    def _onStamperUpdate(self):
        _logger.info('%s received stamper update', self)
        self._pushClientMessage('{}\nreceived stamper update'.format(self))
        super(GiftEventDevHub, self)._onStamperUpdate()

    def _updateSettings(self, eventSettings):
        _logger.info('%s received new settings %s', self, eventSettings)
        self._pushClientMessage('{}\nreceived new server settings'.format(self))
        super(GiftEventDevHub, self)._updateSettings(eventSettings)
