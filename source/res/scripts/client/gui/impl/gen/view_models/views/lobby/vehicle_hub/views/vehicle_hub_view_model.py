# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/vehicle_hub_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_model import ArmorModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.comparison_model import ComparisonModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.menu_item_model import MenuItemModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.modules_model import ModulesModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.overview_model import OverviewModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.research_purchase_model import ResearchPurchaseModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.stats_model import StatsModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree_model import VehSkillTreeModel

class VehicleHubViewModel(ViewModel):
    __slots__ = ('onMoveSpace', 'onMouseOver3dScene')
    OVERVIEW = 'overview'
    MODULES = 'modules'
    VEH_SKILL_TREE = 'vehSkillTree'
    STATS = 'stats'
    ARMOR = 'armor'

    def __init__(self, properties=10, commands=2):
        super(VehicleHubViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def router(self):
        return self._getViewModel(0)

    @staticmethod
    def getRouterType():
        return RouterModel

    @property
    def vehicleInfoModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleInfoModelType():
        return VehicleInfoModel

    @property
    def comparisonModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getComparisonModelType():
        return ComparisonModel

    @property
    def overviewModel(self):
        return self._getViewModel(3)

    @staticmethod
    def getOverviewModelType():
        return OverviewModel

    @property
    def modulesModel(self):
        return self._getViewModel(4)

    @staticmethod
    def getModulesModelType():
        return ModulesModel

    @property
    def vehSkillTreeModel(self):
        return self._getViewModel(5)

    @staticmethod
    def getVehSkillTreeModelType():
        return VehSkillTreeModel

    @property
    def statsModel(self):
        return self._getViewModel(6)

    @staticmethod
    def getStatsModelType():
        return StatsModel

    @property
    def armorModel(self):
        return self._getViewModel(7)

    @staticmethod
    def getArmorModelType():
        return ArmorModel

    @property
    def researchPurchaseModel(self):
        return self._getViewModel(8)

    @staticmethod
    def getResearchPurchaseModelType():
        return ResearchPurchaseModel

    def getMenuItems(self):
        return self._getArray(9)

    def setMenuItems(self, value):
        self._setArray(9, value)

    @staticmethod
    def getMenuItemsType():
        return MenuItemModel

    def _initialize(self):
        super(VehicleHubViewModel, self)._initialize()
        self._addViewModelProperty('router', RouterModel())
        self._addViewModelProperty('vehicleInfoModel', VehicleInfoModel())
        self._addViewModelProperty('comparisonModel', ComparisonModel())
        self._addViewModelProperty('overviewModel', OverviewModel())
        self._addViewModelProperty('modulesModel', ModulesModel())
        self._addViewModelProperty('vehSkillTreeModel', VehSkillTreeModel())
        self._addViewModelProperty('statsModel', StatsModel())
        self._addViewModelProperty('armorModel', ArmorModel())
        self._addViewModelProperty('researchPurchaseModel', ResearchPurchaseModel())
        self._addArrayProperty('menuItems', Array())
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
