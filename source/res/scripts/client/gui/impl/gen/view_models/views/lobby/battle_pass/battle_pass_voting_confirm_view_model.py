# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_voting_confirm_view_model.py
from frameworks.wulf import ViewModel

class BattlePassVotingConfirmViewModel(ViewModel):
    __slots__ = ('onVoteClick',)

    def __init__(self, properties=5, commands=1):
        super(BattlePassVotingConfirmViewModel, self).__init__(properties=properties, commands=commands)

    def getStyleName(self):
        return self._getString(0)

    def setStyleName(self, value):
        self._setString(0, value)

    def getRecruitName(self):
        return self._getString(1)

    def setRecruitName(self, value):
        self._setString(1, value)

    def getIsBattlePassBought(self):
        return self._getBool(2)

    def setIsBattlePassBought(self, value):
        self._setBool(2, value)

    def getIsRight(self):
        return self._getBool(3)

    def setIsRight(self, value):
        self._setBool(3, value)

    def getIsLeft(self):
        return self._getBool(4)

    def setIsLeft(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(BattlePassVotingConfirmViewModel, self)._initialize()
        self._addStringProperty('styleName', '')
        self._addStringProperty('recruitName', '')
        self._addBoolProperty('isBattlePassBought', False)
        self._addBoolProperty('isRight', False)
        self._addBoolProperty('isLeft', False)
        self.onVoteClick = self._addCommand('onVoteClick')
