# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/icon_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class IconBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(IconBonusModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(6)

    def setIcon(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(IconBonusModel, self)._initialize()
        self._addStringProperty('icon', '')
