# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class WtBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(WtBonusModel, self).__init__(properties=properties, commands=commands)

    def getSpecialId(self):
        return self._getNumber(8)

    def setSpecialId(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(WtBonusModel, self)._initialize()
        self._addNumberProperty('specialId', 0)
