# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/challenges/notifications/challenges_shield_used_model.py
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel

class ChallengesShieldUsedModel(NotificationBaseModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(ChallengesShieldUsedModel, self).__init__(properties=properties, commands=commands)

    def getAttempts(self):
        return self._getNumber(1)

    def setAttempts(self, value):
        self._setNumber(1, value)

    def getMissionID(self):
        return self._getString(2)

    def setMissionID(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ChallengesShieldUsedModel, self)._initialize()
        self._addNumberProperty('attempts', 0)
        self._addStringProperty('missionID', '')
        self.onClick = self._addCommand('onClick')
