# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/random/random_battle_info_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.battle_info_model import BattleInfoModel

class RandomBattleInfoModel(BattleInfoModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(RandomBattleInfoModel, self).__init__(properties=properties, commands=commands)

    def getFinishReason(self):
        return self._getNumber(7)

    def setFinishReason(self, value):
        self._setNumber(7, value)

    def getFinishReasonClarification(self):
        return self._getString(8)

    def setFinishReasonClarification(self, value):
        self._setString(8, value)

    def getCommendationsReceived(self):
        return self._getNumber(9)

    def setCommendationsReceived(self, value):
        self._setNumber(9, value)

    def getArenaGuiType(self):
        return self._getNumber(10)

    def setArenaGuiType(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(RandomBattleInfoModel, self)._initialize()
        self._addNumberProperty('finishReason', 0)
        self._addStringProperty('finishReasonClarification', '')
        self._addNumberProperty('commendationsReceived', 0)
        self._addNumberProperty('arenaGuiType', 0)
