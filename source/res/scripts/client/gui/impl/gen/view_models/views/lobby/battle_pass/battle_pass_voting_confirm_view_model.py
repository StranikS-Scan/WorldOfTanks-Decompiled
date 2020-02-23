# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_voting_confirm_view_model.py
from frameworks.wulf import ViewModel

class BattlePassVotingConfirmViewModel(ViewModel):
    __slots__ = ('onVoteClick',)

    def __init__(self, properties=5, commands=1):
        super(BattlePassVotingConfirmViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleCD(self):
        return self._getNumber(0)

    def setVehicleCD(self, value):
        self._setNumber(0, value)

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getStyleName(self):
        return self._getString(2)

    def setStyleName(self, value):
        self._setString(2, value)

    def getRecruitName(self):
        return self._getString(3)

    def setRecruitName(self, value):
        self._setString(3, value)

    def getIsBattlePassBought(self):
        return self._getBool(4)

    def setIsBattlePassBought(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(BattlePassVotingConfirmViewModel, self)._initialize()
        self._addNumberProperty('vehicleCD', 0)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('styleName', '')
        self._addStringProperty('recruitName', '')
        self._addBoolProperty('isBattlePassBought', False)
        self.onVoteClick = self._addCommand('onVoteClick')
