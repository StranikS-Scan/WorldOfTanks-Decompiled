# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/tooltips/mode_selector_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ModeSelectorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ModeSelectorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBattleTypes(self):
        return self._getArray(0)

    def setBattleTypes(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(ModeSelectorTooltipModel, self)._initialize()
        self._addArrayProperty('battleTypes', Array())
