# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/info_page/ny_info_view.py
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from constants import CURRENT_REALM
from gifts.gifts_common import GiftEventID, GiftEventState
from gui.gift_system.constants import HubUpdateReason
from gui.gift_system.mixins import GiftEventHubWatcher
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel, GiftSystemState, Tabs
from gui.impl.lobby.new_year.ny_views_helpers import showInfoVideo
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases, VIEW_ALIAS_TO_MENU_NAME
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showLootBoxBuyWindow, showLootBoxEntry, showLootBoxGuaranteedRewardsInfo, showLootBoxOpeningStream
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from helpers import dependency, getLanguageCode
from items.components.ny_constants import ToyTypes
from new_year.celebrity.celebrity_quests_helpers import getQuestCountForExtraSlot, getQuestCountForCommander
from new_year.ny_bonuses import CreditsBonusHelper, getBonusConfig
from new_year.ny_constants import NyTabBarRewardsView
from ny_common.settings import NYLootBoxConsts, NY_CONFIG_NAME
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.ny.loggers import NyInfoViewSlideLogger, NyInfoViewLogger, NyInfoFlowLogger
_giftsOrder = (NewYearInfoViewModel.LEVELS,
 NewYearInfoViewModel.STYLES,
 NewYearInfoViewModel.SMALLBOXES,
 NewYearInfoViewModel.BIGBOXES)
_GIFT_EVENT_STATE_MAP = {GiftEventState.ENABLED: GiftSystemState.ENABLED,
 GiftEventState.SUSPENDED: GiftSystemState.SUSPENDED,
 GiftEventState.DISABLED: GiftSystemState.DISABLED}
_TAB_BY_VIEW_ALIAS = {ViewAliases.VEHICLES_VIEW: Tabs.VEHICLES}

class NyInfoView(HistorySubModelPresenter, GiftEventHubWatcher):
    __slots__ = ('__slideLogger',)
    _GIFT_EVENT_ID = GiftEventID.NY_HOLIDAYS
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __flowLogger = NyInfoFlowLogger()

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NyInfoView, self).__init__(viewModel, parentView)
        self.__slideLogger = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NyInfoView, self).initialize()
        self.viewModel.videoCover.onClick += self.__onClickVideo
        self.viewModel.onButtonClick += self.__onButtonClick
        self.viewModel.onSlideChanged += self.__onSlideChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        NewYearNavigation.onUpdateCurrentView += self.__onUpdateView
        self.catchGiftEventHub()
        maxBonus = CreditsBonusHelper.getMaxBonus()
        maxMegaBonus = CreditsBonusHelper.getMegaToysBonusByCount(len(ToyTypes.MEGA))
        multipliersList = getBonusConfig().getAtmosphereMultipliers()
        if kwargs.get('showDefaultTabForced', False):
            startTab = Tabs.DEFAULT
        else:
            startTab = _TAB_BY_VIEW_ALIAS.get(kwargs.get('previousViewAlias'), Tabs.DEFAULT)
        self.__slideLogger = NyInfoViewSlideLogger(startTab=startTab)
        self.__slideLogger.onSlideOpened()
        with self.viewModel.transaction() as model:
            model.setMaxBonus(maxBonus)
            model.setUsualMaxBonus(maxBonus - maxMegaBonus)
            model.setSingleMegaBonus(CreditsBonusHelper.getMegaToysBonusValue())
            model.setMaxMegaBonus(maxMegaBonus)
            model.region.setRealm(CURRENT_REALM)
            model.region.setLanguage(getLanguageCode())
            model.setQuestsToGetExtraSlot(getQuestCountForExtraSlot())
            model.setMinMultiplier(min(multipliersList))
            model.setMaxMultiplier(max(multipliersList))
            model.setQuestsToGetCommander(getQuestCountForCommander())
            model.setStartTab(startTab)
            self.__updateStatus(model=model)

    def finalize(self):
        NyInfoViewLogger().onViewClosed()
        self.__onSlideClosed()
        self.viewModel.videoCover.onClick -= self.__onClickVideo
        self.viewModel.onButtonClick -= self.__onButtonClick
        self.viewModel.onSlideChanged -= self.__onSlideChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        NewYearNavigation.onUpdateCurrentView -= self.__onUpdateView
        self.releaseGiftEventHub()
        super(NyInfoView, self).finalize()

    def _onGiftHubUpdate(self, reason, _=None):
        if reason == HubUpdateReason.SETTINGS:
            self.__updateStatus()

    def _goBack(self):
        if not self._navigationHistory.isEmpty:
            backPageAlias = self._navigationHistory.getLast()
            if backPageAlias:
                self.__flowLogger.logBackClick(view=VIEW_ALIAS_TO_MENU_NAME.get(backPageAlias), albumTab=self._tabCache.getCurrentYear(), rewardTab=self._tabCache.getRewardsTab(), selectedObject=NewYearNavigation.getCurrentObject())
        super(NyInfoView, self)._goBack()

    @replaceNoneKwargsModel
    def __updateStatus(self, model=None):
        isLootBoxesEnabled = self.__lobbyContext.getServerSettings().isLootBoxesEnabled()
        isExternalBuyBox = self.__lobbyContext.getServerSettings().getLootBoxShop().get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.EXTERNAL) == NYLootBoxConsts.EXTERNAL
        model.setGiftSystemState(_GIFT_EVENT_STATE_MAP[self.getGiftEventState()])
        model.setIsExternalBuyBox(isExternalBuyBox)
        model.setIsLootBoxEnabled(isLootBoxesEnabled)

    def __onButtonClick(self, args):
        action = args['value']
        if action == NewYearInfoViewModel.LEVELS:
            self._goToRewardsView(tabName=NyTabBarRewardsView.FOR_LEVELS, popHistory=True)
        elif action == NewYearInfoViewModel.STYLES:
            self._goToRewardsView(tabName=NyTabBarRewardsView.COLLECTION_NY22, popHistory=True)
        elif action == NewYearInfoViewModel.BIGBOXES:
            showLootBoxBuyWindow()
        elif action == NewYearInfoViewModel.SMALLBOXES:
            self.__slideLogger.onViewOpened()
            showLootBoxEntry(lootBoxType=NewYearLootBoxes.COMMON)
        elif action == NewYearInfoViewModel.CELEBRITY:
            self._goToCelebrityView(popHistory=True, skipIntro=True)
        elif action == NewYearInfoViewModel.GUARANTEED_REWARDS:
            showLootBoxGuaranteedRewardsInfo()
        elif action == NewYearInfoViewModel.STREAM_BOX:
            showLootBoxOpeningStream()
        elif action == NewYearInfoViewModel.GIFT:
            skipIntro = {NewYearStorageKeys.GIFT_SYSTEM_INTRO_VISITED: True}
            self.__settingsCore.serverSettings.saveInNewYearStorage(skipIntro)
            self._goToByViewAlias(ViewAliases.GIFT_SYSTEM_VIEW, popHistory=True)

    @staticmethod
    def __onClickVideo():
        showInfoVideo()

    def __onSlideChanged(self, args):
        self.__onSlideClosed()
        slideName = args.get('name')
        switchType = args.get('switchType')
        if slideName and switchType:
            self.__slideLogger = NyInfoViewSlideLogger(slideName=slideName)
            self.__slideLogger.onSlideOpened(switchType)

    def __onUpdateView(self, *_, **kwargs):
        prevViewAlias = kwargs.get('previousViewAlias')
        if prevViewAlias and self._navigationHistory.getLast() != prevViewAlias:
            self._navigationHistory.clear()
            self._navigationHistory.addToHistory(prevViewAlias, {})
            self._updateBackButton()
            startTab = _TAB_BY_VIEW_ALIAS.get(prevViewAlias, Tabs.DEFAULT)
            self.viewModel.setStartTab(startTab)
            self.__onSlideClosed()
            self.__slideLogger = NyInfoViewSlideLogger(startTab=startTab)
            self.__slideLogger.onSlideOpened()

    def __onServerSettingsChanged(self, diff):
        if 'isLootBoxesEnabled' in diff or diff.get(NY_CONFIG_NAME, {}).get(NYLootBoxConsts.CONFIG_NAME) is not None:
            self.__updateStatus()
        return

    def __onSlideClosed(self):
        if self.__slideLogger is not None:
            self.__slideLogger.onSlideClosed()
            self.__slideLogger = None
        return
