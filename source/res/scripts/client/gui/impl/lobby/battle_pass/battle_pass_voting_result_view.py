# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_voting_result_view.py
import logging
from functools import partial
from operator import itemgetter
from adisp import process
from async import async, await
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.managers.UtilsManager import ONE_SECOND
from gui.battle_pass.battle_pass_award import awardsFactory
from gui.battle_pass.battle_pass_helpers import isNeededToVote
from gui.battle_pass.undefined_bonuses import getStyleInfo, getTankmanInfo, getRecruitNation
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_voting_result_view_model import BattlePassVotingResultViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.final_reward_item_model import FinalRewardItemModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from gui.shared.event_dispatcher import showStylePreview, showBattleVotingResultWindow, hideVehiclePreview, showHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from gui.sounds.filters import switchHangarOverlaySoundFilter
from gui.wgcg.battle_pass.contexts import BattlePassGetVotingDataCtx
from helpers import dependency
from helpers.func_utils import oncePerPeriod
from shared_utils import findFirst
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)

class BattlePassVotingResultView(ViewImpl):
    __slots__ = ('__isOverlay', '__isVoted', '__requestNotifier')
    __c11n = dependency.descriptor(ICustomizationService)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __webController = dependency.descriptor(IWebController)
    __itemsCache = dependency.descriptor(IItemsCache)
    CALLBACK_REPEAT_TIME = 60

    def __init__(self, layoutID, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, viewModelClazz=BattlePassVotingResultViewModel, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        settings.args = args
        settings.kwargs = kwargs
        self.__isOverlay = False
        self.__isVoted = False
        self.__requestNotifier = SimpleNotifier(self.__getTimeToNotifyFailedRequest, self.__requestVotingData)
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
        self.__requestVotingData()
        self.__setRewards()
        self.__setMaxEpisode()
        self.__isOverlay = isOverlay
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        super(BattlePassVotingResultView, self)._finalize()
        self.__removeListeners()
        switchHangarOverlaySoundFilter(on=False)
        if not self.__isVoted:
            self.__battlePassController.getFinalFlowSM().continueFlow()
        self.__requestNotifier.stopNotification()

    def __showLocked(self):
        self.viewModel.setState(self.viewModel.LOCKED_STATE)

    def __showNeedVoting(self):
        self.viewModel.setState(self.viewModel.NEED_VOTING_STATE)

    def __showResult(self):
        self.viewModel.setState(self.viewModel.RESULT_STATE)

    def __showStylePreview(self, args):
        hideVehiclePreview(noCallback=True)
        self.__battlePassController.getFinalFlowSM().pauseFlow()
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

    def __setMaxEpisode(self):
        self.viewModel.setMaxEpisode(self.__battlePassController.getMaxLevel())

    def __setRewards(self):
        finalAwards = self.__battlePassController.getFinalRewards()
        finalAwards = sorted(finalAwards.iteritems(), key=itemgetter(0), reverse=True)
        for vehCD, reward in finalAwards:
            sharedBonuses = awardsFactory(reward.get('shared'))
            uniqueBonuses = awardsFactory(reward.get('unique'))
            style = self.__getStyleFromSharedBonuses(sharedBonuses)
            recruitInfo = self.__getRecruitInfoFromUniqueBonuses(uniqueBonuses)
            if style is None or recruitInfo is None:
                return
            self.viewModel.finalRewards.addViewModel(self.__getRewardItem(vehCD, style, recruitInfo))

        return

    def __getRewardItem(self, vehCD, style, recruitInfo):
        vehicle = self.__itemsCache.items.getItemByCD(vehCD)
        item = FinalRewardItemModel()
        item.setStyleID(style.id)
        item.setVehicleCD(vehCD)
        item.setVehicleUserName(vehicle.userName)
        item.setStyleName(style.userName)
        item.setRecruitName(recruitInfo.getFullUserNameByNation(getRecruitNation(recruitInfo)))
        item.setSelected(self.__battlePassController.getVoteOption() == vehCD)
        return item

    @oncePerPeriod(ONE_SECOND)
    @async
    def __onVoteClick(self, args):
        vehicleCD = int(args.get('vehicleCD'))
        data = {}
        for reward in self.viewModel.finalRewards.getItems():
            if reward.getVehicleCD() == vehicleCD:
                data['finalReward'] = reward

        result = yield await(dialogs.chooseFinalRewardBattlePass(data=data))
        if result:
            self.__isVoted = True
            self.__battlePassController.getFinalFlowSM().continueFlow(voteOption=vehicleCD)
            self.__onBackClick()

    def __onBackClick(self):
        if self.__isOverlay:
            showHangar()
        else:
            showMissionsBattlePassCommonProgression()
        self.destroyWindow()

    def __updateVotingResult(self, votingResult):
        selfVote = self.__battlePassController.getVoteOption()
        for model in self.viewModel.finalRewards.getItems():
            vehCD = model.getVehicleCD()
            model.setVoicesNumber(votingResult.get(vehCD, 0) + (1 if selfVote == vehCD else 0))

    def __addListeners(self):
        model = self.viewModel
        model.onPreviewClick += self.__showStylePreview
        model.onVoteClick += self.__onVoteClick
        model.onBackClick += self.__onBackClick
        model.showLocked += self.__showLocked
        model.showNeedVoting += self.__showNeedVoting
        model.showResult += self.__showResult
        self.__battlePassController.onBattlePassSettingsChange += self.__onSettingsChange

    def __removeListeners(self):
        model = self.viewModel
        model.onPreviewClick -= self.__showStylePreview
        model.onVoteClick -= self.__onVoteClick
        model.onBackClick -= self.__onBackClick
        model.showLocked -= self.__showLocked
        model.showNeedVoting -= self.__showNeedVoting
        model.showResult -= self.__showResult
        self.__battlePassController.onBattlePassSettingsChange -= self.__onSettingsChange

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

    @process
    def __requestVotingData(self):
        ctx = BattlePassGetVotingDataCtx(self.__battlePassController.getSeasonID())
        response = yield self.__webController.sendRequest(ctx=ctx)
        success = response.isSuccess()
        if success:
            result = ctx.getDataObj(response.getData())
            self.__updateVotingResult(result)
        else:
            self.__requestNotifier.startNotification()
        self.viewModel.setFailService(not success)

    def __getTimeToNotifyFailedRequest(self):
        return self.CALLBACK_REPEAT_TIME

    @classmethod
    def __previewCallback(cls, isOverlay):
        cls.__battlePassController.getFinalFlowSM().unpauseFlow()
        hideVehiclePreview(noCallback=True)
        showBattleVotingResultWindow(isOverlay=isOverlay)
