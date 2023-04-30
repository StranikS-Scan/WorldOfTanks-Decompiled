# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/tooltips/entry_point_before_progression_tooltip_view_model.py
from frameworks.wulf import ViewModel

class EntryPointBeforeProgressionTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(EntryPointBeforeProgressionTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getStartTimestamp(self):
        return self._getNumber(0)

    def setStartTimestamp(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(EntryPointBeforeProgressionTooltipViewModel, self)._initialize()
        self._addNumberProperty('startTimestamp', 0)
