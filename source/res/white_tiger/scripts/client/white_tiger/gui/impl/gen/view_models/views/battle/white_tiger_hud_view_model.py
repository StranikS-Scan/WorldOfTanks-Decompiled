# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/battle/white_tiger_hud_view_model.py
from frameworks.wulf import Array, ViewModel
from white_tiger.gui.impl.gen.view_models.views.battle.boss_status_model import BossStatusModel
from white_tiger.gui.impl.gen.view_models.views.battle.generator_status_model import GeneratorStatusModel

class WhiteTigerHudViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(WhiteTigerHudViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def boss(self):
        return self._getViewModel(0)

    @staticmethod
    def getBossType():
        return BossStatusModel

    @property
    def miniboss(self):
        return self._getViewModel(1)

    @staticmethod
    def getMinibossType():
        return BossStatusModel

    def getIsRespawning(self):
        return self._getBool(2)

    def setIsRespawning(self, value):
        self._setBool(2, value)

    def getIsEndgame(self):
        return self._getBool(3)

    def setIsEndgame(self, value):
        self._setBool(3, value)

    def getIsColorblind(self):
        return self._getBool(4)

    def setIsColorblind(self, value):
        self._setBool(4, value)

    def getIsMinibossActive(self):
        return self._getBool(5)

    def setIsMinibossActive(self, value):
        self._setBool(5, value)

    def getIsShieldDown(self):
        return self._getBool(6)

    def setIsShieldDown(self, value):
        self._setBool(6, value)

    def getShieldCooldownSeconds(self):
        return self._getNumber(7)

    def setShieldCooldownSeconds(self, value):
        self._setNumber(7, value)

    def getHyperionCharge(self):
        return self._getNumber(8)

    def setHyperionCharge(self, value):
        self._setNumber(8, value)

    def getIsAlly(self):
        return self._getBool(9)

    def setIsAlly(self, value):
        self._setBool(9, value)

    def getIsSpecialBoss(self):
        return self._getBool(10)

    def setIsSpecialBoss(self, value):
        self._setBool(10, value)

    def getGenerators(self):
        return self._getArray(11)

    def setGenerators(self, value):
        self._setArray(11, value)

    @staticmethod
    def getGeneratorsType():
        return GeneratorStatusModel

    def _initialize(self):
        super(WhiteTigerHudViewModel, self)._initialize()
        self._addViewModelProperty('boss', BossStatusModel())
        self._addViewModelProperty('miniboss', BossStatusModel())
        self._addBoolProperty('isRespawning', False)
        self._addBoolProperty('isEndgame', False)
        self._addBoolProperty('isColorblind', False)
        self._addBoolProperty('isMinibossActive', False)
        self._addBoolProperty('isShieldDown', False)
        self._addNumberProperty('shieldCooldownSeconds', 0)
        self._addNumberProperty('hyperionCharge', 0)
        self._addBoolProperty('isAlly', False)
        self._addBoolProperty('isSpecialBoss', False)
        self._addArrayProperty('generators', Array())
