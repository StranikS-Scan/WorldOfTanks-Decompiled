# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/buy_vehicle_view.py
from gui.Scaleform.framework.entities.view_sound import ViewSoundMixin
from gui.impl.lobby.secret_event.sound_constants import BUYING_SETTINGS
from gui.impl.lobby.buy_vehicle_view import BuyVehicleWindow, BuyVehicleView
from helpers import dependency
from gui.shared import event_dispatcher
from skeletons.gui.server_events import IEventsCache

class _BuyVehicleView(BuyVehicleView, ViewSoundMixin):
    eventsCache = dependency.descriptor(IEventsCache)
    _COMMON_SOUND_SPACE = BUYING_SETTINGS

    def __init__(self, **kwargs):
        super(_BuyVehicleView, self).__init__(**kwargs)
        self._initSoundManager()

    def _initialize(self):
        super(_BuyVehicleView, self)._initialize()
        self._startSoundManager()
        self.eventsCache.onSyncCompleted += self.__onEventsCacheResync

    def _finalize(self):
        self.eventsCache.onSyncCompleted -= self.__onEventsCacheResync
        self._deinitSoundManager()
        super(_BuyVehicleView, self)._finalize()

    def __onEventsCacheResync(self):
        if not self.eventsCache.isEventEnabled():
            event_dispatcher.showHangar()
            self.__onWindowClose()


class SecretEventBuyVehicleWindow(BuyVehicleWindow):

    def _getSettings(self, **kwargs):
        settings = super(SecretEventBuyVehicleWindow, self)._getSettings(**kwargs)
        settings.content = _BuyVehicleView(**kwargs)
        return settings
