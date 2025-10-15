# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/modules_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.tooltips.bonus_parameter import BonusParameter
from portal.gui.impl.gen.view_models.views.lobby.tooltips.modules_parameters import ModulesParameters

class ItemType(Enum):
    GUN = 'vehicleGun'
    ENGINE = 'vehicleEngine'
    TURRET = 'vehicleTurret'
    HULL = 'vehicleChassis'
    DAMAGEBONUS = 'damageBonus'
    KDBONUS = 'kdBonus'
    SMALLMOBILITYBONUS = 'smallMobilityBonus'
    SMALLKDBONUS = 'smallKDBonus'


class ModuleModifier(Enum):
    DAMAGEGUN = 'damageGun'
    QUICKFIREGUN = 'quickfireGun'
    DRUMGUN = 'drumGun'
    DUALGUN = 'dualGun'
    MAGAZINERELOADINGGUN = 'magazineReloadingGun'
    FASTHULL = 'fastHull'
    HPHULL = 'hpHull'
    ARMOREDHULL = 'armoredHull'
    FASTTURRET = 'fastTurret'
    HPTURRET = 'hpTurret'
    FASTENGINE = 'fastEngine'
    POWERENGINE = 'powerEngine'


class ModulesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ModulesTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonusParameter(self):
        return self._getViewModel(0)

    @staticmethod
    def getBonusParameterType():
        return BonusParameter

    def getItemType(self):
        return ItemType(self._getString(1))

    def setItemType(self, value):
        self._setString(1, value.value)

    def getModuleModifier(self):
        return ModuleModifier(self._getString(2))

    def setModuleModifier(self, value):
        self._setString(2, value.value)

    def getModuleName(self):
        return self._getString(3)

    def setModuleName(self, value):
        self._setString(3, value)

    def getNextLevel(self):
        return self._getNumber(4)

    def setNextLevel(self, value):
        self._setNumber(4, value)

    def getIsModule(self):
        return self._getBool(5)

    def setIsModule(self, value):
        self._setBool(5, value)

    def getParameters(self):
        return self._getArray(6)

    def setParameters(self, value):
        self._setArray(6, value)

    @staticmethod
    def getParametersType():
        return ModulesParameters

    def _initialize(self):
        super(ModulesTooltipModel, self)._initialize()
        self._addViewModelProperty('bonusParameter', BonusParameter())
        self._addStringProperty('itemType')
        self._addStringProperty('moduleModifier')
        self._addStringProperty('moduleName', '')
        self._addNumberProperty('nextLevel', 0)
        self._addBoolProperty('isModule', True)
        self._addArrayProperty('parameters', Array())
