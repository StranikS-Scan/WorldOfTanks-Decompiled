# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/qfg_carousel/carousel_data_provider.py
from fun_random.gui.feature.util.fun_helpers import getVehicleComparisonKey
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS

class FunRandomQuickFireGunsCarouselDataProvider(CarouselDataProvider, FunSubModesWatcher):

    def onSubModeSelected(self):
        self.filter.update({}, False)
        self._setBaseCriteria()

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return getVehicleComparisonKey(vehicle)

    def _getVehicleStats(self, vehicle):
        return {'statsText': '',
         'visibleStats': False}

    def _setBaseCriteria(self):
        super(FunRandomQuickFireGunsCarouselDataProvider, self)._setBaseCriteria()
        self._baseCriteria = self.getDesiredSubMode().getCarouselBaseCriteria() or self._baseCriteria

    def _buildVehicle(self, vehicle):
        result = super(FunRandomQuickFireGunsCarouselDataProvider, self)._buildVehicle(vehicle)
        result['tooltip'] = TOOLTIPS_CONSTANTS.FUN_RANDOM_VEHICLE
        result['isWulfTooltip'] = True
        result['isEarnCrystals'] = False
        result['xpImgSource'] = ''
        return result
