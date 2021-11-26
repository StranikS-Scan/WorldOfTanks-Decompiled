# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/marathon_vehicle_preview.py
import typing
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.server_events.events_dispatcher import showMissionsMarathon
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController
from gui.impl import backport
from gui.impl.gen import R
from web.web_client_api.common import ItemPackTypeGroup

class MarathonVehiclePreview(VehiclePreview):
    __marathonCtrl = dependency.descriptor(IMarathonEventsController)

    def __init__(self, ctx=None):
        super(MarathonVehiclePreview, self).__init__(ctx)
        self.__marathonPrefix = ctx.get('marathonPrefix')
        self.__marathon = self.__marathonCtrl.getMarathon(self.__marathonPrefix)
        self.__backToHangar = ctx.get('backToHangar', False)

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VEHPREVIEW_CONSTANTS.BUYING_PANEL_PY_ALIAS:
            if self._itemsPack is not None:
                viewPy.setMarathonEvent(self.__marathonPrefix)
                viewPy.setInfoTooltip()
                items = tuple((item for item in self._itemsPack if item.type not in ItemPackTypeGroup.CREW))
                viewPy.setPackItems(items, self._price, self._oldPrice, self._title)
        elif alias == VEHPREVIEW_CONSTANTS.CREW_LINKAGE:
            if self._itemsPack:
                crewItems = tuple((item for item in self._itemsPack if item.type in ItemPackTypeGroup.CREW))
                vehicleItems = tuple((item for item in self._itemsPack if item.type in ItemPackTypeGroup.VEHICLE))
                viewPy.setVehicleCrews(vehicleItems, crewItems)
        return

    def _processBackClick(self, ctx=None):
        if self.__backToHangar:
            super(MarathonVehiclePreview, self)._processBackClick(ctx)
        else:
            showMissionsMarathon(self.__marathonPrefix)

    def _getBackBtnLabel(self):
        if self.__backToHangar:
            return backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.hangar())
        else:
            return backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.marathon()) if self.__marathon is None else backport.text(self.__marathon.backBtnLabel)

    def _getExitEvent(self):
        exitEvent = super(MarathonVehiclePreview, self)._getExitEvent()
        exitEvent.ctx.update({'marathonPrefix': self.__marathonPrefix})
        return exitEvent
