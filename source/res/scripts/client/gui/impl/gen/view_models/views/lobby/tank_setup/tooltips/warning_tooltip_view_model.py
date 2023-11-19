# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/tooltips/warning_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class WarningDescription(Enum):
    SIMILARDEVICEALREADYINSTALLED = 'similar_device_already_installed'
    TOOHEAVY = 'too_heavy'
    USELESSBATTLEBOOSTER = 'useless_battle_booster'


class WarningTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WarningTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getReason(self):
        return WarningDescription(self._getString(0))

    def setReason(self, value):
        self._setString(0, value.value)

    def getIsCritical(self):
        return self._getBool(1)

    def setIsCritical(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(WarningTooltipViewModel, self)._initialize()
        self._addStringProperty('reason')
        self._addBoolProperty('isCritical', False)
