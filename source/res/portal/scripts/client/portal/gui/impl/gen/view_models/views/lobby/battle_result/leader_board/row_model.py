# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/battle_result/leader_board/row_model.py
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.leader_board.user_battle_info_model import UserBattleInfoModel

class RowModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RowModel, self).__init__(properties=properties, commands=commands)

    @property
    def user(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserType():
        return UserBattleInfoModel

    def getPlace(self):
        return self._getNumber(1)

    def setPlace(self, value):
        self._setNumber(1, value)

    def getIsPersonal(self):
        return self._getBool(2)

    def setIsPersonal(self, value):
        self._setBool(2, value)

    def getIsSquadMode(self):
        return self._getBool(3)

    def setIsSquadMode(self, value):
        self._setBool(3, value)

    def getIsLeaver(self):
        return self._getBool(4)

    def setIsLeaver(self, value):
        self._setBool(4, value)

    def getSquadIndex(self):
        return self._getNumber(5)

    def setSquadIndex(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(RowModel, self)._initialize()
        self._addViewModelProperty('user', UserBattleInfoModel())
        self._addNumberProperty('place', 0)
        self._addBoolProperty('isPersonal', False)
        self._addBoolProperty('isSquadMode', False)
        self._addBoolProperty('isLeaver', False)
        self._addNumberProperty('squadIndex', 0)
