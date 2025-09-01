# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tanksetup/tooltips/popular_loadouts_tooltip_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class PopularLoadoutsTooltipModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(PopularLoadoutsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getOptionalDevicesResultType(self):
        return self._getNumber(10)

    def setOptionalDevicesResultType(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(PopularLoadoutsTooltipModel, self)._initialize()
        self._addNumberProperty('optionalDevicesResultType', 0)
