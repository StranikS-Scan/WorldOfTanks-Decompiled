# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/battle_result_view/row_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.user_battle_info_model import UserBattleInfoModel

class RowModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RowModel, self).__init__(properties=properties, commands=commands)

    @property
    def user(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserType():
        return UserBattleInfoModel

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getAnonymizerNick(self):
        return self._getString(2)

    def setAnonymizerNick(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(RowModel, self)._initialize()
        self._addViewModelProperty('user', UserBattleInfoModel())
        self._addStringProperty('type', 'rowBrEnemy')
        self._addStringProperty('anonymizerNick', '')
