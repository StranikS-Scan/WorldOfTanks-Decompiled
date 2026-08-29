# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/tooltips/umg_reward_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class UmgRewardModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(UmgRewardModel, self).__init__(properties=properties, commands=commands)

    def getIsLocked(self):
        return self._getBool(9)

    def setIsLocked(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(UmgRewardModel, self)._initialize()
        self._addBoolProperty('isLocked', False)
