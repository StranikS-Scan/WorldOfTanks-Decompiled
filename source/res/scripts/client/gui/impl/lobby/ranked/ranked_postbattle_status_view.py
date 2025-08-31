# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/ranked_postbattle_status_view.py
import logging
import typing
from account_helpers.AccountSettings import AccountSettings, ENABLE_RANKED_ANIMATIONS
from frameworks.wulf import ViewSettings, Array
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ranked.ranked_postbattle_status_view_model import RankedPostbattleStatusViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent, Window
    from gui.ranked_battles.ranked_models import PostBattleRankInfo
_logger = logging.getLogger(__name__)
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent

class RankedPostbattleStatusView(ViewImpl):
    __slots__ = ('__rewards', '__rankedInfo', '__tooltipItems')
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, rewards, rankedInfo):
        self.__rewards = rewards
        self.__rankedInfo = rankedInfo
        self.__tooltipItems = {}
        settings = ViewSettings(R.views.lobby.ranked.RankedPostbattleStatusView())
        settings.model = RankedPostbattleStatusViewModel()
        super(RankedPostbattleStatusView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RankedPostbattleStatusView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = self.getTooltipData(event)
            if tooltipData is not None:
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window is None:
                    return
                window.load()
                return window
            if tooltipId == TOOLTIPS_CONSTANTS.RANKED_BATTLES_RANK:
                rankID = int(event.getArgument('rankID'))
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(rankID,))
            if tooltipId == TOOLTIPS_CONSTANTS.RANKED_DIVISION_INFO:
                divisionId = str(event.getArgument('divisionId'))
                isCurrent = bool(event.getArgument('isCurrent'))
                isLocked = bool(event.getArgument('isLocked'))
                isCompleted = bool(event.getArgument('isCompleted'))
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(divisionId,
                 isCurrent,
                 isLocked,
                 isCompleted))
            return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(None,))
        else:
            return super(RankedPostbattleStatusView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(RankedPostbattleStatusView, self)._onLoading(*args, **kwargs)
        self.__setViewData()

    def _finalize(self):
        self.__tooltipItems = None
        super(RankedPostbattleStatusView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onDestroy), (self.viewModel.onSwitchAnimation, self.__onSwitchAnimation), (self.viewModel.onSelectReward, self.__onSelectReward))

    @replaceNoneKwargsModel
    def __setViewData(self, model=None):
        finalRank = self.__rankedController.getMaxPossibleRank()
        showAnimation = AccountSettings.getSettings(ENABLE_RANKED_ANIMATIONS)
        model.setMaxRank(self.__rankedInfo.prevMaxRank)
        model.setShowAnimation(showAnimation)
        model.setCanTakeReward(self.__rankedController.hasAnyRewardToTake())
        model.setIsFinal(finalRank == self.__rankedInfo.accRank)
        oldDivision = self.__rankedController.getDivision(self.__rankedInfo.prevAccRank)
        oldRank = self.__rankedInfo.prevAccRank
        model.oldState.setDivision(oldDivision.getID())
        model.oldState.setRank(oldRank)
        model.oldState.setStep(self.__rankedInfo.prevAccStep)
        model.oldState.setDivisionStart(oldDivision.firstRank)
        model.oldState.setDivisionFinish(oldDivision.lastRank)
        newDivision = self.__rankedController.getDivision(self.__rankedInfo.accRank)
        newRank = self.__rankedInfo.accRank
        model.newState.setDivision(newDivision.getID())
        model.newState.setRank(newRank)
        model.newState.setStep(self.__rankedInfo.accStep)
        model.newState.setDivisionStart(newDivision.firstRank)
        model.newState.setDivisionFinish(newDivision.lastRank)
        stepsRank = min(oldRank, newRank) + 1
        model.setTotalSteps(self.__rankedController.getStepsToEarnRank(stepsRank))
        unburnableRanks = Array()
        for rank in self.__rankedController.getModeSettings().unburnableRanks:
            unburnableRanks.addNumber(rank)

        model.setUnburnableRanks(unburnableRanks)
        rewards = model.rewards
        rewards.clearItems()
        packBonusModelAndTooltipData(self.__rewards, rewards, self.__tooltipItems)

    def __onDestroy(self, *_):
        self.destroyWindow()

    def __onSwitchAnimation(self, *_):
        value = AccountSettings.getSettings(ENABLE_RANKED_ANIMATIONS)
        AccountSettings.setSettings(ENABLE_RANKED_ANIMATIONS, not value)
        self.__setViewData()

    def __onSelectReward(self, args):
        rank = args.get('rankID')
        if rank is None:
            return
        else:
            self.__rankedController.takeRewardForRank(rank)
            return


class RankedPostbattleStatusWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards, rankedInfo):
        super(RankedPostbattleStatusWindow, self).__init__(content=RankedPostbattleStatusView(rewards, rankedInfo))
