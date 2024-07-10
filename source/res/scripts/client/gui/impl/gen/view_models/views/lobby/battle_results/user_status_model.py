# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/user_status_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel

class UserStatusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(UserStatusModel, self).__init__(properties=properties, commands=commands)

    @property
    def killer(self):
        return self._getViewModel(0)

    @staticmethod
    def getKillerType():
        return UserNameModel

    def getIsLeftBattle(self):
        return self._getBool(1)

    def setIsLeftBattle(self, value):
        self._setBool(1, value)

    def getDeathReason(self):
        return self._getNumber(2)

    def setDeathReason(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(UserStatusModel, self)._initialize()
        self._addViewModelProperty('killer', UserNameModel())
        self._addBoolProperty('isLeftBattle', False)
        self._addNumberProperty('deathReason', 0)
