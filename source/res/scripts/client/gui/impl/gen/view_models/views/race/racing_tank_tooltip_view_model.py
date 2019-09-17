# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/race/racing_tank_tooltip_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.Scaleform.daapi.view.lobby.race.user_tech_parameter_model import UserTechParameterModel

class RacingTankTooltipViewModel(ViewModel):
    __slots__ = ()

    @property
    def techParams(self):
        return self._getViewModel(0)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(RacingTankTooltipViewModel, self)._initialize()
        self._addViewModelProperty('techParams', UserTechParameterModel())
        self._addStringProperty('name', '')
        self._addResourceProperty('description', R.invalid())
