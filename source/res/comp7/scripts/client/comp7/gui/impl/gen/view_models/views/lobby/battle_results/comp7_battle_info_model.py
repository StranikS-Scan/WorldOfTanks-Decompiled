# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/battle_results/comp7_battle_info_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_battle_info_model import RandomBattleInfoModel

class Comp7BattleInfoModel(RandomBattleInfoModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(Comp7BattleInfoModel, self).__init__(properties=properties, commands=commands)

    def getIsLeave(self):
        return self._getBool(11)

    def setIsLeave(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(Comp7BattleInfoModel, self)._initialize()
        self._addBoolProperty('isLeave', False)
