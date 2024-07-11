# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/big_icon_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class BigIconBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(BigIconBonusModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(7)

    def setIcon(self, value):
        self._setString(7, value)

    def getBigIcon(self):
        return self._getString(8)

    def setBigIcon(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(BigIconBonusModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addStringProperty('bigIcon', '')
