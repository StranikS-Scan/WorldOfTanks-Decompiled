# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/node_stage_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class NodeStatus(Enum):
    LOCKED = 'locked'
    AVAILABLE = 'available'
    NOT_ENOUGH_POINTS = 'notEnoughPoints'
    LEARNED = 'learned'
    NEED_TO_LEARN = 'needToLearn'
    SKIPPED = 'skipped'


class ItemType(Enum):
    GUN = 'vehicleGun'
    ENGINE = 'vehicleEngine'
    TURRET = 'vehicleTurret'
    HULL = 'vehicleChassis'
    DAMAGEBONUS = 'damageBonus'
    KDBONUS = 'kdBonus'
    SMALLMOBILITYBONUS = 'smallMobilityBonus'
    SMALLKDBONUS = 'smallKDBonus'
    NONE = 'none'


class ItemModifier(Enum):
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
    NONE = 'none'


class NodeType(Enum):
    MODULE = 'module'
    VEHICLEMODIFIER = 'vehicleModifier'
    ABILITY = 'ability'


class NodeStageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NodeStageModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getPointsToOpen(self):
        return self._getNumber(2)

    def setPointsToOpen(self, value):
        self._setNumber(2, value)

    def getItemType(self):
        return ItemType(self._getString(3))

    def setItemType(self, value):
        self._setString(3, value.value)

    def getItemModifier(self):
        return ItemModifier(self._getString(4))

    def setItemModifier(self, value):
        self._setString(4, value.value)

    def getNodeType(self):
        return NodeType(self._getString(5))

    def setNodeType(self, value):
        self._setString(5, value.value)

    def getNodeStatus(self):
        return NodeStatus(self._getString(6))

    def setNodeStatus(self, value):
        self._setString(6, value.value)

    def _initialize(self):
        super(NodeStageModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addNumberProperty('pointsToOpen', 0)
        self._addStringProperty('itemType')
        self._addStringProperty('itemModifier')
        self._addStringProperty('nodeType')
        self._addStringProperty('nodeStatus')
