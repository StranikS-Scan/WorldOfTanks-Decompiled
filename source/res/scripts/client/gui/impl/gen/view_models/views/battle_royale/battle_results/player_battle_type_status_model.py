# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/battle_results/player_battle_type_status_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel

class BattleType(Enum):
    SOLO = 'solo'
    RANDOMPLATOON = 'randomPlatoon'
    PLATOON = 'platoon'


class PlayerBattleTypeStatusModel(ViewModel):
    __slots__ = ('onInviteToPlatoon',)

    def __init__(self, properties=3, commands=1):
        super(PlayerBattleTypeStatusModel, self).__init__(properties=properties, commands=commands)

    @property
    def user(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserType():
        return UserNameModel

    def getBattleType(self):
        return BattleType(self._getString(1))

    def setBattleType(self, value):
        self._setString(1, value.value)

    def getIsPlatoonWindowOpen(self):
        return self._getBool(2)

    def setIsPlatoonWindowOpen(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(PlayerBattleTypeStatusModel, self)._initialize()
        self._addViewModelProperty('user', UserNameModel())
        self._addStringProperty('battleType')
        self._addBoolProperty('isPlatoonWindowOpen', False)
        self.onInviteToPlatoon = self._addCommand('onInviteToPlatoon')
