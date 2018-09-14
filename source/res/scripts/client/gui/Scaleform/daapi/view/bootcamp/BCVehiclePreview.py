# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCVehiclePreview.py
from gui.Scaleform.daapi.view.lobby.vehiclePreview.VehiclePreview import VehiclePreview
from gui.Scaleform.daapi.view.meta.BCVehiclePreviewMeta import BCVehiclePreviewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared import event_dispatcher
from gui.Scaleform.framework import g_entitiesFactories
from bootcamp.Bootcamp import g_bootcamp, DISABLED_TANK_LEVELS
from bootcamp.BootCampEvents import g_bootcampEvents
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from BCSimpleDialog import BCSimpleDialog

class BCVehiclePreview(BCVehiclePreviewMeta):

    def __init__(self, ctx=None):
        super(BCVehiclePreview, self).__init__(ctx, skipConfirm=True)
        self._showVehInfoPanel = False
        self._showHeaderCloseBtn = False
        self.__vehicleCD = ctx.get('itemCD')
        self.__backAlias = ctx.get('previewAlias', VIEW_ALIAS.BOOTCAMP_VEHICLE_PREVIEW)
        self._disableBuyButton = False

    def _populate(self):
        g_currentPreviewVehicle.selectVehicle(self.__vehicleCD)
        if g_currentPreviewVehicle.item.level in DISABLED_TANK_LEVELS:
            self._disableBuyButton = True
        super(BCVehiclePreview, self)._populate()
        g_bootcampEvents.onRequestChangeVehiclePreviewBuyButtonState += self.__setBuyButtonState
        from bootcamp.BootcampGarage import g_bootcampGarage
        nationData = g_bootcampGarage.getNationData()
        g_currentPreviewVehicle.onVehicleUnlocked += self.__onVehicleUnlockedMessage
        g_currentPreviewVehicle.onVehicleInventoryChanged += self.__onVehicleInventoryChanged
        foundHints = False
        if nationData['vehicle_second'] == self.__vehicleCD:
            foundHints = g_bootcampGarage.runViewAlias(self.alias)
        if not foundHints:
            g_bootcampGarage.closeAllPopUps()
            g_bootcampGarage.checkReturnToHangar()

    def _dispose(self):
        super(BCVehiclePreview, self)._dispose()
        g_bootcampEvents.onRequestChangeVehiclePreviewBuyButtonState -= self.__setBuyButtonState
        g_currentPreviewVehicle.onVehicleUnlocked -= self.__onVehicleUnlockedMessage
        g_currentPreviewVehicle.onVehicleInventoryChanged -= self.__onVehicleInventoryChanged
        from bootcamp.BootcampGarage import g_bootcampGarage
        g_bootcampGarage.closeAllPopUps()

    def __onVehicleUnlockedMessage(self):
        from bootcamp.BootcampGarage import g_bootcampGarage
        g_bootcampGarage.showNextHint()

    def __onVehicleInventoryChanged(self):
        from bootcamp.BootcampGarage import g_bootcampGarage
        g_bootcampGarage.showNextHint()

    def onBackClick(self):
        if self.__backAlias == VIEW_ALIAS.BOOTCAMP_LOBBY_RESEARCH:
            event_dispatcher.showResearchView(self.__vehicleCD)
        else:
            event = g_entitiesFactories.makeLoadEvent(self.__backAlias)
            self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def onBuyOrResearchClick(self):
        from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
        from bootcamp.BootcampGarage import g_bootcampGarage
        nationData = g_bootcampGarage.getNationData()
        if nationData['vehicle_second'] == self.__vehicleCD:
            super(BCVehiclePreview, self).onBuyOrResearchClick()
            if self._actionType == ItemsActionsFactory.UNLOCK_ITEM:
                g_bootcampGarage.highlightLobbyHint('DialogAccept')

    def __setBuyButtonState(self, enabled):
        self._disableBuyButton = not enabled
        self._updateBtnState()
