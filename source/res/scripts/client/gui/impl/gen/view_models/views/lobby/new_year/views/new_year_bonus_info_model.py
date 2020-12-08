# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_bonus_info_model.py
from frameworks.wulf import ViewModel

class NewYearBonusInfoModel(ViewModel):
    __slots__ = ()
    BONUS_FREE_XP = 'freeXPFactor'
    BONUS_XP = 'xpFactor'
    BONUS_TANKMEN_XP = 'tankmenXPFactor'

    def __init__(self, properties=2, commands=0):
        super(NewYearBonusInfoModel, self).__init__(properties=properties, commands=commands)

    def getBonusType(self):
        return self._getString(0)

    def setBonusType(self, value):
        self._setString(0, value)

    def getBonusValue(self):
        return self._getNumber(1)

    def setBonusValue(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NewYearBonusInfoModel, self)._initialize()
        self._addStringProperty('bonusType', 'freeXPFactor')
        self._addNumberProperty('bonusValue', 0)
