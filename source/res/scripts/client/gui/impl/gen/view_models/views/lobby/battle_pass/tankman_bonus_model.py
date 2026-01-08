# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tankman_bonus_model.py
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class TankmanBonusModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(TankmanBonusModel, self).__init__(properties=properties, commands=commands)

    def getWithUniqueVoice(self):
        return self._getBool(15)

    def setWithUniqueVoice(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(TankmanBonusModel, self)._initialize()
        self._addBoolProperty('withUniqueVoice', False)
