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
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.tiers_limit_model import TiersLimitModel
from gui.shared.formatters.ranges import toRomanRangeString
from gui.impl.lobby.platoon.platoon_helpers import convertTierFilterToList
from gui.impl.lobby.platoon.tooltip.platoon_alert_tooltip import AlertTooltip
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl import backport
_logger = logging.getLogger(__name__)
_strButtons = R.strings.platoon.buttons

class TiersLimitSubview(ViewImpl):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.platoon.subViews.TiersLimit(), model=TiersLimitModel())
        self.__isShowingSettings = False
        self.__showSettingsCallback = None
        self.__searchFlags = None
        self.__tiersString = None
        self.__isExpanded = False
        super(TiersLimitSubview, self).__init__(settings)
        return

    def resetState(self):
        self.__searchFlags = None
        self.__tiersString = None
        self.__isExpanded = False
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return AlertTooltip(R.strings.platoon.searching.expanded.header(), R.strings.platoon.searching.expanded.body()) if contentID == R.views.lobby.platoon.AlertTooltip() else None

    def hideSettings(self):
        self.__isShowingSettings = False
        self.__updateSettingsButtonIsPressedState()

    def setShowCallback(self, func):
        self.__showSettingsCallback = func

    def update(self, *args):
        if self.__tiersString:
            self.__updateViewModel()
        else:
            self.__updateTierFilterString()

    def _finalize(self):
        self.__showSettingsCallback = None
        self.__removeListeners()
        return

    def _onLoading(self, *args, **kwargs):
        self.__addListeners()
        self.resetState()
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
        platoonCtrl = self.__platoonCtrl
        platoonCtrl.onFilterUpdate += self.__updateTierFilterString
        platoonCtrl.onMembersUpdate += self.__onMembersUpdate
        platoonCtrl.onAvailableTiersForSearchChanged += self.__updateTierFilterString
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def __removeListeners(self):
        self.viewModel.btnResetSettings.onClick -= self.__onReset
        if self.__showSettingsCallback:
            self.viewModel.btnShowSettings.onClick -= self.__onShow
        platoonCtrl = self.__platoonCtrl
        platoonCtrl.onFilterUpdate -= self.__updateTierFilterString
        platoonCtrl.onMembersUpdate -= self.__onMembersUpdate
        platoonCtrl.onAvailableTiersForSearchChanged -= self.__updateTierFilterString
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def __onServerSettingsChange(self, diff):
        if 'unit_assembler_config' in diff:
            self.update()

    def __updateViewModel(self):
        platoonCtrl = self.__platoonCtrl
        layoutID = self.getParentView().layoutID
        isInSearch = platoonCtrl.isInSearch()
        isInQueue = platoonCtrl.isInQueue()
        hasTierPreferences = platoonCtrl.isTankLevelPreferenceEnabled()
        tiersString = self.__tiersString if platoonCtrl.canStartSearch() else ''
        with self.viewModel.transaction() as model:
            hasResetSettingsButton = bool(tiersString) and layoutID != R.views.lobby.platoon.SearchingDropdown() and platoonCtrl.canStartSearch() and not isInSearch
            hasLookingForCaption = hasTierPreferences and layoutID == R.views.lobby.platoon.SearchingDropdown() and bool(tiersString)
            hasTiersString = hasTierPreferences and layoutID != R.views.lobby.platoon.MembersWindow() and bool(tiersString) and platoonCtrl.canStartSearch()
            hasFilterOptions = hasTierPreferences or platoonCtrl.isVOIPEnabled()
            hasSettingsButton = layoutID != R.views.lobby.platoon.SearchingDropdown() and platoonCtrl.canStartSearch() and hasFilterOptions
            isSettingsButtonEnabled = not isInQueue and not isInSearch and platoonCtrl.hasFreeSlot() or layoutID == R.views.lobby.platoon.PlatoonDropdown()
            usePopover = layoutID == R.views.lobby.platoon.MembersWindow()
            useLight = layoutID == R.views.lobby.platoon.SearchingDropdown()
            model.setHasResetButton(hasResetSettingsButton)
            model.setHasLookingForCaption(hasLookingForCaption)
            model.setHasTiersCaption(hasTiersString)
            model.btnShowSettings.setIsEnabled(isSettingsButtonEnabled)
            model.btnShowSettings.setHasPopover(usePopover)
            model.setHasSettingsButton(hasSettingsButton)
            model.setIsLight(useLight)
            model.setTiers(tiersString)
            model.setIsExpanded(self.__isExpanded)

    def __onSettingsChanged(self, diff):
        if GAME.UNIT_FILTER in diff:
            self.__updateTierFilterString()

    def __updateTierFilterString(self):
        platoonCtrl = self.__platoonCtrl
        if platoonCtrl.isTankLevelPreferenceEnabled():
            searchFlags, isExpanded = platoonCtrl.getExpandedSearchFlags()
            if not self.__tiersString or searchFlags != self.__searchFlags:
                self.__searchFlags = searchFlags
                self.__tiersString = toRomanRangeString(convertTierFilterToList(searchFlags), 1)
            self.__isExpanded = isExpanded
        else:
            self.__tiersString = ''
            self.__isExpanded = False
        self.__updateViewModel()

    def __onReset(self):
        self.__platoonCtrl.resetUnitTierFilter()

    def __onShow(self):
        if self.__showSettingsCallback:
            self.__isShowingSettings = not self.__isShowingSettings
            self.__updateSettingsButtonIsPressedState()
            self.__showSettingsCallback(self.__isShowingSettings)

    def __onMembersUpdate(self):
        self.update()

    def __updateSettingsButtonIsPressedState(self):
        with self.viewModel.transaction() as model:
            model.btnShowSettings.setIsPressed(self.__isShowingSettings)
