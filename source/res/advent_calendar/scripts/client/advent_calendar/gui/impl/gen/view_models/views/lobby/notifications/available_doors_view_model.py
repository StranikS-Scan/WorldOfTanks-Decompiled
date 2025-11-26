# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/gen/view_models/views/lobby/notifications/available_doors_view_model.py
from enum import Enum
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel

class State(Enum):
    DOORS_AVAILABLE = 'doorsAvailable'
    FIRST_ENTRY = 'firstEntry'
    POST_EVENT = 'postEvent'


class Theme(Enum):
    AUTUMN = 'autumn'
    WINTER = 'winter'


class AvailableDoorsViewModel(NotificationBaseModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(AvailableDoorsViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getTheme(self):
        return Theme(self._getString(2))

    def setTheme(self, value):
        self._setString(2, value.value)

    def getEventEndDate(self):
        return self._getNumber(3)

    def setEventEndDate(self, value):
        self._setNumber(3, value)

    def getIsButtonDisabled(self):
        return self._getBool(4)

    def setIsButtonDisabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(AvailableDoorsViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addStringProperty('theme')
        self._addNumberProperty('eventEndDate', 0)
        self._addBoolProperty('isButtonDisabled', False)
        self.onClick = self._addCommand('onClick')
