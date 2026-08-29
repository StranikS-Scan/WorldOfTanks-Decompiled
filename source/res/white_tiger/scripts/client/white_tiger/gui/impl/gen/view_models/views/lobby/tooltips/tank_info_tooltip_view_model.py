# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/tank_info_tooltip_view_model.py
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.property_model import PropertyModel

class TankInfoTooltipViewModel(PropertyModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TankInfoTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(TankInfoTooltipViewModel, self)._initialize()
        self._addResourceProperty('description', R.invalid())
