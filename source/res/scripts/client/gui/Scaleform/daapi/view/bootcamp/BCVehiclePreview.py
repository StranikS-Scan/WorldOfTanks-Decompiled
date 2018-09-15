# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCVehiclePreview.py
from gui.Scaleform.daapi.view.meta.BCVehiclePreviewMeta import BCVehiclePreviewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared import event_dispatcher
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.Scaleform.framework import g_entitiesFactories
from bootcamp.Bootcamp import DISABLED_TANK_LEVELS
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampGarage import g_bootcampGarage
from CurrentVehicle import g_currentPreviewVehicle

class BCVehiclePreview(BCVehiclePreviewMeta):

    def __init__(self, ctx=None):
        super(BCVehiclePreview, self).__init__(ctx, skipConfirm=True)
        self._showVehInfoPanel = False
        self._showHeaderCloseBtn = False
        self._disableBuyButton = False

    def onBackClick(self):
        if self._backAlias == VIEW_ALIAS.LOBBY_RESEARCH and self.__isSecondVehicle():
            firstVehicleCD = g_bootcampGarage.getNationData()['vehicle_first']
            event_dispatcher.showResearchView(firstVehicleCD)
        else:
            super(BCVehiclePreview, self).onBackClick()

    def onBuyOrResearchClick(self):
        if self.__isSecondVehicle():
            super(BCVehiclePreview, self).onBuyOrResearchClick()
            if self._actionType == ItemsActionsFactory.UNLOCK_ITEM:
                g_bootcampGarage.highlightLobbyHint('DialogAccept')

    def _populate(self):
        g_currentPreviewVehicle.selectVehicle(self._vehicleCD)
        if g_currentPreviewVehicle.item.level in DISABLED_TANK_LEVELS:
            self._disableBuyButton = True
        super(BCVehiclePreview, self)._populate()
        g_bootcampEvents.onRequestChangeVehiclePreviewBuyButtonState += self.__setBuyButtonState
        g_currentPreviewVehicle.onVehicleUnlocked += self.__onVehicleUnlockedMessage
        g_currentPreviewVehicle.onVehicleInventoryChanged += self.__onVehicleInventoryChanged
        foundHints = False
        if self.__isSecondVehicle():
            foundHints = g_bootcampGarage.runViewAlias(self.alias)
        if not foundHints:
            g_bootcampGarage.checkReturnToHangar()
        g_bootcampEvents.onEnterPreview()

    def _dispose(self):
        super(BCVehiclePreview, self)._dispose()
        g_bootcampEvents.onRequestChangeVehiclePreviewBuyButtonState -= self.__setBuyButtonState
        g_currentPreviewVehicle.onVehicleUnlocked -= self.__onVehicleUnlockedMessage
        g_currentPreviewVehicle.onVehicleInventoryChanged -= self.__onVehicleInventoryChanged
        g_bootcampEvents.onExitPreview()

    def __onVehicleUnlockedMessage(self):
        g_bootcampGarage.showNextHint()

    def __onVehicleInventoryChanged(self):
        g_bootcampGarage.showNextHint()

    def __setBuyButtonState(self, enabled):
        self._disableBuyButton = not enabled
        self._updateBtnState()

    def __isSecondVehicle(self):
        nationData = g_bootcampGarage.getNationData()
        return nationData['vehicle_second'] == self._vehicleCD
