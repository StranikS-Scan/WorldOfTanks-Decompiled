# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/style_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class StyleBonusModel(IconBonusModel):
    __slots__ = ()
    STYLE_3D_REWARD_NAME = 'style_3d'

    def __init__(self, properties=10, commands=0):
        super(StyleBonusModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(9)

    def setId(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(StyleBonusModel, self)._initialize()
        self._addNumberProperty('id', 0)
