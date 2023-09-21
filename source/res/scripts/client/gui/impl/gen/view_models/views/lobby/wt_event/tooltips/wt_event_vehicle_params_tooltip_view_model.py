# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_vehicle_params_tooltip_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.property_model import PropertyModel

class WtEventVehicleParamsTooltipViewModel(PropertyModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(WtEventVehicleParamsTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(WtEventVehicleParamsTooltipViewModel, self)._initialize()
        self._addResourceProperty('description', R.invalid())
