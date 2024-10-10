# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/vehicle_tech_tree_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.techtree.node_relation import NodeRelation
from gui.impl.gen.view_models.views.lobby.techtree.node_tech_tree_model import NodeTechTreeModel
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_custom_hints_model import TechTreeCustomHintsModel
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_nation_model import TechTreeNationModel
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_settings import TechTreeSettings
from gui.impl.gen.view_models.views.lobby.techtree.vehicle_node_data import VehicleNodeData

class VehicleTechTreeModel(ViewModel):
    __slots__ = ('onNationChange', 'goToCollectionVehicle', 'goToBlueprintView', 'buyVehicle', 'unlockVehicle', 'restoreVehicle', 'addVehicleToCompare', 'goToModulesTechTree', 'onBlueprintModeChanged', 'goToPremiumShop', 'goToNationChangeView', 'goToEarlyAccess', 'onClose')
    TECHTREE_VEHICLE_TOOLTIP = 'techtreeVehicleTooltip'
    VEHICLE_COLLECTOR_TOOLTIP = 'vehicleCollectorTooltip'
    BLUEPRINT_FRAGMENT_INFO = 'blueprintFragmentInfo'
    TECHTREE_NATION_TOOLTIP = 'techtreeNationTooltip'

    def __init__(self, properties=19, commands=13):
        super(VehicleTechTreeModel, self).__init__(properties=properties, commands=commands)

    @property
    def hints(self):
        return self._getViewModel(0)

    @staticmethod
    def getHintsType():
        return TechTreeCustomHintsModel

    @property
    def settings(self):
        return self._getViewModel(1)

    @staticmethod
    def getSettingsType():
        return TechTreeSettings

    def getAvailableNations(self):
        return self._getArray(2)

    def setAvailableNations(self, value):
        self._setArray(2, value)

    @staticmethod
    def getAvailableNationsType():
        return TechTreeNationModel

    def getSelectedNation(self):
        return self._getString(3)

    def setSelectedNation(self, value):
        self._setString(3, value)

    def getEarlyAccessNation(self):
        return self._getString(4)

    def setEarlyAccessNation(self, value):
        self._setString(4, value)

    def getIsCmpAvailable(self):
        return self._getBool(5)

    def setIsCmpAvailable(self, value):
        self._setBool(5, value)

    def getHasCollectibleVehicles(self):
        return self._getBool(6)

    def setHasCollectibleVehicles(self, value):
        self._setBool(6, value)

    def getIsBlueprintMode(self):
        return self._getBool(7)

    def setIsBlueprintMode(self, value):
        self._setBool(7, value)

    def getIsBlueprintModeEnabled(self):
        return self._getBool(8)

    def setIsBlueprintModeEnabled(self, value):
        self._setBool(8, value)

    def getUniversalBlueprintsCount(self):
        return self._getNumber(9)

    def setUniversalBlueprintsCount(self, value):
        self._setNumber(9, value)

    def getNationBlueprintsCount(self):
        return self._getNumber(10)

    def setNationBlueprintsCount(self, value):
        self._setNumber(10, value)

    def getIsEarlyAccessPaused(self):
        return self._getBool(11)

    def setIsEarlyAccessPaused(self, value):
        self._setBool(11, value)

    def getIsEarlyAccessFirstTimeShown(self):
        return self._getBool(12)

    def setIsEarlyAccessFirstTimeShown(self, value):
        self._setBool(12, value)

    def getIsParagonsEnabled(self):
        return self._getBool(13)

    def setIsParagonsEnabled(self, value):
        self._setBool(13, value)

    def getEarlyAccessCurrentTokens(self):
        return self._getNumber(14)

    def setEarlyAccessCurrentTokens(self, value):
        self._setNumber(14, value)

    def getClosePremiumPanelTrigger(self):
        return self._getReal(15)

    def setClosePremiumPanelTrigger(self, value):
        self._setReal(15, value)

    def getNodes(self):
        return self._getArray(16)

    def setNodes(self, value):
        self._setArray(16, value)

    @staticmethod
    def getNodesType():
        return NodeTechTreeModel

    def getNodesRelation(self):
        return self._getArray(17)

    def setNodesRelation(self, value):
        self._setArray(17, value)

    @staticmethod
    def getNodesRelationType():
        return NodeRelation

    def getVehiclesData(self):
        return self._getArray(18)

    def setVehiclesData(self, value):
        self._setArray(18, value)

    @staticmethod
    def getVehiclesDataType():
        return VehicleNodeData

    def _initialize(self):
        super(VehicleTechTreeModel, self)._initialize()
        self._addViewModelProperty('hints', TechTreeCustomHintsModel())
        self._addViewModelProperty('settings', TechTreeSettings())
        self._addArrayProperty('availableNations', Array())
        self._addStringProperty('selectedNation', '')
        self._addStringProperty('earlyAccessNation', '')
        self._addBoolProperty('isCmpAvailable', False)
        self._addBoolProperty('hasCollectibleVehicles', False)
        self._addBoolProperty('isBlueprintMode', False)
        self._addBoolProperty('isBlueprintModeEnabled', False)
        self._addNumberProperty('universalBlueprintsCount', 0)
        self._addNumberProperty('nationBlueprintsCount', 0)
        self._addBoolProperty('isEarlyAccessPaused', False)
        self._addBoolProperty('isEarlyAccessFirstTimeShown', False)
        self._addBoolProperty('isParagonsEnabled', False)
        self._addNumberProperty('earlyAccessCurrentTokens', 0)
        self._addRealProperty('closePremiumPanelTrigger', 0.0)
        self._addArrayProperty('nodes', Array())
        self._addArrayProperty('nodesRelation', Array())
        self._addArrayProperty('vehiclesData', Array())
        self.onNationChange = self._addCommand('onNationChange')
        self.goToCollectionVehicle = self._addCommand('goToCollectionVehicle')
        self.goToBlueprintView = self._addCommand('goToBlueprintView')
        self.buyVehicle = self._addCommand('buyVehicle')
        self.unlockVehicle = self._addCommand('unlockVehicle')
        self.restoreVehicle = self._addCommand('restoreVehicle')
        self.addVehicleToCompare = self._addCommand('addVehicleToCompare')
        self.goToModulesTechTree = self._addCommand('goToModulesTechTree')
        self.onBlueprintModeChanged = self._addCommand('onBlueprintModeChanged')
        self.goToPremiumShop = self._addCommand('goToPremiumShop')
        self.goToNationChangeView = self._addCommand('goToNationChangeView')
        self.goToEarlyAccess = self._addCommand('goToEarlyAccess')
        self.onClose = self._addCommand('onClose')
