# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/token_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class TokenBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(TokenBonusModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(7)

    def setUserName(self, value):
        self._setString(7, value)

    def getIconSmall(self):
        return self._getString(8)

    def setIconSmall(self, value):
        self._setString(8, value)

    def getIconBig(self):
        return self._getString(9)

    def setIconBig(self, value):
        self._setString(9, value)

    def getIcon(self):
        return self._getString(10)

    def setIcon(self, value):
        self._setString(10, value)

    def getTankType(self):
        return self._getString(11)

    def setTankType(self, value):
        self._setString(11, value)

    def getTankUserName(self):
        return self._getString(12)

    def setTankUserName(self, value):
        self._setString(12, value)

    def getTankLevel(self):
        return self._getNumber(13)

    def setTankLevel(self, value):
        self._setNumber(13, value)

    def getDiscountPercent(self):
        return self._getNumber(14)

    def setDiscountPercent(self, value):
        self._setNumber(14, value)

    def _initialize(self):
        super(TokenBonusModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addStringProperty('iconSmall', '')
        self._addStringProperty('iconBig', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('tankType', '')
        self._addStringProperty('tankUserName', '')
        self._addNumberProperty('tankLevel', 0)
        self._addNumberProperty('discountPercent', 0)
