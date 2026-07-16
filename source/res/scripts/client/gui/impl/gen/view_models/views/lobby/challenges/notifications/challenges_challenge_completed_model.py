# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/challenges/notifications/challenges_challenge_completed_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel
from gui.impl.gen.view_models.views.lobby.challenges.bonus_model import BonusModel

class ChallengesChallengeCompletedModel(NotificationBaseModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(ChallengesChallengeCompletedModel, self).__init__(properties=properties, commands=commands)

    def getChallengeName(self):
        return self._getString(1)

    def setChallengeName(self, value):
        self._setString(1, value)

    def getAnyMissionsLeft(self):
        return self._getBool(2)

    def setAnyMissionsLeft(self, value):
        self._setBool(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(ChallengesChallengeCompletedModel, self)._initialize()
        self._addStringProperty('challengeName', '')
        self._addBoolProperty('anyMissionsLeft', False)
        self._addArrayProperty('rewards', Array())
        self.onClick = self._addCommand('onClick')
