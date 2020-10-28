# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_voting_result_view.py
import logging
from functools import partial
from operator import itemgetter
from async import async, await
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.battle_pass.battle_pass_award import awardsFactory, BattlePassAwardsManager
from gui.battle_pass.battle_pass_helpers import isNeededToVote, BattlePassProgressionSubTabs, BackgroundPositions
from gui.battle_pass.undefined_bonuses import getStyleInfo, getTankmanInfo, getRecruitNation
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_voting_result_view_model import BattlePassVotingResultViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from gui.shared.event_dispatcher import showStylePreview, hideVehiclePreview, showHangar, isViewLoaded
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from shared_utils import findFirst, first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BattlePassVotingResultView(ViewImpl):
    __slots__ = ('__isOverlay', '__isVoted', '__requestNotifier', '__previewOpened')
    __c11n = dependency.descriptor(ICustomizationService)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, viewModelClazz=BattlePassVotingResultViewModel, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        settings.args = args
        settings.kwargs = kwargs
        self.__isOverlay = False
        self.__isVoted = False
        self.__previewOpened = False
        self.__requestNotifier = SimpleNotifier(self.__getTimeToRepeatRequest, self.__updateVotingResult)
        super(BattlePassVotingResultView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassVotingResultView, self).getViewModel()

    def _onLoading(self, isOverlay=False, *args, **kwargs):
        super(BattlePassVotingResultView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewState()
        if isOverlay:
            self.viewModel.setBackBtnLabel(backport.text(R.strings.menu.viewHeader.closeBtn.label()))
        else:
            self.viewModel.setBackBtnLabel(backport.text(R.strings.menu.viewHeader.backBtn.label()))
            self.viewModel.setBackBtnDescr(backport.text(R.strings.battle_pass_2020.battlePassVoting.backBtnDescr()))
        self.__setRewards()
        self.__setMainData()
        self.__isOverlay = isOverlay
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        super(BattlePassVotingResultView, self)._finalize()
        self.__removeListeners()
        switchHangarOverlaySoundFilter(on=False)
        if not self.__previewOpened:
            self.__battlePassController.getFinalRewardLogic().postEscape()
        self.__previewOpened = False
        self.__requestNotifier.stopNotification()

    def __showLocked(self):
        self.viewModel.setState(self.viewModel.LOCKED_STATE)

    def __showNeedVoting(self):
        self.viewModel.setState(self.viewModel.NEED_VOTING_STATE)

    def __showResult(self):
        self.viewModel.setState(self.viewModel.RESULT_STATE)

    def __showStylePreview(self, args):
        self.__previewOpened = True
        if self.__isOverlay:
            hideVehiclePreview(back=False)
            self.__battlePassController.getFinalRewardLogic().postPreviewOpen()
            self.destroyWindow()
        vehicleCD = int(args.get('vehicleCD'))
        styleID = int(args.get('styleID'))
        style = self.__c11n.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
        showStylePreview(vehicleCD, style, style.getDescription(), partial(self.__previewCallback, self.__isOverlay), backBtnDescrLabel=backport.text(R.strings.battle_pass_2020.battlePassVoting.backBtnTextPreview()))

    def __updateViewState(self):
        if isNeededToVote():
            self.__showNeedVoting()
        elif self.__battlePassController.isPlayerVoted():
            self.__showResult()
        else:
            self.__showLocked()

    def __setMainData(self):
        with self.viewModel.transaction() as tx:
            tx.setMaxEpisode(self.__battlePassController.getMaxLevel())
            tx.setIsBattlePassPurchased(self.__battlePassController.isBought())

    def __setRewards(self):
        finalAwards = self.__battlePassController.getFinalRewards()
        finalAwards = sorted(finalAwards.iteritems(), key=itemgetter(0), reverse=True)
        for vehCD, reward in finalAwards:
            sharedBonuses = awardsFactory(reward.get('shared'))
            uniqueBonuses = awardsFactory(reward.get('unique'))
            additionalSharedBonuses = self.__getAdditionalSharedBonuses(vehCD)
            style = self.__getStyleFromSharedBonuses(sharedBonuses)
            additionalStyle = self.__getStyleFromSharedBonuses(additionalSharedBonuses)
            recruitInfo = self.__getRecruitInfoFromUniqueBonuses(uniqueBonuses)
            if not (style and recruitInfo and additionalStyle):
                return
            vehiclePos = BattlePassAwardsManager.getVehicleBackgroundPosition(vehCD)
            if vehiclePos == BackgroundPositions.LEFT:
                self.__setFinalRewardItem(vehCD, style, recruitInfo, additionalStyle, self.viewModel.leftReward)
            if vehiclePos == BackgroundPositions.RIGHT:
                self.__setFinalRewardItem(vehCD, style, recruitInfo, additionalStyle, self.viewModel.rightReward)

        self.__updateVotingResult()

    def __setFinalRewardItem(self, vehCD, mainStyle, recruitInfo, additionalStyle, item):
        vehicle = self.__itemsCache.items.getItemByCD(vehCD)
        with item.transaction() as tx:
            tx.setStyleID(mainStyle.id)
            tx.setVehicleCD(vehCD)
            tx.setVehicleUserName(vehicle.userName)
            tx.setStyleName(mainStyle.userName)
            tx.setRecruitName(recruitInfo.getFullUserNameByNation(getRecruitNation(recruitInfo)))
            tx.setSelected(self.__battlePassController.getVoteOption() == vehCD)
            role, fullName = self.__getRecruitRoleAndUserName(recruitInfo)
            if self.__battlePassController.isBought():
                rewardsText = backport.text(R.strings.battle_pass_2020.battlePassVoting.options.rewardsBP(), mainStyleName=mainStyle.userName, additionalStyleName=additionalStyle.userName, role=role, recruitFullName=fullName)
            else:
                rewardsText = backport.text(R.strings.battle_pass_2020.battlePassVoting.options.rewards(), mainStyleName=mainStyle.userName, role=role, recruitFullName=fullName)
            tx.setRewards(rewardsText)

    def __getAdditionalSharedBonuses(self, mainVehCD):
        finalAwards = self.__battlePassController.getFinalRewards()
        _, reward = findFirst(lambda (vehCD, _): vehCD != mainVehCD, finalAwards.iteritems())
        return awardsFactory(reward.get('shared'))

    @async
    def __onVoteClick(self, args):
        vehicleCD = int(args.get('vehicleCD'))
        data = {}
        vehiclePos = BattlePassAwardsManager.getVehicleBackgroundPosition(vehicleCD)
        if vehiclePos == BackgroundPositions.LEFT:
            data['finalReward'] = self.viewModel.leftReward
        elif vehiclePos == BackgroundPositions.RIGHT:
            data['finalReward'] = self.viewModel.rightReward
        if isViewLoaded(R.views.lobby.battle_pass.BattlePassVotingConfirmView()):
            return
        result = yield await(dialogs.chooseFinalRewardBattlePass(parent=self.getParentWindow(), data=data))
        if result:
            self.__isVoted = True
            self.__battlePassController.getFinalRewardLogic().postNextState(voteOption=vehicleCD)
            self.__onBackClick()

    def __onBackClick(self):
        if self.__isOverlay:
            showHangar()
        self.destroyWindow()

    def __updateVotingResult(self):
        votingRequester = self.__battlePassController.getVotingRequester()
        success, votingResult = votingRequester.startGettingResults(self.__battlePassController.getSeasonID())
        with self.viewModel.transaction() as tx:
            tx.setFailService(not success)
        if success:
            self.__requestNotifier.startNotification()
        selfVote = self.__battlePassController.getVoteOption()
        for rewardModel in (self.viewModel.rightReward, self.viewModel.leftReward):
            with rewardModel.transaction() as tx:
                vehCD = tx.getVehicleCD()
                tx.setVoicesNumber(votingResult.get(vehCD, 0) + (1 if selfVote == vehCD else 0))

    def __onVotingResultsUpdated(self):
        self.__updateVotingResult()

    def __addListeners(self):
        model = self.viewModel
        model.onPreviewClick += self.__showStylePreview
        model.onVoteClick += self.__onVoteClick
        model.onBackClick += self.__onBackClick
        model.showLocked += self.__showLocked
        model.showNeedVoting += self.__showNeedVoting
        model.showResult += self.__showResult
        self.__battlePassController.onBattlePassSettingsChange += self.__onSettingsChange
        self.__battlePassController.getVotingRequester().onVotingResultsUpdated += self.__onVotingResultsUpdated

    def __removeListeners(self):
        model = self.viewModel
        model.onPreviewClick -= self.__showStylePreview
        model.onVoteClick -= self.__onVoteClick
        model.onBackClick -= self.__onBackClick
        model.showLocked -= self.__showLocked
        model.showNeedVoting -= self.__showNeedVoting
        model.showResult -= self.__showResult
        self.__battlePassController.onBattlePassSettingsChange -= self.__onSettingsChange
        votingRequester = self.__battlePassController.getVotingRequester()
        votingRequester.onVotingResultsUpdated -= self.__onVotingResultsUpdated
        votingRequester.stopGetting()

    def __onSettingsChange(self, *_):
        if self.__battlePassController.isVisible() and not self.__battlePassController.isPaused():
            self.__setRewards()
        else:
            self.destroyWindow()

    @staticmethod
    def __getStyleFromSharedBonuses(sharedBonuses):
        customizationsBonus = findFirst(lambda bonus: bonus.getName() == 'customizations', sharedBonuses)
        styleInfo = getStyleInfo(customizationsBonus)
        if styleInfo is None:
            _logger.error('Could not get style info from shared bonuses')
            return
        else:
            return styleInfo

    @staticmethod
    def __getRecruitInfoFromUniqueBonuses(uniqueBonuses):
        tmanBonus = findFirst(lambda bonus: bonus.getName() == 'tmanToken', uniqueBonuses)
        tankmanInfo = getTankmanInfo(tmanBonus)
        if tankmanInfo is None:
            _logger.error('Could not get tankman info from unique bonuses')
            return
        else:
            return tankmanInfo

    @staticmethod
    def __getTimeToRepeatRequest():
        return ONE_MINUTE * 5

    @staticmethod
    def __getRecruitRoleAndUserName(recruitInfo):
        roles = recruitInfo.getRoles()
        fullName = recruitInfo.getFullUserNameByNation(getRecruitNation(recruitInfo))
        role = '' if len(roles) != 1 else backport.text(R.strings.battle_pass_2020.finalReward.tankman.roles.dyn(first(roles))())
        return (role, fullName)

    def __previewCallback(self, isOverlay):
        self.__previewOpened = False
        self.__battlePassController.getFinalRewardLogic().postClosePreview()
        if not isOverlay:
            showMissionsBattlePassCommonProgression(BattlePassProgressionSubTabs.VOTING_TAB)


class BattlePassVotingResultWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, isOverlay, parent):
        super(BattlePassVotingResultWindow, self).__init__(content=BattlePassVotingResultView(R.views.lobby.battle_pass.BattlePassVotingResultView(), wsFlags=ViewFlags.VIEW if isOverlay else ViewFlags.LOBBY_TOP_SUB_VIEW, isOverlay=isOverlay), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, parent=parent)
