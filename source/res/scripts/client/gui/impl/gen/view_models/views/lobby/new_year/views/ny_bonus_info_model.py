# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_bonus_info_model.py
from frameworks.wulf import ViewModel

class NyBonusInfoModel(ViewModel):
    __slots__ = ()
    BONUS_FREE_XP = 'freeXPFactor'
    BONUS_XP = 'xpFactor'
    BONUS_TANKMEN_XP = 'tankmenXPFactor'

    def __init__(self, properties=4, commands=0):
        super(NyBonusInfoModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getBonusType(self):
        return self._getString(1)

    def setBonusType(self, value):
        self._setString(1, value)

    def getBonusValue(self):
        return self._getNumber(2)

    def setBonusValue(self, value):
        self._setNumber(2, value)

    def getLabel(self):
        return self._getString(3)

    def setLabel(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(NyBonusInfoModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('bonusType', 'freeXPFactor')
        self._addNumberProperty('bonusValue', 0)
        self._addStringProperty('label', '')
