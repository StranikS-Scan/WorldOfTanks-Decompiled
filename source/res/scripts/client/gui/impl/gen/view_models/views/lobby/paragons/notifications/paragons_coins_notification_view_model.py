# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/notifications/paragons_coins_notification_view_model.py
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class ParagonsCoinsNotificationViewModel(NotificationModel):
    __slots__ = ('goToTechTree', 'goToParagons')

    def __init__(self, properties=4, commands=2):
        super(ParagonsCoinsNotificationViewModel, self).__init__(properties=properties, commands=commands)

    def getIsEntryPointAvailable(self):
        return self._getBool(1)

    def setIsEntryPointAvailable(self, value):
        self._setBool(1, value)

    def getCount(self):
        return self._getNumber(2)

    def setCount(self, value):
        self._setNumber(2, value)

    def getMinVehicleCount(self):
        return self._getNumber(3)

    def setMinVehicleCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ParagonsCoinsNotificationViewModel, self)._initialize()
        self._addBoolProperty('isEntryPointAvailable', False)
        self._addNumberProperty('count', 1)
        self._addNumberProperty('minVehicleCount', 1)
        self.goToTechTree = self._addCommand('goToTechTree')
        self.goToParagons = self._addCommand('goToParagons')
