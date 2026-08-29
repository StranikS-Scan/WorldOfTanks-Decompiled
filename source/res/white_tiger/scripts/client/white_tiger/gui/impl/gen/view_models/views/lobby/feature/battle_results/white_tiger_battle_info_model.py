# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/feature/battle_results/white_tiger_battle_info_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.battle_info_model import BattleInfoModel

class WhiteTigerBattleInfoModel(BattleInfoModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(WhiteTigerBattleInfoModel, self).__init__(properties=properties, commands=commands)

    def getAssetsPointer(self):
        return self._getString(7)

    def setAssetsPointer(self, value):
        self._setString(7, value)

    def getSubModeAssetsPointer(self):
        return self._getString(8)

    def setSubModeAssetsPointer(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(WhiteTigerBattleInfoModel, self)._initialize()
        self._addStringProperty('assetsPointer', 'undefined')
        self._addStringProperty('subModeAssetsPointer', 'undefined')
