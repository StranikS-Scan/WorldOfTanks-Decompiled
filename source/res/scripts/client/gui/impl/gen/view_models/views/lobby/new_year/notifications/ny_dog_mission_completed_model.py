# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_dog_mission_completed_model.py
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class NyDogMissionCompletedModel(NotificationModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(NyDogMissionCompletedModel, self).__init__(properties=properties, commands=commands)

    def getMissionsCompleted(self):
        return self._getNumber(1)

    def setMissionsCompleted(self, value):
        self._setNumber(1, value)

    def getMissionsTotal(self):
        return self._getNumber(2)

    def setMissionsTotal(self, value):
        self._setNumber(2, value)

    def getBundleLevel(self):
        return self._getNumber(3)

    def setBundleLevel(self, value):
        self._setNumber(3, value)

    def getIsButtonDisabled(self):
        return self._getBool(4)

    def setIsButtonDisabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(NyDogMissionCompletedModel, self)._initialize()
        self._addNumberProperty('missionsCompleted', 0)
        self._addNumberProperty('missionsTotal', 0)
        self._addNumberProperty('bundleLevel', 0)
        self._addBoolProperty('isButtonDisabled', False)
        self.onClick = self._addCommand('onClick')
