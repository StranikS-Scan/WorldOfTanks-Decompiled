# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCVehiclePreview.py
from gui.Scaleform.daapi.view.bootcamp.lobby.vehicle_preview.vehicle_preview_dp import BCVehPreviewDataProvider
from gui.Scaleform.daapi.view.lobby.vehiclePreview.VehiclePreview import VehiclePreview
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import event_dispatcher
from bootcamp.Bootcamp import DISABLED_TANK_LEVELS
from bootcamp.Bootcamp import g_bootcamp
from CurrentVehicle import g_currentPreviewVehicle
from soft_exception import SoftException

class BCVehiclePreview(VehiclePreview):

    def __init__(self, ctx=None):
        if 'previewDP' is ctx:
            raise SoftException('previewDP is already in ctx for BCVehiclePreview')
        ctx['previewDP'] = BCVehPreviewDataProvider()
        super(BCVehiclePreview, self).__init__(ctx, skipConfirm=False)
        self._showHeaderCloseBtn = False
        self._disableBuyButton = False

    def onBackClick(self):
        if self._backAlias == VIEW_ALIAS.LOBBY_RESEARCH and self.__isSecondVehicle():
            firstVehicleCD = g_bootcamp.getNationData()['vehicle_first']
            event_dispatcher.showResearchView(firstVehicleCD)
        else:
            super(BCVehiclePreview, self).onBackClick()

    def onBuyOrResearchClick(self):
        if self.__isSecondVehicle():
            super(BCVehiclePreview, self).onBuyOrResearchClick()

    def _populate(self):
        g_currentPreviewVehicle.selectVehicle(self._vehicleCD)
        if g_currentPreviewVehicle.item.level in DISABLED_TANK_LEVELS:
            self._disableBuyButton = True
        super(BCVehiclePreview, self)._populate()

    def __isSecondVehicle(self):
        nationData = g_bootcamp.getNationData()
        return nationData['vehicle_second'] == self._vehicleCD
