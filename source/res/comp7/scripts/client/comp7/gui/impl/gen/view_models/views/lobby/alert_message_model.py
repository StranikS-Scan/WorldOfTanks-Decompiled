# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/alert_message_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel

class State(Enum):
    NONE = 'none'
    BAN = 'ban'
    PREANNOUNCE = 'preannounce'
    NOVEHICLES = 'noVehicles'
    QUALIFICATION = 'qualification'
    CEASEFIREAVAILABLE = 'ceasefireAvailable'
    CEASEFIREUNAVAILABLE = 'ceasefireUnavailable'
    MODEOFFLINE = 'modeOffline'
    SEASONEND = 'seasonEnd'


class AlertMessageModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(AlertMessageModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getBanTimeleftInSeconds(self):
        return self._getNumber(1)

    def setBanTimeleftInSeconds(self, value):
        self._setNumber(1, value)

    def getStartEventTimestamp(self):
        return self._getNumber(2)

    def setStartEventTimestamp(self, value):
        self._setNumber(2, value)

    def getLevels(self):
        return self._getArray(3)

    def setLevels(self, value):
        self._setArray(3, value)

    @staticmethod
    def getLevelsType():
        return int

    def _initialize(self):
        super(AlertMessageModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('banTimeleftInSeconds', 0)
        self._addNumberProperty('startEventTimestamp', 0)
        self._addArrayProperty('levels', Array())
        self.onClick = self._addCommand('onClick')
