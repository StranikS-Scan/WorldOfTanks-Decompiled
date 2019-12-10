# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_info_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_gift_list_item import NewYearGiftListItem
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.shared.event_dispatcher import showNewYearInfoPage, showLootBoxBuyWindow
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates
from helpers import dependency
from new_year.ny_bonuses import CreditsBonusHelper
from items.components.ny_constants import ToyTypes
from new_year.ny_constants import NyTabBarRewardsView
from new_year.vehicle_branch import getInEventCooldown
from ny_common.settings import NYLootBoxConsts, NY_CONFIG_NAME
from skeletons.gui.lobby_context import ILobbyContext
_giftsOrder = (NewYearInfoViewModel.LEVELS,
 NewYearInfoViewModel.STYLES,
 NewYearInfoViewModel.SMALLBOXES,
 NewYearInfoViewModel.BIGBOXES)

class NewYearInfoView(NewYearHistoryNavigation):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('__giftsOrder', '__giftsCallbacks')

    def __init__(self, *args, **kwargs):
        super(NewYearInfoView, self).__init__(ViewSettings(R.views.lobby.new_year.views.new_year_info_view.NewYearInfoView(), flags=ViewFlags.VIEW, model=NewYearInfoViewModel()), *args, **kwargs)

    def _onLoading(self, *args, **kwargs):
        super(NewYearInfoView, self)._onLoading()
        maxBonus = CreditsBonusHelper.getMaxBonus()
        maxMegaBonus = CreditsBonusHelper.getMegaToysBonusByCount(len(ToyTypes.MEGA))
        with self.viewModel.transaction() as model:
            model.setMaxBonus(maxBonus)
            model.setCreditsBonus(CreditsBonusHelper.getBonus())
            model.setUsualMaxBonus(maxBonus - maxMegaBonus)
            model.setSingleMegaBonus(CreditsBonusHelper.getMegaToysBonusValue())
            model.setMaxMegaBonus(maxMegaBonus)
            model.setCooldownValue(getInEventCooldown())
            self.__updateGifts(model)

    def _initialize(self, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: NewYearSoundEvents.INFO,
         NewYearSoundConfigKeys.EXIT_EVENT: NewYearSoundEvents.INFO_EXIT,
         NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.INFO}
        super(NewYearInfoView, self)._initialize(soundConfig)
        self.viewModel.onVideoClicked += self.__onVideoClicked
        self.viewModel.onButtonClick += self.__changeView
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def _finalize(self):
        self.viewModel.onVideoClicked -= self.__onVideoClicked
        self.viewModel.onButtonClick -= self.__changeView
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(NewYearInfoView, self)._finalize()

    @property
    def viewModel(self):
        return super(NewYearInfoView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        pass

    def __updateGifts(self, model):
        isLootBoxesEnabled = self.__lobbyContext.getServerSettings().isLootBoxesEnabled()
        isBrowserIcon = self.__lobbyContext.getServerSettings().getLootBoxShop().get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.EXTERNAL) == NYLootBoxConsts.EXTERNAL
        model.giftList.clear()
        model.giftList.invalidate()
        for giftType in _giftsOrder:
            newType = NewYearGiftListItem()
            newType.setType(giftType)
            if giftType == NewYearInfoViewModel.BIGBOXES:
                newType.setIsShowButton(isLootBoxesEnabled)
                newType.setIsBrowserIconVisible(isBrowserIcon)
            else:
                newType.setIsShowButton(giftType != NewYearInfoViewModel.SMALLBOXES)
            model.giftList.addViewModel(newType)

        model.giftList.invalidate()

    def __changeView(self, args):
        action = args['value']
        if action == NewYearInfoViewModel.LEVELS:
            self._goToRewardsView(viewName=NyTabBarRewardsView.FOR_LEVELS)
        elif action == NewYearInfoViewModel.STYLES:
            self._goToRewardsView(viewName=NyTabBarRewardsView.COLLECTION_NY20)
        elif action == NewYearInfoViewModel.BIGBOXES:
            showLootBoxBuyWindow()

    @staticmethod
    def __onVideoClicked():
        showNewYearInfoPage()

    def __onServerSettingsChanged(self, diff):
        if 'isLootBoxesEnabled' in diff or diff.get(NY_CONFIG_NAME, {}).get(NYLootBoxConsts.CONFIG_NAME) is not None:
            self.__updateGifts(self.viewModel)
        return
