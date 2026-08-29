# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_vehicle_style_preview.py
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview

class WTVehicleStylePreview(VehicleStylePreview):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    _SHOW_CLOSE_BTN = True

    def closeView(self):
        self.__prebattleVehicle.selectAny()
        super(WTVehicleStylePreview, self).closeView()

    def _getData(self):
        data = super(WTVehicleStylePreview, self)._getData()
        data.update({'showCloseBtn': self._SHOW_CLOSE_BTN})
        return data
