# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/new_year/ny_menu_component.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_CELEBRITY_CHALLENGE_VISITED, NY_CELEBRITY_QUESTS_VISITED_MASK, NY_OLD_COLLECTIONS_BY_YEAR_VISITED, NY_OLD_COLLECTIONS_VISITED
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.new_year import InjectWithContext
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundsManager
from gui.impl.new_year.tooltips.new_year_collections_tooltip_content import NewYearCollectionsTooltipContent
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.views.tabs_controller import NewYearMainTabsController
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers import isMemoryRiskySystem
from items.components.ny_constants import TOKEN_FREE_TALISMANS, CelebrityQuestTokenParts
from new_year.ny_constants import NyWidgetTopMenu, AdditionalCameraObject
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
if typing.TYPE_CHECKING:
    from gui.impl.new_year.views.tabs_controller import TabsController
    from gui.shared.event_dispatcher import NYViewCtx
_NAVIGATION_ALIAS_VIEWS = {NyWidgetTopMenu.GLADE: ViewAliases.GLADE_VIEW,
 NyWidgetTopMenu.DECORATIONS: ViewAliases.CRAFT_VIEW,
 NyWidgetTopMenu.COLLECTIONS: ViewAliases.ALBUM_VIEW,
 NyWidgetTopMenu.INFO: ViewAliases.INFO_VIEW,
 NyWidgetTopMenu.REWARDS: ViewAliases.REWARDS_VIEW,
 NyWidgetTopMenu.SHARDS: ViewAliases.BREAK_VIEW}
_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {NyWidgetTopMenu.GLADE: NewYearSoundEvents.GLADE,
                                         NyWidgetTopMenu.DECORATIONS: NewYearSoundEvents.TOYS,
                                         NyWidgetTopMenu.COLLECTIONS: NewYearSoundEvents.ALBUM_SELECT,
                                         NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO,
                                         NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS,
                                         NyWidgetTopMenu.SHARDS: NewYearSoundEvents.DEBRIS},
 NewYearSoundConfigKeys.EXIT_EVENT: {NyWidgetTopMenu.GLADE: NewYearSoundEvents.GLADE_EXIT,
                                     NyWidgetTopMenu.DECORATIONS: NewYearSoundEvents.TOYS_EXIT,
                                     NyWidgetTopMenu.COLLECTIONS: NewYearSoundEvents.ALBUM_SELECT_EXIT,
                                     NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO_EXIT,
                                     NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS_EXIT,
                                     NyWidgetTopMenu.SHARDS: NewYearSoundEvents.DEBRIS_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {NyWidgetTopMenu.DECORATIONS: NewYearSoundStates.TOYS,
                                      NyWidgetTopMenu.COLLECTIONS: NewYearSoundStates.ALBUM_SELECT,
                                      NyWidgetTopMenu.INFO: NewYearSoundStates.INFO,
                                      NyWidgetTopMenu.REWARDS: NewYearSoundStates.REWARDS_LEVELS,
                                      NyWidgetTopMenu.SHARDS: NewYearSoundStates.DEBRIS}}

@loggerTarget(logKey=NY_LOG_KEYS.NY_LOBBY_MENU, loggerCls=NYLogger)
class NYMainMenu(NewYearHistoryNavigation):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.ny_main_menu.NYMainMenuInject())
        settings.flags = ViewFlags.COMPONENT
        settings.model = NyMainMenuModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NYMainMenu, self).__init__(settings)
        self.__tabsController = NewYearMainTabsController()
        self.__currentView = None
        self.__soundsManager = None
        return

    @property
    def viewModel(self):
        return super(NYMainMenu, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltips = R.views.lobby.new_year.tooltips
        if contentID == tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        return NewYearCollectionsTooltipContent() if contentID == tooltips.new_year_collections_tooltip_content.NYCollectionsTooltipContent() else None

    @loggerEntry
    def _onLoading(self, ctx=None, *args, **kwargs):
        super(NYMainMenu, self)._onLoading(*args, **kwargs)
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue}
        self.__soundsManager = NewYearSoundsManager(soundConfig)
        self.viewModel.onSwitchContent += self.__onMenuItemSelected
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self._nyController.onDataUpdated += self.__onDataUpdated
        self._celebrityController.onQuestsUpdated += self.__onDataUpdated
        AccountSettings.onSettingsChanging += self.__onAccountDataUpdated
        g_clientUpdateManager.addCallback('tokens', self.__onTokensChanged)
        g_eventBus.addListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.setIsExtendedAnim(not isMemoryRiskySystem())
        if ctx is not None:
            self.__onSwitchView(ctx)
        return

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onSwitchContent -= self.__onMenuItemSelected
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._celebrityController.onQuestsUpdated -= self.__onDataUpdated
        AccountSettings.onSettingsChanging -= self.__onAccountDataUpdated
        g_clientUpdateManager.removeCallback('tokens', self.__onTokensChanged)
        g_eventBus.removeListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.getCurrentObject() is not None:
            self._resetObject()
        self.__soundsManager.onExitView()
        self.__soundsManager.clear()
        self.__currentView = None
        if self.__tabsController is not None:
            self.__tabsController.closeTabs()
        super(NYMainMenu, self)._finalize()
        return

    @simpleLog(action=NY_LOG_ACTIONS.NY_LOBBY_CLOSE)
    def __onCloseBtnClick(self):
        self.closeMainView()

    def __onMenuItemSelected(self, args):
        menuName = args['view']
        viewAlias = _NAVIGATION_ALIAS_VIEWS[menuName]
        self._navigationHistory.clear()
        if viewAlias == ViewAliases.GLADE_VIEW and self.getCurrentObject() == AdditionalCameraObject.CELEBRITY:
            viewAlias = ViewAliases.CELEBRITY_VIEW
        self._goToByViewAlias(viewAlias, saveHistory=False)

    def __onSwitchViewEvent(self, event):
        ctx = event.ctx
        self.__onSwitchView(ctx)

    def __onSwitchView(self, ctx):
        menuName = ctx.viewParams.menuName
        if menuName != self.__currentView:
            self.__soundsManager.onExitView()
            self.__currentView = menuName
            self.__soundsManager.onEnterView()
        if self.__tabsController.getCurrentTabName() != menuName:
            self.__tabsController.selectTab(menuName)
        self.__updateMenu()

    def __onDataUpdated(self, *_):
        self.__updateMenu()

    def __onAccountDataUpdated(self, key, value):
        if key in (NY_CELEBRITY_CHALLENGE_VISITED,
         NY_CELEBRITY_QUESTS_VISITED_MASK,
         NY_OLD_COLLECTIONS_VISITED,
         NY_OLD_COLLECTIONS_BY_YEAR_VISITED):
            self.__updateMenu()

    def __onTokensChanged(self, tokens):
        if TOKEN_FREE_TALISMANS in tokens or any((token.startswith(CelebrityQuestTokenParts.PREFIX) for token in tokens)):
            self.__updateMenu()

    def __updateMenu(self):
        with self.viewModel.transaction() as model:
            arrayModel = model.getItemsMenu()
            self.__tabsController.updateTabModels(arrayModel)
            tabIdx = self.__tabsController.getSelectedTabIdx()
            model.setStartIndexMenu(tabIdx)

    def __getEntranceSoundEvent(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.ENTRANCE_EVENT, {}).get(self.__currentView)

    def __getExitSoundEvent(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.EXIT_EVENT, {}).get(self.__currentView)

    def __getSoundStateValue(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.STATE_VALUE, {}).get(self.__currentView)


class NYMainMenuUBInject(InjectWithContext):
    __slots__ = ()

    def _getInjectViewClass(self):
        return NYMainMenu
