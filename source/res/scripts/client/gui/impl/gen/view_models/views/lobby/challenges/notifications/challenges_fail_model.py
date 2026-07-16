# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/challenges/notifications/challenges_fail_model.py
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel

class ChallengesFailModel(NotificationBaseModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(ChallengesFailModel, self).__init__(properties=properties, commands=commands)

    def getChallengeName(self):
        return self._getString(1)

    def setChallengeName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(ChallengesFailModel, self)._initialize()
        self._addStringProperty('challengeName', '')
        self.onClick = self._addCommand('onClick')
