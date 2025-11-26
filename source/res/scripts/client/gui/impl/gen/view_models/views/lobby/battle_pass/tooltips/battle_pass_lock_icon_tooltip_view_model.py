# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_lock_icon_tooltip_view_model.py
from frameworks.wulf import ViewModel

class BattlePassLockIconTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BattlePassLockIconTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsHoliday(self):
        return self._getBool(0)

    def setIsHoliday(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(BattlePassLockIconTooltipViewModel, self)._initialize()
        self._addBoolProperty('isHoliday', False)
