# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/comp7_grand_tournament_widget_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class Comp7GrandTournamentState(Enum):
    COUNTDOWN = 'countdown'
    LIVE = 'live'
    DAYISOVER = 'dayIsOver'
    FINISHED = 'finished'


class Comp7GrandTournamentWidgetModel(ViewModel):
    __slots__ = ('onOpenComp7GrandTournament',)

    def __init__(self, properties=3, commands=1):
        super(Comp7GrandTournamentWidgetModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return Comp7GrandTournamentState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getIsExtended(self):
        return self._getBool(1)

    def setIsExtended(self, value):
        self._setBool(1, value)

    def getTimeLeft(self):
        return self._getNumber(2)

    def setTimeLeft(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(Comp7GrandTournamentWidgetModel, self)._initialize()
        self._addStringProperty('state')
        self._addBoolProperty('isExtended', False)
        self._addNumberProperty('timeLeft', 0)
        self.onOpenComp7GrandTournament = self._addCommand('onOpenComp7GrandTournament')
