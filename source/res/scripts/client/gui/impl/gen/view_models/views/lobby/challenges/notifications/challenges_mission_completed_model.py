# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/challenges/notifications/challenges_mission_completed_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel
from gui.impl.gen.view_models.views.lobby.challenges.bonus_model import BonusModel

class ChallengesMissionCompletedModel(NotificationBaseModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(ChallengesMissionCompletedModel, self).__init__(properties=properties, commands=commands)

    def getMissionID(self):
        return self._getString(1)

    def setMissionID(self, value):
        self._setString(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(ChallengesMissionCompletedModel, self)._initialize()
        self._addStringProperty('missionID', '')
        self._addArrayProperty('rewards', Array())
        self.onClick = self._addCommand('onClick')
