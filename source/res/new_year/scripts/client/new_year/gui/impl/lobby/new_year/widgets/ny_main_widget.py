# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/widgets/ny_main_widget.py
from new_year.gui.impl.lobby.new_year.tooltips.ny_main_widget_tooltip import NyMainWidgetTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_total_bonus_tooltip import NyTotalBonusTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_pet_overview_tooltip import NyPetOverviewTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_block_activities_tooltip import NyBlockActivitiesTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_common_tooltip import NyCommonTooltip, getCommonTooltipArgsFromEvent
from new_year.gui.impl.lobby.new_year.widgets.ny_widget_handler import NyWidgetHandler
from new_year.gui.impl.new_year.sound_rtpc_controller import SoundRTPCController
from new_year.gui.impl.new_year.sounds import NewYearSoundsManager
from new_year.ny_constants import SyncDataKeys
from new_year.skeletons.new_year import INewYearController, ITamagotchiDataProvider
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_model import NewYearMainWidgetModel
from new_year.ny_constants import ViewAliases
from gui.impl.pub import ViewImpl
from helpers import dependency
from new_year_common.items.components.ny_constants import NewYearObjects
from skeletons.gui.shared import IItemsCache
_EXTENDED_RENDER_PIPELINE = 0

class NyMainWidgetInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return NyMainWidget()


class NyMainWidget(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self):
        settings = ViewSettings(R.views.new_year.lobby.new_year.NyMainWidget())
        settings.flags = ViewFlags.VIEW
        settings.model = NewYearMainWidgetModel()
        super(NyMainWidget, self).__init__(settings)
        self.__soundManager = NewYearSoundsManager({})
        self.__soundRTPCController = None
        self.__wigetHandler = NyWidgetHandler(self.viewModel)
        return

    @property
    def viewModel(self):
        return super(NyMainWidget, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.new_year.lobby.new_year.tooltips.NyMainWidgetTooltip():
            return NyMainWidgetTooltip(event.getArgument('block'))
        elif event.contentID == R.views.new_year.lobby.new_year.tooltips.NyTotalBonusTooltip():
            return NyTotalBonusTooltip()
        elif event.contentID == R.views.new_year.lobby.new_year.tooltips.NyPetOverviewTooltip():
            return NyPetOverviewTooltip()
        elif event.contentID == R.views.new_year.lobby.new_year.tooltips.NyBlockActivitiesTooltip():
            return NyBlockActivitiesTooltip()
        else:
            return NyCommonTooltip(*getCommonTooltipArgsFromEvent(event)) if contentID == R.views.new_year.lobby.new_year.tooltips.CommonTooltip() else None

    def _initialize(self):
        super(NyMainWidget, self)._initialize()
        self._nyController.onDataUpdated += self.__onDataUpdated
        NewYearNavigation.onObjectStateChanged += self.__onObjectStateChanged
        self.__soundRTPCController = SoundRTPCController()
        self.__soundRTPCController.init(NewYearNavigation.getCurrentObject())
        self.__soundRTPCController.setLevelAtmosphere(self._itemsCache.items.festivity.getMaxLevel())
        self.__wigetHandler.initialize()
        self.viewModel.setIsInited(True)

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onWidgetClick), (self.viewModel.onPetClick, self.__onPetClick))

    def _finalize(self):
        if self.__soundRTPCController is not None:
            self.__soundRTPCController.fini()
            self.__soundRTPCController = None
        self.__soundManager.clear()
        self.viewModel.onClick -= self.__onWidgetClick
        self._nyController.onDataUpdated -= self.__onDataUpdated
        NewYearNavigation.onObjectStateChanged -= self.__onObjectStateChanged
        self.__wigetHandler.finalize()
        super(NyMainWidget, self)._finalize()
        return

    def getLobbyMode(self, *_):
        return self.__wigetHandler.lobbyMode

    def __onWidgetClick(self, *_):
        NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW)

    def __onPetClick(self, *_):
        if self._dataProvider.raccoonState:
            NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW, viewAlias=ViewAliases.PET_VIEW, isLoadedFromHangar=False, instantly=True)
        else:
            NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW)

    def __onDataUpdated(self, keys):
        if SyncDataKeys.POINTS in keys:
            self.__wigetHandler.update()

    def __onObjectStateChanged(self):
        currentObject = NewYearNavigation.getCurrentObject()
        self.__soundRTPCController.setCurrentLocation(currentObject)
