# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bob/bob_entry_point_view_model.py
from frameworks.wulf import ViewModel

class BobEntryPointViewModel(ViewModel):
    __slots__ = ('onActionClick',)
    REGISTRATION_BEFORE_EVENT_START = 'registrationBeforeEventStart'
    REGISTRATION_AFTER_EVENT_START = 'registrationAfterEventStart'
    REGISTRATION_LAST_TIME = 'registrationLastTime'
    WAITING_EVENT_START = 'waitingEventStart'
    WAITING_EVENT_FINISH = 'waitingEventFinish'
    AVAILABLE_PRIME_TIME = 'availablePrimeTime'
    NOT_AVAILABLE_PRIME_TIME = 'notAvailablePrimeTime'
    LAST_AVAILABLE_PRIME_TIME = 'lastAvailablePrimeTime'
    ADD_TEAM_EXTRA_POINTS = 'addTeamExtraPoints'
    TEAM_REWARD = 'teamReward'
    EVENT_FINISH = 'eventFinish'

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
        return self._getString(3)

    def setState(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(BobEntryPointViewModel, self)._initialize()
        self._addStringProperty('header', '')
        self._addStringProperty('body', '')
        self._addStringProperty('footer', '')
        self._addStringProperty('state', 'registrationBeforeEventStart')
        self.onActionClick = self._addCommand('onActionClick')
