# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/notifications/doors_available_view_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class DoorsAvailableNotificationState(Enum):
    DOORS_AVAILABLE = 'doorsAvailable'
    FIRST_ENTRY = 'firstEntry'
    POST_EVENT = 'postEvent'


class DoorsAvailableViewModel(NotificationModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(DoorsAvailableViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return DoorsAvailableNotificationState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getEventEndDate(self):
        return self._getNumber(2)

    def setEventEndDate(self, value):
        self._setNumber(2, value)

    def getIsButtonDisabled(self):
        return self._getBool(3)

    def setIsButtonDisabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(DoorsAvailableViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('eventEndDate', 0)
        self._addBoolProperty('isButtonDisabled', False)
        self.onClick = self._addCommand('onClick')
