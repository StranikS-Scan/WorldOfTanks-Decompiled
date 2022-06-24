# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/battle_results/leaderboard/row_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel

class RowModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RowModel, self).__init__(properties=properties, commands=commands)

    @property
    def user(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserType():
        return UserNameModel

    def getPlace(self):
        return self._getString(1)

    def setPlace(self, value):
        self._setString(1, value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def getAnonymizerNick(self):
        return self._getString(3)

    def setAnonymizerNick(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(RowModel, self)._initialize()
        self._addViewModelProperty('user', UserNameModel())
        self._addStringProperty('place', '')
        self._addStringProperty('type', 'rowBrEnemy')
        self._addStringProperty('anonymizerNick', '')
