# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/tooltips/advent_calendar_simple_tooltip_model.py
from frameworks.wulf import ViewModel

class AdventCalendarSimpleTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(AdventCalendarSimpleTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPayload(self):
        return self._getString(0)

    def setPayload(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(AdventCalendarSimpleTooltipModel, self)._initialize()
        self._addStringProperty('payload', '')
