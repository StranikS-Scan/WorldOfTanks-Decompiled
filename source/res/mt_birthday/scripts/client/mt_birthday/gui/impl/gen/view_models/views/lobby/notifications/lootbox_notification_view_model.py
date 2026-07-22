# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/notifications/lootbox_notification_view_model.py
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class LootboxNotificationViewModel(NotificationModel):
    __slots__ = ('goToContainers',)

    def __init__(self, properties=3, commands=1):
        super(LootboxNotificationViewModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getIsSmallContainer(self):
        return self._getBool(2)

    def setIsSmallContainer(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(LootboxNotificationViewModel, self)._initialize()
        self._addNumberProperty('count', 1)
        self._addBoolProperty('isSmallContainer', True)
        self.goToContainers = self._addCommand('goToContainers')
