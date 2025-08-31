# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/user_status_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from gui.impl.gen.view_models.views.lobby.postbattle.killer_user_name_model import KillerUserNameModel

class UserStatusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(UserStatusModel, self).__init__(properties=properties, commands=commands)

    @property
    def killer(self):
        return self._getViewModel(0)

    @staticmethod
    def getKillerType():
        return KillerUserNameModel

    @property
    def user(self):
        return self._getViewModel(1)

    @staticmethod
    def getUserType():
        return UserNameModel

    def getIsLeftBattle(self):
        return self._getBool(2)

    def setIsLeftBattle(self, value):
        self._setBool(2, value)

    def getAttackReason(self):
        return self._getNumber(3)

    def setAttackReason(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(UserStatusModel, self)._initialize()
        self._addViewModelProperty('killer', KillerUserNameModel())
        self._addViewModelProperty('user', UserNameModel())
        self._addBoolProperty('isLeftBattle', False)
        self._addNumberProperty('attackReason', 0)
