# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_main_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_main_view_model import NewYearMainViewModel
from gui.impl.gui_decorators import trackLifeCycle
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.views.tabs_controller import NewYearMainTabsController
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.tooltips.new_year_collections_tooltip_content import NewYearCollectionsTooltipContent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from gui.shared.events import LobbyHeaderMenuEvent
from helpers import dependency
from items.components.ny_constants import TOKEN_FREE_TALISMANS
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, ICustomizableObjectsManager
from new_year.ny_constants import NyWidgetTopMenu
from new_year.custom_selectable_logic import PianoSelectableLogic
_NAVIGATION_ALIAS_VIEWS = {NyWidgetTopMenu.GLADE: ViewAliases.GLADE_VIEW,
 NyWidgetTopMenu.DECORATIONS: ViewAliases.CRAFT_VIEW,
 NyWidgetTopMenu.COLLECTIONS: ViewAliases.ALBUM_VIEW,
 NyWidgetTopMenu.INFO: ViewAliases.INFO_VIEW,
 NyWidgetTopMenu.REWARDS: ViewAliases.REWARDS_VIEW,
 NyWidgetTopMenu.SHARDS: ViewAliases.BREAK_VIEW}

@trackLifeCycle('new_year.main_view')
class NewYearMainView(NewYearHistoryNavigation):
    __slots__ = ('_mainTabs', '__selectableLogic')
    _settingsCore = dependency.descriptor(ISettingsCore)
    _nyController = dependency.descriptor(INewYearController)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = NewYearMainViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearMainView, self).__init__(settings)
        self._mainTabs = NewYearMainTabsController()
        self.__selectableLogic = None
        return

    @property
    def viewModel(self):
        return super(NewYearMainView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        return NewYearCollectionsTooltipContent() if contentID == R.views.lobby.new_year.tooltips.new_year_collections_tooltip_content.NYCollectionsTooltipContent() else None

    def switchView(self, loadingViewParams=None, *args, **kwargs):
        if loadingViewParams is not None:
            self.__setContent(loadingViewParams, self.viewModel, *args, **kwargs)
            self.viewModel.setStartIndexMenu(self._mainTabs.tabOrderKey(loadingViewParams.menuName))
        return

    def _initialize(self, loadingViewParams=None, *args, **kwargs):
        soundConfig = {}
        self._tabCache.clear()
        super(NewYearMainView, self)._initialize(soundConfig)
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onSwitchContent += self.__onSwitchContent
        self._nyController.onDataUpdated += self.__onDataUpdated
        self._nyController.onStateChanged += self.__onStateChanged
        self._hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensChanged})
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)
        with self.viewModel.transaction() as tx:
            self.__updateMenu(tx)
        self.switchView(loadingViewParams, *args, **kwargs)
        self.__selectableLogic = PianoSelectableLogic()
        self.__selectableLogic.init()

    def _finalize(self):
        if self.__selectableLogic is not None:
            self.__selectableLogic.fini()
            self.__selectableLogic = None
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onSwitchContent -= self.__onSwitchContent
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._nyController.onStateChanged -= self.__onStateChanged
        self._hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        g_clientUpdateManager.removeCallback('tokens', self.__onTokensChanged)
        if self.getCurrentObject() is not None:
            self._resetObject()
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        self._navigationHistory.clear()
        super(NewYearMainView, self)._finalize()
        return

    def __onCloseBtnClick(self, *_):
        self.closeMainView()

    def __onSwitchContent(self, args):
        viewName = args['view']
        self._navigationHistory.clear()
        self._goToByViewAlias(_NAVIGATION_ALIAS_VIEWS.get(viewName), saveHistory=False)

    def __onDataUpdated(self, *_):
        with self.viewModel.transaction() as tx:
            self.__updateMenu(tx)

    def __onTokensChanged(self, tokens):
        if TOKEN_FREE_TALISMANS in tokens:
            with self.viewModel.transaction() as tx:
                self.__updateMenu(tx)

    def __updateMenu(self, model):
        for tabController, arrayModel in self.__getMenuList(model):
            tabController.updateTabModels(arrayModel)

    def __getMenuList(self, model):
        return ((self._mainTabs, model.getItemsMenu()),)

    def __setContent(self, loadingViewParams, model, *args, **kwargs):
        self.setChildView(R.dynamic_ids.newYearMainView(), loadingViewParams.className(*args, **kwargs))
        model.setCurrentView(loadingViewParams.menuName)

    def __onStateChanged(self):
        if not self._nyController.isEnabled():
            if not self._app.fadeManager.isInFade():
                self.closeMainView()
            else:
                showHangar()

    def __onSpaceDestroy(self, _):
        self.closeMainView()
