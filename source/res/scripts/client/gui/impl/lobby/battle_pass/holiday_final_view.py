# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/holiday_final_view.py
from battle_pass_common import BattlePassConsts, BattlePassTankmenSource
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_helpers import getReceivedTankmenCount, getTankmenShopPackages, getVehicleInfoForChapter, isSeasonEndingSoon
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.holiday_final_view_model import HolidayFinalViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import ChapterStates
from gui.impl.lobby.battle_pass.states import FinalRewardPreviewBattlePassState
from gui.impl.pub.view_component import ViewComponent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import selectVehicleInHangar, showBattlePass, showBattlePassTankmenVoiceover
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}

class HolidayFinalPresenter(ViewComponent[HolidayFinalViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(HolidayFinalPresenter, self).__init__(R.aliases.battle_pass.HolidayFinal(), HolidayFinalViewModel)
        self.__chapterID = None
        self.__tooltipItems = {}
        return

    @property
    def viewModel(self):
        return super(HolidayFinalPresenter, self).getViewModel()

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def updateInitialData(self, **kwargs):
        self.__updateState()

    def _onLoading(self, *args, **kwargs):
        super(HolidayFinalPresenter, self)._onLoading(*args, **kwargs)
        self.__battlePass.tankmenCacheUpdate()
        self.__chapterID = self.__battlePass.getHolidayChapterID()
        self.__updateState()
        self.__fillModel()

    def _finalize(self):
        self.__chapterID = None
        self.__tooltipItems = None
        super(HolidayFinalPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.awardsWidget.onTakeRewardsClick, self.__takeAllRewards),
         (self.viewModel.awardsWidget.showTankmen, self.__showTankmen),
         (self.viewModel.showRewards, self.__showRewards),
         (self.viewModel.onTakeRewardsClick, self.__takeAllRewards),
         (self.viewModel.showTankmen, self.__showTankmen),
         (self.viewModel.onPreviewVehicle, self.__onPreview),
         (self.viewModel.showVehicle, self.__showVehicle),
         (self.viewModel.showBuy, self.__showBuyWindow),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onEntitlementCacheUpdated, self.__updateState))

    def _getListeners(self):
        return ((events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY),)

    def __fillModel(self):
        self.__setChapter()
        self.__updateDetailRewards()
        with self.viewModel.transaction() as model:
            model.awardsWidget.setIsTalerEnabled(not self.__battlePass.isHoliday())
            model.awardsWidget.setIsBpCoinEnabled(not self.__battlePass.isHoliday())
            model.awardsWidget.setTankmenScreenID(self.__battlePass.getTankmenScreenID(self.__chapter))
            model.setIsSeasonEndingSoon(isSeasonEndingSoon())
            self.__updateRewardChoice(model=model)

    def __setChapter(self):
        with self.viewModel.transaction() as tx:
            tx.setChapterID(self.__chapterID)
            tx.setChapterState(_CHAPTER_STATES.get(self.__battlePass.getChapterState(self.__chapterID)))
            tx.setCurrentLevel(self.__battlePass.getLevelInChapter(self.__chapterID) + 1)

    def __isTankmenReceived(self, shopPackages):
        return all((packageCount - getReceivedTankmenCount(tankman) == 0 for tankman, packageCount in shopPackages.iteritems())) and all((getReceivedTankmenCount(tankman) > 0 for tankman, info in self.__battlePass.getSpecialTankmen().iteritems() if info.get('source') == BattlePassTankmenSource.QUEST_CHAIN)) and all((info.get('availableCount', 0) - getReceivedTankmenCount(tankman) == 0 for tankman, info in self.__battlePass.getSpecialTankmen().iteritems() if info.get('source') in BattlePassTankmenSource.PROGRESSION))

    def __update(self):
        if self.__battlePass.isPaused():
            showBattlePass()
        else:
            self.__fillModel()
            self.__updateState()

    def __onBattlePassSettingsChanged(self, *_):
        self.__update()

    @replaceNoneKwargsModel
    def __updateRewardChoice(self, model=None):
        model.awardsWidget.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
        model.awardsWidget.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())

    def __updateDetailRewards(self):
        fromLevel = 1
        toLevel = self.__battlePass.getLevelInChapter(self.__chapterID)
        with self.viewModel.rewards.transaction() as tx:
            tx.nowRewards.clearItems()
            tx.futureRewards.clearItems()
            tx.setFromLevel(fromLevel)
            tx.setToLevel(toLevel)
            tx.setChapterID(self.__chapterID)
        packBonusModelAndTooltipData(self.__getRewards(), self.viewModel.rewards.nowRewards, self.__tooltipItems)

    def __getRewards(self):
        fromLevel = 1
        curLevel = self.__battlePass.getLevelInChapter(self.__chapterID)
        bonuses = []
        if not self.__battlePass.isBought(self.__chapterID):
            bonuses.extend(self.__battlePass.getPackedAwardsInterval(self.__chapterID, fromLevel, curLevel, awardType=BattlePassConsts.REWARD_PAID))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def __showRewards(self):
        self.viewModel.setState(self.viewModel.REWARDS_STATE)

    def __updateState(self):
        if not self.__battlePass.isBought(self.__chapterID):
            state = self.viewModel.BUY_STATE
        elif self.__battlePass.getTankmenScreenID(self.__chapter) and not self.__isTankmenReceived(getTankmenShopPackages()):
            state = self.viewModel.TANKMEN_STATE
        elif self.__battlePass.getNotChosenRewardCount() > 0:
            state = self.viewModel.SELECTABLE_REWARDS_STATE
        else:
            state = self.viewModel.FINAL_STATE
        self.viewModel.setState(state)

    def __onPreview(self):
        FinalRewardPreviewBattlePassState.goTo(chapterID=self.__chapterID, origin=self.layoutID)

    def __takeAllRewards(self):
        self.__battlePass.takeAllRewards()

    def __showTankmen(self):
        showBattlePassTankmenVoiceover(self.__battlePass.getTankmenScreenID(self.__chapter))

    def __showVehicle(self):
        vehicle, _ = getVehicleInfoForChapter(self.__chapterID)
        if vehicle.isInInventory:
            selectVehicleInHangar(vehicle.intCD)
        else:
            self.destroyWindow()

    def __onAwardViewClose(self, *_):
        self.__updateState()
        self.__fillModel()

    @staticmethod
    def __showBuyWindow():
        showBattlePass(R.aliases.battle_pass.BuyPass())
