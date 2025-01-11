# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/vehicle_tech_tree_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.paragons_entry_point_view_model import ParagonsEntryPointViewModel
from gui.impl.gen.view_models.views.lobby.techtree.node_relation import NodeRelation
from gui.impl.gen.view_models.views.lobby.techtree.node_tech_tree_model import NodeTechTreeModel
from gui.impl.gen.view_models.views.lobby.techtree.paragons_unlocked_branch import ParagonsUnlockedBranch
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_buttons import TechTreeButtons
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_custom_hints_model import TechTreeCustomHintsModel
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_nation_model import TechTreeNationModel
from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_settings import TechTreeSettings
from gui.impl.gen.view_models.views.lobby.techtree.vehicle_node_data import VehicleNodeData

class VehicleTechTreeModel(ViewModel):
    __slots__ = ('onNationChange', 'goToCollectionVehicle', 'goToBlueprintView', 'buyVehicle', 'unlockVehicle', 'restoreVehicle', 'addVehicleToCompare', 'goToModulesTechTree', 'onBlueprintModeChanged', 'goToPremiumShop', 'goToNationChangeView', 'goToEarlyAccess', 'onTechTreeButtonPressed', 'onClose', 'onParagonsUnlockedBranchShown', 'onResetBranchShown')
    TECHTREE_VEHICLE_TOOLTIP = 'techtreeVehicleTooltip'
    VEHICLE_COLLECTOR_TOOLTIP = 'vehicleCollectorTooltip'
    BLUEPRINT_FRAGMENT_INFO = 'blueprintFragmentInfo'
    TECHTREE_NATION_TOOLTIP = 'techtreeNationTooltip'

    def __init__(self, properties=23, commands=16):
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

    @property
    def paragonsEntryPoint(self):
        return self._getViewModel(2)

    @staticmethod
    def getParagonsEntryPointType():
        return ParagonsEntryPointViewModel

    def getAvailableNations(self):
        return self._getArray(3)

    def setAvailableNations(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAvailableNationsType():
        return TechTreeNationModel

    def getSelectedNation(self):
        return self._getString(4)

    def setSelectedNation(self, value):
        self._setString(4, value)

    def getEarlyAccessNation(self):
        return self._getString(5)

    def setEarlyAccessNation(self, value):
        self._setString(5, value)

    def getIsCmpAvailable(self):
        return self._getBool(6)

    def setIsCmpAvailable(self, value):
        self._setBool(6, value)

    def getHasCollectibleVehicles(self):
        return self._getBool(7)

    def setHasCollectibleVehicles(self, value):
        self._setBool(7, value)

    def getIsBlueprintMode(self):
        return self._getBool(8)

    def setIsBlueprintMode(self, value):
        self._setBool(8, value)

    def getIsBlueprintModeEnabled(self):
        return self._getBool(9)

    def setIsBlueprintModeEnabled(self, value):
        self._setBool(9, value)

    def getUniversalBlueprintsCount(self):
        return self._getNumber(10)

    def setUniversalBlueprintsCount(self, value):
        self._setNumber(10, value)

    def getNationBlueprintsCount(self):
        return self._getNumber(11)

    def setNationBlueprintsCount(self, value):
        self._setNumber(11, value)

    def getIsEarlyAccessPaused(self):
        return self._getBool(12)

    def setIsEarlyAccessPaused(self, value):
        self._setBool(12, value)

    def getIsEarlyAccessFirstTimeShown(self):
        return self._getBool(13)

    def setIsEarlyAccessFirstTimeShown(self, value):
        self._setBool(13, value)

    def getIsParagonsResetBranchNeedToShow(self):
        return self._getBool(14)

    def setIsParagonsResetBranchNeedToShow(self, value):
        self._setBool(14, value)

    def getIsParagonsEnabled(self):
        return self._getBool(15)

    def setIsParagonsEnabled(self, value):
        self._setBool(15, value)

    def getEarlyAccessCurrentTokens(self):
        return self._getNumber(16)

    def setEarlyAccessCurrentTokens(self, value):
        self._setNumber(16, value)

    def getClosePremiumPanelTrigger(self):
        return self._getReal(17)

    def setClosePremiumPanelTrigger(self, value):
        self._setReal(17, value)

    def getNodes(self):
        return self._getArray(18)

    def setNodes(self, value):
        self._setArray(18, value)

    @staticmethod
    def getNodesType():
        return NodeTechTreeModel

    def getNodesRelation(self):
        return self._getArray(19)

    def setNodesRelation(self, value):
        self._setArray(19, value)

    @staticmethod
    def getNodesRelationType():
        return NodeRelation

    def getVehiclesData(self):
        return self._getArray(20)

    def setVehiclesData(self, value):
        self._setArray(20, value)

    @staticmethod
    def getVehiclesDataType():
        return VehicleNodeData

    def getParagonsUnlockedBranchesToShow(self):
        return self._getArray(21)

    def setParagonsUnlockedBranchesToShow(self, value):
        self._setArray(21, value)

    @staticmethod
    def getParagonsUnlockedBranchesToShowType():
        return ParagonsUnlockedBranch

    def getTechTreeButtons(self):
        return self._getArray(22)

    def setTechTreeButtons(self, value):
        self._setArray(22, value)

    @staticmethod
    def getTechTreeButtonsType():
        return TechTreeButtons

    def _initialize(self):
        super(VehicleTechTreeModel, self)._initialize()
        self._addViewModelProperty('hints', TechTreeCustomHintsModel())
        self._addViewModelProperty('settings', TechTreeSettings())
        self._addViewModelProperty('paragonsEntryPoint', ParagonsEntryPointViewModel())
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
        self._addBoolProperty('isParagonsResetBranchNeedToShow', False)
        self._addBoolProperty('isParagonsEnabled', False)
        self._addNumberProperty('earlyAccessCurrentTokens', 0)
        self._addRealProperty('closePremiumPanelTrigger', 0.0)
        self._addArrayProperty('nodes', Array())
        self._addArrayProperty('nodesRelation', Array())
        self._addArrayProperty('vehiclesData', Array())
        self._addArrayProperty('paragonsUnlockedBranchesToShow', Array())
        self._addArrayProperty('techTreeButtons', Array())
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
        self.onTechTreeButtonPressed = self._addCommand('onTechTreeButtonPressed')
        self.onClose = self._addCommand('onClose')
        self.onParagonsUnlockedBranchShown = self._addCommand('onParagonsUnlockedBranchShown')
        self.onResetBranchShown = self._addCommand('onResetBranchShown')
