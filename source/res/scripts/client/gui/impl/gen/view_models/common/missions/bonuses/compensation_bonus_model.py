# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/compensation_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class CompensationBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(CompensationBonusModel, self).__init__(properties=properties, commands=commands)

    @property
    def compensatedItem(self):
        return self._getViewModel(7)

    def _initialize(self):
        super(CompensationBonusModel, self)._initialize()
        self._addViewModelProperty('compensatedItem', BonusModel())
