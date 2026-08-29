# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_configurable_vehicle_preview.py
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import ConfigurableVehiclePreview

class WTConfigurableVehiclePreview(ConfigurableVehiclePreview):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def closeView(self):
        self.__prebattleVehicle.selectAny()
        super(WTConfigurableVehiclePreview, self).closeView()
