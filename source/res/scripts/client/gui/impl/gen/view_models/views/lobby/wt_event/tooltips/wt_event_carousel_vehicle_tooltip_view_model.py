# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_carousel_vehicle_tooltip_view_model.py
from frameworks.wulf import ViewModel

class WtEventCarouselVehicleTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WtEventCarouselVehicleTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleType(self):
        return self._getString(0)

    def setVehicleType(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(WtEventCarouselVehicleTooltipViewModel, self)._initialize()
        self._addStringProperty('vehicleType', '')
