# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_off_season_view_model.py
from frameworks.wulf import ViewModel

class BattlePassOffSeasonViewModel(ViewModel):
    __slots__ = ()
    LOSE_VOTE = 'loseVote'
    WIN_VOTE = 'winVote'
    NOT_VOTE = 'notVote'

    def __init__(self, properties=12, commands=0):
        super(BattlePassOffSeasonViewModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getHasBattlePass(self):
        return self._getBool(1)

    def setHasBattlePass(self, value):
        self._setBool(1, value)

    def getIsPostProgression(self):
        return self._getBool(2)

    def setIsPostProgression(self, value):
        self._setBool(2, value)

    def getIsPostProgressionCompleted(self):
        return self._getBool(3)

    def setIsPostProgressionCompleted(self, value):
        self._setBool(3, value)

    def getIsEnabled(self):
        return self._getBool(4)

    def setIsEnabled(self, value):
        self._setBool(4, value)

    def getLeftVehicle(self):
        return self._getString(5)

    def setLeftVehicle(self, value):
        self._setString(5, value)

    def getLeftPoints(self):
        return self._getNumber(6)

    def setLeftPoints(self, value):
        self._setNumber(6, value)

    def getRightVehicle(self):
        return self._getString(7)

    def setRightVehicle(self, value):
        self._setString(7, value)

    def getRightPoints(self):
        return self._getNumber(8)

    def setRightPoints(self, value):
        self._setNumber(8, value)

    def getSeasonName(self):
        return self._getString(9)

    def setSeasonName(self, value):
        self._setString(9, value)

    def getIsFailedService(self):
        return self._getBool(10)

    def setIsFailedService(self, value):
        self._setBool(10, value)

    def getVoteStatus(self):
        return self._getString(11)

    def setVoteStatus(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(BattlePassOffSeasonViewModel, self)._initialize()
        self._addNumberProperty('level', 1)
        self._addBoolProperty('hasBattlePass', False)
        self._addBoolProperty('isPostProgression', False)
        self._addBoolProperty('isPostProgressionCompleted', False)
        self._addBoolProperty('isEnabled', True)
        self._addStringProperty('leftVehicle', '')
        self._addNumberProperty('leftPoints', 0)
        self._addStringProperty('rightVehicle', '')
        self._addNumberProperty('rightPoints', 0)
        self._addStringProperty('seasonName', '')
        self._addBoolProperty('isFailedService', False)
        self._addStringProperty('voteStatus', 'notVote')
