# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_random_battle_info_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.battle_info_model import BattleInfoModel

class FunRandomBattleInfoModel(BattleInfoModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(FunRandomBattleInfoModel, self).__init__(properties=properties, commands=commands)

    def getAssetsPointer(self):
        return self._getString(6)

    def setAssetsPointer(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(FunRandomBattleInfoModel, self)._initialize()
        self._addStringProperty('assetsPointer', 'undefined')
