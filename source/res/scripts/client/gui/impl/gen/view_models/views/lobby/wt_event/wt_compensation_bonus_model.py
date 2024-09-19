# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_compensation_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class WtCompensationBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(WtCompensationBonusModel, self).__init__(properties=properties, commands=commands)

    def getCompensationSource(self):
        return self._getString(8)

    def setCompensationSource(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(WtCompensationBonusModel, self)._initialize()
        self._addStringProperty('compensationSource', '')
