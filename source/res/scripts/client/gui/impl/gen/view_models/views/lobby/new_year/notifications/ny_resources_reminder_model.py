# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_resources_reminder_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class reminderType(Enum):
    PERSONAL = 'Personal'
    FRIENDS = 'Friends'
    FINDFRIENDS = 'FindFriends'


class NyResourcesReminderModel(NotificationModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=6, commands=1):
        super(NyResourcesReminderModel, self).__init__(properties=properties, commands=commands)

    def getResourcesCount(self):
        return self._getNumber(1)

    def setResourcesCount(self, value):
        self._setNumber(1, value)

    def getIsExtra(self):
        return self._getBool(2)

    def setIsExtra(self, value):
        self._setBool(2, value)

    def getViewType(self):
        return reminderType(self._getString(3))

    def setViewType(self, value):
        self._setString(3, value.value)

    def getFriendName(self):
        return self._getString(4)

    def setFriendName(self, value):
        self._setString(4, value)

    def getIsButtonDisabled(self):
        return self._getBool(5)

    def setIsButtonDisabled(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NyResourcesReminderModel, self)._initialize()
        self._addNumberProperty('resourcesCount', 0)
        self._addBoolProperty('isExtra', False)
        self._addStringProperty('viewType')
        self._addStringProperty('friendName', '')
        self._addBoolProperty('isButtonDisabled', False)
        self.onClick = self._addCommand('onClick')
