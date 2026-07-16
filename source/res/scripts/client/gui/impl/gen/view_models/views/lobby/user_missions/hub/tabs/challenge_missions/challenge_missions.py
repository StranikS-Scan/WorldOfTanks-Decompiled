# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/challenge_missions/challenge_missions.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.challenge_missions.challenges_pack import ChallengesPack

class ChallengeMissions(ViewModel):
    __slots__ = ('onSelectChallenge', 'openPreview', 'onAction')
    ACTION_ACTIVATE = 'activate'
    ACTION_RESTART = 'restart'
    ACTION_SURRENDER = 'surrender'

    def __init__(self, properties=6, commands=3):
        super(ChallengeMissions, self).__init__(properties=properties, commands=commands)

    def getEnabled(self):
        return self._getBool(0)

    def setEnabled(self, value):
        self._setBool(0, value)

    def getActiveChallengeID(self):
        return self._getNumber(1)

    def setActiveChallengeID(self, value):
        self._setNumber(1, value)

    def getIsSuitableVehicles(self):
        return self._getBool(2)

    def setIsSuitableVehicles(self, value):
        self._setBool(2, value)

    def getSelectedChallengeID(self):
        return self._getNumber(3)

    def setSelectedChallengeID(self, value):
        self._setNumber(3, value)

    def getSelectedChallengeExpireTime(self):
        return self._getNumber(4)

    def setSelectedChallengeExpireTime(self, value):
        self._setNumber(4, value)

    def getChallengesPacks(self):
        return self._getArray(5)

    def setChallengesPacks(self, value):
        self._setArray(5, value)

    @staticmethod
    def getChallengesPacksType():
        return ChallengesPack

    def _initialize(self):
        super(ChallengeMissions, self)._initialize()
        self._addBoolProperty('enabled', False)
        self._addNumberProperty('activeChallengeID', 0)
        self._addBoolProperty('isSuitableVehicles', False)
        self._addNumberProperty('selectedChallengeID', 0)
        self._addNumberProperty('selectedChallengeExpireTime', 0)
        self._addArrayProperty('challengesPacks', Array())
        self.onSelectChallenge = self._addCommand('onSelectChallenge')
        self.openPreview = self._addCommand('openPreview')
        self.onAction = self._addCommand('onAction')
