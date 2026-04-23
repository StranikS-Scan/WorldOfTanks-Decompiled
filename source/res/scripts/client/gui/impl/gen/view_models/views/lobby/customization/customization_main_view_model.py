# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_main_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_bill_data_model import CustomizationBillDataModel
from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_model import CustomizationCarouselModel
from gui.impl.gen.view_models.views.lobby.customization.customization_filter_model import CustomizationFilterModel
from gui.impl.gen.view_models.views.lobby.customization.customization_header_vehicle_info_model import CustomizationHeaderVehicleInfoModel
from gui.impl.gen.view_models.views.lobby.customization.customization_magnetic_tool_model import CustomizationMagneticToolModel
from gui.impl.gen.view_models.views.lobby.customization.customization_markers_model import CustomizationMarkersModel
from gui.impl.gen.view_models.views.lobby.customization.customization_seasons_model import CustomizationSeasonsModel
from gui.impl.gen.view_models.views.lobby.customization.customization_tabs_model import CustomizationTabsModel
from gui.impl.gen.view_models.views.lobby.customization.customization_toolbar_model import CustomizationToolbarModel
from gui.impl.gen.view_models.views.lobby.customization.progression_styles.stage_switcher_widget_model import StageSwitcherWidgetModel

class CustomizationMainViewModel(ViewModel):
    __slots__ = ('onClose', 'onCloseCarouselView', 'onCloseBinEsc', 'onCloseStyleInfoEsc', 'onExpandCarousel', 'onMoveSpace', 'onSelectItem', 'onUnselectItem', 'onSelectTab', 'onSelectSeason', 'onApplyToAllSeasonsChange', 'changeFilter', 'clearFilter', 'onHoverItem', 'onHoverTab', 'onClickDecalsBanner', 'onEditItem', 'onCloseEditItem', 'onSceneOverChange', 'onSceneDraggingChange', 'onSceneClick', 'onBuyItems', 'onProgressiveInfoButtonClick', 'onPressSelectNextItem', 'onRequestItems')

    def __init__(self, properties=20, commands=25):
        super(CustomizationMainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def carouselModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getCarouselModelType():
        return CustomizationCarouselModel

    @property
    def tabsModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getTabsModelType():
        return CustomizationTabsModel

    @property
    def filterModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getFilterModelType():
        return CustomizationFilterModel

    @property
    def billModel(self):
        return self._getViewModel(3)

    @staticmethod
    def getBillModelType():
        return CustomizationBillDataModel

    @property
    def seasonsModel(self):
        return self._getViewModel(4)

    @staticmethod
    def getSeasonsModelType():
        return CustomizationSeasonsModel

    @property
    def headerVehicleInfoModel(self):
        return self._getViewModel(5)

    @staticmethod
    def getHeaderVehicleInfoModelType():
        return CustomizationHeaderVehicleInfoModel

    @property
    def markersModel(self):
        return self._getViewModel(6)

    @staticmethod
    def getMarkersModelType():
        return CustomizationMarkersModel

    @property
    def toolbarModel(self):
        return self._getViewModel(7)

    @staticmethod
    def getToolbarModelType():
        return CustomizationToolbarModel

    @property
    def stageSwitcherWidgetModel(self):
        return self._getViewModel(8)

    @staticmethod
    def getStageSwitcherWidgetModelType():
        return StageSwitcherWidgetModel

    @property
    def magneticToolModel(self):
        return self._getViewModel(9)

    @staticmethod
    def getMagneticToolModelType():
        return CustomizationMagneticToolModel

    def getIsEditable(self):
        return self._getBool(10)

    def setIsEditable(self, value):
        self._setBool(10, value)

    def getIsApplyToAllSeasonsAvailable(self):
        return self._getBool(11)

    def setIsApplyToAllSeasonsAvailable(self, value):
        self._setBool(11, value)

    def getIsApplyToAllSeasonsSelected(self):
        return self._getBool(12)

    def setIsApplyToAllSeasonsSelected(self, value):
        self._setBool(12, value)

    def getIsBuyViewActive(self):
        return self._getBool(13)

    def setIsBuyViewActive(self, value):
        self._setBool(13, value)

    def getIsShowProgressionInfoButton(self):
        return self._getBool(14)

    def setIsShowProgressionInfoButton(self, value):
        self._setBool(14, value)

    def getIsStyleInfoViewActive(self):
        return self._getBool(15)

    def setIsStyleInfoViewActive(self, value):
        self._setBool(15, value)

    def getIsHoverVehicleSlot(self):
        return self._getBool(16)

    def setIsHoverVehicleSlot(self, value):
        self._setBool(16, value)

    def getIsProgressiveItemsViewVisible(self):
        return self._getBool(17)

    def setIsProgressiveItemsViewVisible(self, value):
        self._setBool(17, value)

    def getIsFilterPopoverOpened(self):
        return self._getBool(18)

    def setIsFilterPopoverOpened(self, value):
        self._setBool(18, value)

    def getIsOnboardingViewOpened(self):
        return self._getBool(19)

    def setIsOnboardingViewOpened(self, value):
        self._setBool(19, value)

    def _initialize(self):
        super(CustomizationMainViewModel, self)._initialize()
        self._addViewModelProperty('carouselModel', CustomizationCarouselModel())
        self._addViewModelProperty('tabsModel', CustomizationTabsModel())
        self._addViewModelProperty('filterModel', CustomizationFilterModel())
        self._addViewModelProperty('billModel', CustomizationBillDataModel())
        self._addViewModelProperty('seasonsModel', CustomizationSeasonsModel())
        self._addViewModelProperty('headerVehicleInfoModel', CustomizationHeaderVehicleInfoModel())
        self._addViewModelProperty('markersModel', CustomizationMarkersModel())
        self._addViewModelProperty('toolbarModel', CustomizationToolbarModel())
        self._addViewModelProperty('stageSwitcherWidgetModel', StageSwitcherWidgetModel())
        self._addViewModelProperty('magneticToolModel', CustomizationMagneticToolModel())
        self._addBoolProperty('isEditable', False)
        self._addBoolProperty('isApplyToAllSeasonsAvailable', False)
        self._addBoolProperty('isApplyToAllSeasonsSelected', False)
        self._addBoolProperty('isBuyViewActive', False)
        self._addBoolProperty('isShowProgressionInfoButton', False)
        self._addBoolProperty('isStyleInfoViewActive', False)
        self._addBoolProperty('isHoverVehicleSlot', False)
        self._addBoolProperty('isProgressiveItemsViewVisible', False)
        self._addBoolProperty('isFilterPopoverOpened', False)
        self._addBoolProperty('isOnboardingViewOpened', False)
        self.onClose = self._addCommand('onClose')
        self.onCloseCarouselView = self._addCommand('onCloseCarouselView')
        self.onCloseBinEsc = self._addCommand('onCloseBinEsc')
        self.onCloseStyleInfoEsc = self._addCommand('onCloseStyleInfoEsc')
        self.onExpandCarousel = self._addCommand('onExpandCarousel')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onSelectItem = self._addCommand('onSelectItem')
        self.onUnselectItem = self._addCommand('onUnselectItem')
        self.onSelectTab = self._addCommand('onSelectTab')
        self.onSelectSeason = self._addCommand('onSelectSeason')
        self.onApplyToAllSeasonsChange = self._addCommand('onApplyToAllSeasonsChange')
        self.changeFilter = self._addCommand('changeFilter')
        self.clearFilter = self._addCommand('clearFilter')
        self.onHoverItem = self._addCommand('onHoverItem')
        self.onHoverTab = self._addCommand('onHoverTab')
        self.onClickDecalsBanner = self._addCommand('onClickDecalsBanner')
        self.onEditItem = self._addCommand('onEditItem')
        self.onCloseEditItem = self._addCommand('onCloseEditItem')
        self.onSceneOverChange = self._addCommand('onSceneOverChange')
        self.onSceneDraggingChange = self._addCommand('onSceneDraggingChange')
        self.onSceneClick = self._addCommand('onSceneClick')
        self.onBuyItems = self._addCommand('onBuyItems')
        self.onProgressiveInfoButtonClick = self._addCommand('onProgressiveInfoButtonClick')
        self.onPressSelectNextItem = self._addCommand('onPressSelectNextItem')
        self.onRequestItems = self._addCommand('onRequestItems')
