# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/abilities_stage_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ItemType(Enum):
    GUN = 'gun'
    ENGINE = 'engine'
    TOWER = 'tower'
    HULL = 'hull'
    DAMADGEBONUS = 'damadgeBonus'
    KDBONUS = 'kdBonus'
    SMALLMOBILITYBONUS = 'smallMobilityBonus'
    SMALLKDBONUS = 'smallKDBonus'


class ModuleModifier(Enum):
    DAMADGEGUN = 'damadgeGun'
    QUICKFIRERGUN = 'quickfirerGun'
    DRUMGUN = 'drumGun'
    DUALGUN = 'dualGun'
    MAGAZINERELOADINGGUN = 'magazineReloadingGun'
    FASTHULL = 'fastHull'
    HPHULL = 'hpHull'
    ARMOREDHULL = 'armoredHull'
    FASTTOWER = 'fastTower'
    HPTOWER = 'hpTower'
    FASTENGINE = 'fastEngine'
    POWERENGINE = 'powerEngine'


class NodeType(Enum):
    MODULE = 'module'
    BONUS = 'bonus'
    ABILITY = 'ability'


class AbilitiesStageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(AbilitiesStageModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getItemType(self):
        return ItemType(self._getString(2))

    def setItemType(self, value):
        self._setString(2, value.value)

    def getModuleModifier(self):
        return ModuleModifier(self._getString(3))

    def setModuleModifier(self, value):
        self._setString(3, value.value)

    def getNodeType(self):
        return NodeType(self._getString(4))

    def setNodeType(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(AbilitiesStageModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('itemType')
        self._addStringProperty('moduleModifier')
        self._addStringProperty('nodeType')
