# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/subview/platoon_tiers_limit_subview.py
import logging
import typing
from account_helpers.settings_core.settings_constants import GAME
from frameworks.wulf import ViewEvent, View
from gui.impl.pub.view_impl import ViewImpl
from frameworks.wulf import ViewSettings
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.shared import IItemsCache
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.tiers_limit_model import TiersLimitModel
from gui.shared.formatters.ranges import toRomanRangeString
from gui.impl.lobby.platoon.platoon_helpers import convertTierFilterToList
from gui.impl.lobby.platoon.tooltip.platoon_alert_tooltip import AlertTooltip
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl import backport
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
_logger = logging.getLogger(__name__)
_strButtons = R.strings.platoon.buttons

class TiersLimitSubview(ViewImpl):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)
    tiersString = None
    isExpanded = False

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.platoon.subViews.TiersLimit(), model=TiersLimitModel())
        self.__isShowingSettings = False
        self.__showSettingsCallback = None
        super(TiersLimitSubview, self).__init__(settings)
        return

    @staticmethod
    def resetState():
        TiersLimitSubview.tiersString = None
        TiersLimitSubview.isExpanded = False
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return AlertTooltip(R.strings.platoon.searching.expanded.header(), R.strings.platoon.searching.expanded.body()) if contentID == R.views.lobby.platoon.AlertTooltip() else None

    def hideSettings(self):
        self.__isShowingSettings = False

    def setShowCallback(self, func):
        self.__showSettingsCallback = func

    def _finalize(self):
        self.__showSettingsCallback = None
        self.__removeListeners()
        return

    def _onLoading(self, *args, **kwargs):
        self.__addListeners()
        self.update()
        with self.viewModel.transaction() as model:
            model.btnShowSettings.setCaption(backport.text(_strButtons.settings.caption()))
            model.btnShowSettings.setDescription(backport.text(_strButtons.settings.description()))
            model.btnResetSettings.setCaption(backport.text(_strButtons.reset.caption()))
            model.btnResetSettings.setDescription(backport.text(_strButtons.reset.description()))

    def __addListeners(self):
        self.viewModel.btnResetSettings.onClick += self.__onReset
        if self.__showSettingsCallback:
            self.viewModel.btnShowSettings.onClick += self.__onShow
        self.__platoonCtrl.onFilterUpdate += self.__onFilterUpdate
        self.__platoonCtrl.onMembersUpdate += self.__onMembersUpdate
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_eventBus.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.update, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted += self.__onVehicleStateChanged

    def __removeListeners(self):
        self.viewModel.btnResetSettings.onClick -= self.__onReset
        if self.__showSettingsCallback:
            self.viewModel.btnShowSettings.onClick -= self.__onShow
        self.__platoonCtrl.onFilterUpdate -= self.__onFilterUpdate
        self.__platoonCtrl.onMembersUpdate -= self.__onMembersUpdate
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_eventBus.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.update, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted -= self.__onVehicleStateChanged

    def update(self, *args):
        if TiersLimitSubview.tiersString:
            self.__updateViewModel()
            return
        else:
            self.__onFilterUpdate(None, False)
            return

    def __onServerSettingsChange(self, diff):
        if 'unit_assembler_config' in diff:
            self.update()

    def __onVehicleStateChanged(self, *args, **kwargs):
        self.update()

    def __updateViewModel(self):
        layoutID = self.getParentView().layoutID
        isInSearch = self.__platoonCtrl.isInSearch()
        hasTierPreferences = self.__platoonCtrl.isTankLevelPreferenceEnabled()
        tiersString = TiersLimitSubview.tiersString if self.__platoonCtrl.canStartSearch() else ''
        with self.viewModel.transaction() as model:
            hideResetSettingsButton = not bool(tiersString) or layoutID == R.views.lobby.platoon.SearchingDropdown() or not self.__platoonCtrl.canStartSearch() or isInSearch
            canShowLookingForCaption = hasTierPreferences and layoutID == R.views.lobby.platoon.SearchingDropdown() and bool(tiersString)
            canShowTiersString = layoutID != R.views.lobby.platoon.MembersWindow() and bool(tiersString) and self.__platoonCtrl.canStartSearch()
            hasFilterOptions = hasTierPreferences or self.__platoonCtrl.isVOIPEnabled()
            isSettingsButtonVisible = layoutID != R.views.lobby.platoon.SearchingDropdown() and self.__platoonCtrl.canStartSearch() and hasFilterOptions
            isSettingsButtonEnabled = not isInSearch and self.__platoonCtrl.hasFreeSlot() or layoutID == R.views.lobby.platoon.PlatoonDropdown()
            usePopover = layoutID == R.views.lobby.platoon.MembersWindow()
            useLight = layoutID == R.views.lobby.platoon.SearchingDropdown()
            model.setHideResetButton(hideResetSettingsButton)
            model.setShowLookingForCaption(canShowLookingForCaption)
            model.setShowTiersCaption(canShowTiersString)
            model.btnShowSettings.setIsVisible(isSettingsButtonVisible)
            model.btnShowSettings.setIsEnabled(isSettingsButtonEnabled)
            model.btnShowSettings.setShouldShowPopover(usePopover)
            model.setIsLight(useLight)
            model.setTiers(tiersString)
            model.setIsExpanded(TiersLimitSubview.isExpanded)

    def __onSettingsChanged(self, diff):
        if GAME.UNIT_FILTER in diff:
            self.__onFilterUpdate(None, False)
        return

    def __onFilterUpdate(self, tierFilter, isExpanded):
        if tierFilter is None:
            unitFilter = self.__platoonCtrl.getUnitFilter()
            tierFilter = convertTierFilterToList(unitFilter)
        tierString = ''
        if self.__platoonCtrl.isTankLevelPreferenceEnabled():
            tierString = toRomanRangeString(tierFilter, 1)
        TiersLimitSubview.tiersString = tierString
        TiersLimitSubview.isExpanded = isExpanded
        self.__updateViewModel()
        return

    def __onReset(self):
        self.__platoonCtrl.resetUnitTierFilter()

    def __onShow(self):
        if self.__showSettingsCallback:
            self.__isShowingSettings = not self.__isShowingSettings
            self.__showSettingsCallback(self.__isShowingSettings)

    def __onMembersUpdate(self):
        self.update()
