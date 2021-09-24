# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/wt_event_vehicle_preview.py
import typing
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_model import PortalType
from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import ConfigurableVehiclePreview
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events, event_dispatcher
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class WtEventVehiclePreview(ConfigurableVehiclePreview):
    __eventCtrl = dependency.descriptor(IGameEventController)

    def _populate(self):
        super(WtEventVehiclePreview, self)._populate()
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.EVENT_VEHICLE_PREVIEW_OPEN), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__eventCtrl.onUpdated += self.__eventUpdated

    def _dispose(self):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.EVENT_VEHICLE_PREVIEW_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__eventCtrl.onUpdated -= self.__eventUpdated
        super(WtEventVehiclePreview, self)._dispose()

    def _processBackClick(self, ctx=None):
        self.closeView()
        if self.__eventCtrl.isAvailable():
            Waiting.show('updating', softStart=True)
            event_dispatcher.showEventPortalWindow(PortalType.TANK)
            self.__eventCtrl.doSelectEventPrb()

    def _getBackBtnLabel(self):
        return VEHICLE_PREVIEW.HEADER_BACKBTN_DESCRLABEL_WTTANKPORTAL

    def __eventUpdated(self):
        if not self.__eventCtrl.isAvailable():
            self.closeView()
