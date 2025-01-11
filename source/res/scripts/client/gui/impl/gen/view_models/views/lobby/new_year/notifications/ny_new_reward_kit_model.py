# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_new_reward_kit_model.py
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class NyNewRewardKitModel(NotificationModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(NyNewRewardKitModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(1)

    def setCategory(self, value):
        self._setString(1, value)

    def getKitsCount(self):
        return self._getNumber(2)

    def setKitsCount(self, value):
        self._setNumber(2, value)

    def getIsButtonDisabled(self):
        return self._getBool(3)

    def setIsButtonDisabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyNewRewardKitModel, self)._initialize()
        self._addStringProperty('category', '')
        self._addNumberProperty('kitsCount', 0)
        self._addBoolProperty('isButtonDisabled', False)
        self.onClick = self._addCommand('onClick')
