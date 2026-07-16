# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/battle_results/comp7_light_battle_info_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_battle_info_model import RandomBattleInfoModel

class Comp7LightBattleInfoModel(RandomBattleInfoModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(Comp7LightBattleInfoModel, self).__init__(properties=properties, commands=commands)

    def getIsLeave(self):
        return self._getBool(11)

    def setIsLeave(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(Comp7LightBattleInfoModel, self)._initialize()
        self._addBoolProperty('isLeave', False)
