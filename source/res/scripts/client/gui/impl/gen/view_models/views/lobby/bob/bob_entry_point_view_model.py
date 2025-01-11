# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bob/bob_entry_point_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    BEFOREEVENTSTART = 'beforeEventStart'
    PAUSED = 'paused'
    REGISTRATIONAFTEREVENTSTART = 'registrationAfterEventStart'
    AVAILABLEPRIMETIME = 'availablePrimeTime'
    NOTAVAILABLEPRIMETIME = 'notAvailablePrimeTime'
    EVENTFINISH = 'eventFinish'


class BobEntryPointViewModel(ViewModel):
    __slots__ = ('onAction',)

    def __init__(self, properties=4, commands=1):
        super(BobEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getHeader(self):
        return self._getString(0)

    def setHeader(self, value):
        self._setString(0, value)

    def getBody(self):
        return self._getString(1)

    def setBody(self, value):
        self._setString(1, value)

    def getFooter(self):
        return self._getString(2)

    def setFooter(self, value):
        self._setString(2, value)

    def getState(self):
        return State(self._getString(3))

    def setState(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(BobEntryPointViewModel, self)._initialize()
        self._addStringProperty('header', '')
        self._addStringProperty('body', '')
        self._addStringProperty('footer', '')
        self._addStringProperty('state', State.BEFOREEVENTSTART.value)
        self.onAction = self._addCommand('onAction')
