# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/tooltips/event_battle_calendar_tooltip_model.py
from frameworks.wulf import ViewModel

class EventBattleCalendarTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(EventBattleCalendarTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndActivePhaseDate(self):
        return self._getNumber(1)

    def setEndActivePhaseDate(self, value):
        self._setNumber(1, value)

    def getEndEventDate(self):
        return self._getNumber(2)

    def setEndEventDate(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(EventBattleCalendarTooltipModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endActivePhaseDate', 0)
        self._addNumberProperty('endEventDate', 0)
