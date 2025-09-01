# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/veh_skill_tree/tree_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.node_model import NodeModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.path_model import PathModel

class ResearchAvailability(Enum):
    NOT_IN_INVENTORY = 'notInInventory'
    NOT_ENOUGH_EXP = 'notEnoughExp'
    IN_BATTLE = 'inBattle'
    IN_FORMATION = 'inFormation'
    NEEDS_REPAIR = 'needsRepair'
    AVAILABLE = 'researchAvailable'


class TreeViewModel(ViewModel):
    __slots__ = ('onResearch', 'onShowNodeConfigurationWindow', 'onSelectNode', 'onFinalNodeResearchAnimationFinished')

    def __init__(self, properties=9, commands=4):
        super(TreeViewModel, self).__init__(properties=properties, commands=commands)

    def getResearchedPerks(self):
        return self._getArray(0)

    def setResearchedPerks(self, value):
        self._setArray(0, value)

    @staticmethod
    def getResearchedPerksType():
        return int

    def getNodes(self):
        return self._getArray(1)

    def setNodes(self, value):
        self._setArray(1, value)

    @staticmethod
    def getNodesType():
        return NodeModel

    def getPaths(self):
        return self._getArray(2)

    def setPaths(self, value):
        self._setArray(2, value)

    @staticmethod
    def getPathsType():
        return Array[PathModel]

    def getRootNodeId(self):
        return self._getNumber(3)

    def setRootNodeId(self, value):
        self._setNumber(3, value)

    def getRootNodeUiId(self):
        return self._getNumber(4)

    def setRootNodeUiId(self, value):
        self._setNumber(4, value)

    def getResearchAvailability(self):
        return ResearchAvailability(self._getString(5))

    def setResearchAvailability(self, value):
        self._setString(5, value.value)

    def getLockedTree(self):
        return self._getBool(6)

    def setLockedTree(self, value):
        self._setBool(6, value)

    def getIsProgressionCompleted(self):
        return self._getBool(7)

    def setIsProgressionCompleted(self, value):
        self._setBool(7, value)

    def getIsPrestigeGlareShown(self):
        return self._getBool(8)

    def setIsPrestigeGlareShown(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(TreeViewModel, self)._initialize()
        self._addArrayProperty('researchedPerks', Array())
        self._addArrayProperty('nodes', Array())
        self._addArrayProperty('paths', Array())
        self._addNumberProperty('rootNodeId', 0)
        self._addNumberProperty('rootNodeUiId', 0)
        self._addStringProperty('researchAvailability')
        self._addBoolProperty('lockedTree', False)
        self._addBoolProperty('isProgressionCompleted', False)
        self._addBoolProperty('isPrestigeGlareShown', False)
        self.onResearch = self._addCommand('onResearch')
        self.onShowNodeConfigurationWindow = self._addCommand('onShowNodeConfigurationWindow')
        self.onSelectNode = self._addCommand('onSelectNode')
        self.onFinalNodeResearchAnimationFinished = self._addCommand('onFinalNodeResearchAnimationFinished')
