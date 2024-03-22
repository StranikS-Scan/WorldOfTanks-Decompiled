# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/tournaments_widget_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TournamentsState(Enum):
    REGISTRATION = 'registration'
    ACTIVE = 'active'


class TournamentsWidgetModel(ViewModel):
    __slots__ = ('onOpenTournaments',)

    def __init__(self, properties=3, commands=1):
        super(TournamentsWidgetModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getState(self):
        return TournamentsState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getIsExtended(self):
        return self._getBool(2)

    def setIsExtended(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(TournamentsWidgetModel, self)._initialize()
        self._addBoolProperty('isEnabled', False)
        self._addStringProperty('state')
        self._addBoolProperty('isExtended', False)
        self.onOpenTournaments = self._addCommand('onOpenTournaments')
