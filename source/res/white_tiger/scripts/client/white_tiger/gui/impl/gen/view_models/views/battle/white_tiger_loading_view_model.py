# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/battle/white_tiger_loading_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PlayerTypeEnum(Enum):
    HUNTER = 'hunter'
    BOSS = 'boss'


class WhiteTigerLoadingViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WhiteTigerLoadingViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(0)

    def setCurrentProgress(self, value):
        self._setNumber(0, value)

    def getPlayerType(self):
        return PlayerTypeEnum(self._getString(1))

    def setPlayerType(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(WhiteTigerLoadingViewModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
        self._addStringProperty('playerType', PlayerTypeEnum.HUNTER.value)
