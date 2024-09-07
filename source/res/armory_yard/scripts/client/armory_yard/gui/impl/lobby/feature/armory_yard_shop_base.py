# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_shop_base.py
from frameworks.wulf import ViewStatus
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import EVENT_BUS_SCOPE, events
from PlayerEvents import g_playerEvents

class ArmoryYardShopBaseView(ViewImpl, IGlobalListener):
    __slots__ = ('__isDestroyAfterLoaded', '__onLoadedCallback')

    def __init__(self, settings, onLoadedCallback=None):
        super(ArmoryYardShopBaseView, self).__init__(settings)
        self.__isDestroyAfterLoaded = False
        self.__onLoadedCallback = onLoadedCallback

    def _close(self, *_):
        self.destroyWindow()

    def _getListeners(self):
        return ((events.LobbyHeaderMenuEvent.MENU_CLICK, self._close, EVENT_BUS_SCOPE.LOBBY),)

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardShopBaseView, self)._onLoading(*args, **kwargs)
        g_playerEvents.onEnqueued += self._close
        self.startGlobalListening()

    def _onLoaded(self, *args, **kwargs):
        super(ArmoryYardShopBaseView, self)._onLoaded(*args, **kwargs)
        if self.__onLoadedCallback:
            self.__onLoadedCallback()
        if self.__isDestroyAfterLoaded:
            self.destroyWindow()

    def destroyWindow(self):
        if self.viewStatus == ViewStatus.LOADING:
            self.__isDestroyAfterLoaded = True
            return
        super(ArmoryYardShopBaseView, self).destroyWindow()
        self.stopGlobalListening()
        g_playerEvents.onEnqueued -= self._close

    def onPrbEntitySwitched(self):
        self._close()

    def onPreQueueSettingsChanged(self, diff):
        self._close()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self._close()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self._close()

    def destroy(self):
        super(ArmoryYardShopBaseView, self).destroy()
        self.stopGlobalListening()
        g_playerEvents.onEnqueued -= self._close
