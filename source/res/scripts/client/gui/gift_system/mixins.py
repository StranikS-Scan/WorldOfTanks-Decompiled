# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/mixins.py
import typing
from gifts.gifts_common import GiftEventID, GiftEventState
from gui.gift_system.constants import HubUpdateReason
from gui.gift_system.hubs.base.hub_core import IGiftEventHub
from gui.gift_system.wrappers import filterGiftHubsAction
from helpers import dependency
from skeletons.gui.game_control import IGiftSystemController

class GiftEventHubWatcher(object):
    _GIFT_EVENT_ID = GiftEventID.UNKNOWN
    __giftsController = dependency.descriptor(IGiftSystemController)

    def __init__(self, *args, **kwargs):
        super(GiftEventHubWatcher, self).__init__(*args, **kwargs)
        self._eventHub = None
        return

    def isGiftEventDisabled(self, isCached=True):
        eventHub = self.getGiftEventHub(isCached)
        return eventHub is None or eventHub.getSettings().isDisabled

    def isGiftEventEnabled(self, isCached=True):
        eventHub = self.getGiftEventHub(isCached)
        return eventHub and eventHub.getSettings().isEnabled

    def isGiftEventSuspended(self, isCached=True):
        eventHub = self.getGiftEventHub(isCached)
        return eventHub and eventHub.getSettings().isSuspended

    def getGiftEventState(self, isCached=True):
        eventHub = self.getGiftEventHub(isCached)
        return eventHub.getSettings().giftEventState if eventHub else GiftEventState.DISABLED

    def getGiftEventHub(self, isCached=True):
        return self._eventHub if isCached else self.__giftsController.getEventHub(self._GIFT_EVENT_ID)

    def catchGiftEventHub(self, autoSub=True):
        self._eventHub = self.__giftsController.getEventHub(self._GIFT_EVENT_ID)
        if autoSub:
            self.__subToGiftEventHub()

    def releaseGiftEventHub(self, autoUnsub=True):
        if autoUnsub:
            self.__unsubFromGiftEventHub()
        self._eventHub = None
        return

    def _onGiftHubUpdate(self, reason, extra=None):
        pass

    @filterGiftHubsAction(_GIFT_EVENT_ID)
    def __onHubsCreation(self, *_):
        self._eventHub = self.__giftsController.getEventHub(self._GIFT_EVENT_ID)
        self._eventHub.onHubUpdated += self._onGiftHubUpdate
        self._onGiftHubUpdate(HubUpdateReason.SETTINGS)

    @filterGiftHubsAction(_GIFT_EVENT_ID)
    def __onHubsDestruction(self, *_):
        self._eventHub.onHubUpdated -= self._onGiftHubUpdate
        self._eventHub = None
        self._onGiftHubUpdate(HubUpdateReason.SETTINGS)
        return

    def __subToGiftEventHub(self):
        self.__giftsController.onEventHubsCreated += self.__onHubsCreation
        self.__giftsController.onEventHubsDestroyed += self.__onHubsDestruction
        if self._eventHub is not None:
            self._eventHub.onHubUpdated += self._onGiftHubUpdate
        return

    def __unsubFromGiftEventHub(self):
        self.__giftsController.onEventHubsCreated -= self.__onHubsCreation
        self.__giftsController.onEventHubsDestroyed -= self.__onHubsDestruction
        if self._eventHub is not None:
            self._eventHub.onHubUpdated -= self._onGiftHubUpdate
        return
