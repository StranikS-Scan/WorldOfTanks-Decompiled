# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/notifications/crew_reward_notification_model.py
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel

class CrewRewardNotificationModel(NotificationBaseModel):
    __slots__ = ('onClose', 'onRecruit')

    def __init__(self, properties=5, commands=2):
        super(CrewRewardNotificationModel, self).__init__(properties=properties, commands=commands)

    def getPreName(self):
        return self._getString(1)

    def setPreName(self, value):
        self._setString(1, value)

    def getSurName(self):
        return self._getString(2)

    def setSurName(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getIsRecruited(self):
        return self._getBool(4)

    def setIsRecruited(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(CrewRewardNotificationModel, self)._initialize()
        self._addStringProperty('preName', '')
        self._addStringProperty('surName', '')
        self._addStringProperty('icon', '')
        self._addBoolProperty('isRecruited', False)
        self.onClose = self._addCommand('onClose')
        self.onRecruit = self._addCommand('onRecruit')
