# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_dog_reminder_model.py
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class NyDogReminderModel(NotificationModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(NyDogReminderModel, self).__init__(properties=properties, commands=commands)

    def getIsButtonDisabled(self):
        return self._getBool(1)

    def setIsButtonDisabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(NyDogReminderModel, self)._initialize()
        self._addBoolProperty('isButtonDisabled', False)
        self.onClick = self._addCommand('onClick')
