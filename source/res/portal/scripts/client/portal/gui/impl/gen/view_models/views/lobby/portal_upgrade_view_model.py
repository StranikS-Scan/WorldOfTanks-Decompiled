# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_upgrade_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.portal_research_tree import PortalResearchTree
from portal.gui.impl.gen.view_models.views.lobby.portal_ttx_item_model import PortalTtxItemModel
from portal.gui.impl.gen.view_models.views.lobby.portal_upgrade_vehicle_item_model import PortalUpgradeVehicleItemModel

class PortalUpgradeViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutImprovements', 'onReset', 'onNodeSelect', 'onNodeReset', 'onMoveSpace', 'onStartMoving', 'onNodeUpgrade', 'onNextVehicleClick', 'onPrevVehicleClick', 'onStageHovered')

    def __init__(self, properties=7, commands=11):
        super(PortalUpgradeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentVehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentVehicleType():
        return PortalUpgradeVehicleItemModel

    def getTtx(self):
        return self._getArray(1)

    def setTtx(self, value):
        self._setArray(1, value)

    @staticmethod
    def getTtxType():
        return PortalTtxItemModel

    def getResearchTree(self):
        return self._getArray(2)

    def setResearchTree(self, value):
        self._setArray(2, value)

    @staticmethod
    def getResearchTreeType():
        return PortalResearchTree

    def getIncompatibleModules(self):
        return self._getArray(3)

    def setIncompatibleModules(self, value):
        self._setArray(3, value)

    @staticmethod
    def getIncompatibleModulesType():
        return unicode

    def getUpgradeAvailable(self):
        return self._getBool(4)

    def setUpgradeAvailable(self, value):
        self._setBool(4, value)

    def getIsFirstEnter(self):
        return self._getBool(5)

    def setIsFirstEnter(self, value):
        self._setBool(5, value)

    def getIsMaxLevelAchieved(self):
        return self._getBool(6)

    def setIsMaxLevelAchieved(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(PortalUpgradeViewModel, self)._initialize()
        self._addViewModelProperty('currentVehicle', PortalUpgradeVehicleItemModel())
        self._addArrayProperty('ttx', Array())
        self._addArrayProperty('researchTree', Array())
        self._addArrayProperty('incompatibleModules', Array())
        self._addBoolProperty('upgradeAvailable', False)
        self._addBoolProperty('isFirstEnter', False)
        self._addBoolProperty('isMaxLevelAchieved', False)
        self.onClose = self._addCommand('onClose')
        self.onAboutImprovements = self._addCommand('onAboutImprovements')
        self.onReset = self._addCommand('onReset')
        self.onNodeSelect = self._addCommand('onNodeSelect')
        self.onNodeReset = self._addCommand('onNodeReset')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onStartMoving = self._addCommand('onStartMoving')
        self.onNodeUpgrade = self._addCommand('onNodeUpgrade')
        self.onNextVehicleClick = self._addCommand('onNextVehicleClick')
        self.onPrevVehicleClick = self._addCommand('onPrevVehicleClick')
        self.onStageHovered = self._addCommand('onStageHovered')
