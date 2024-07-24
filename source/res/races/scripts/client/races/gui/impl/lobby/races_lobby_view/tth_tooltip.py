# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/races_lobby_view/tth_tooltip.py
from helpers import dependency
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.items_parameters.params import VehicleParams
from items.components import component_constants
from races.gui.impl.gen.view_models.views.lobby.races_lobby_view.tth_tooltip_model import TthTooltipModel, Property
from skeletons.gui.game_control import IRacesBattleController
from skeletons.gui.shared import IItemsCache

class TthTooltip(ViewImpl):
    __slots__ = ('_property',)
    __racesCtrl = dependency.descriptor(IRacesBattleController)
    __itemsCache = dependency.descriptor(IItemsCache)
    KG_IN_TON = 1000

    def __init__(self, property):
        settings = ViewSettings(layoutID=R.views.races.lobby.races_lobby_view.TTHTooltip())
        settings.model = TthTooltipModel()
        super(TthTooltip, self).__init__(settings)
        self._property = property

    @property
    def viewModel(self):
        return super(TthTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TthTooltip, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setValue(self._getValue())
            model.setProperty(self._property)

    def _getValue(self):
        value = ''
        availiableVehicles = self.__racesCtrl.getRacesVehiclesInfo()
        vehCompDescr = self.__racesCtrl.getSelectedRacesVehicleDescr()
        tth = availiableVehicles.get(vehCompDescr)['vehicleTth']
        vehicle = self.__itemsCache.items.getItemByCD(vehCompDescr)
        vehParams = VehicleParams(vehicle)
        if self._property == Property.MAXSPEED.value:
            value = int(vehParams.speedLimits[0])
        elif self._property == Property.RELOADTIME.value:
            value = int(vehParams.reloadTimeSecs[0])
        elif self._property == Property.ACCELERATION.value:
            value = self.__calculateAccelerationFromZeroToHundred(vehParams)
        elif tth:
            value = tth[self._property]
        return str(value)

    def __calculateAccelerationFromZeroToHundred(self, vehParams, precision=1):
        raceWeightInKg = vehParams.vehicleWeight * self.KG_IN_TON
        enginePower = vehParams.enginePower
        return round(raceWeightInKg * (100 * component_constants.KMH_TO_MS) ** 2 / (2 * enginePower * component_constants.HP_TO_WATTS), precision)
