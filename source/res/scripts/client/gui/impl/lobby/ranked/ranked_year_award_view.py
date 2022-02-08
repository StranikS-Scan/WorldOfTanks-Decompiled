# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/ranked_year_award_view.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent, getRewardRendererModelPresenter, RANKED_MODEL_PRESENTERS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ranked.ranked_year_award_model import RankedYearAwardModel
from gui.ranked_battles.constants import YEAR_AWARDS_ORDER, YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX
from gui.ranked_battles.ranked_formatters import getFormattedBonusesForYearAwardsWindow
from gui.shared import event_dispatcher
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.ranked_battles.ranked_helpers.sound_manager import RankedSoundManager
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
_logger = logging.getLogger(__name__)

class RankedYearAwardView(ViewImpl):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __slots__ = ('__items', '__bonuses', '__points', '__vehicleCD', '__showRemainedSelection')

    def __init__(self, contentResId, *args, **kwargs):
        settings = ViewSettings(contentResId)
        settings.model = RankedYearAwardModel()
        settings.args = args
        settings.kwargs = kwargs
        super(RankedYearAwardView, self).__init__(settings)
        self.__items = {}
        self.__bonuses = []
        self.__points = None
        self.__vehicleCD = None
        self.__showRemainedSelection = False
        return

    @property
    def viewModel(self):
        return super(RankedYearAwardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(RankedYearAwardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def _initialize(self, *args):
        super(RankedYearAwardView, self)._initialize()
        self.viewModel.onDestroyEvent += self.__onDestroy
        self.viewModel.onActionBtnClick += self.__onActionButtonClick
        RankedSoundManager().setOverlayStateOn()

    def _finalize(self):
        self.viewModel.onDestroyEvent -= self.__onDestroy
        self.viewModel.onActionBtnClick -= self.__onActionButtonClick
        del self.__bonuses[:]
        self.__items.clear()
        RankedSoundManager().setOverlayStateOff()
        super(RankedYearAwardView, self)._finalize()

    def _onLoading(self, rawAwards, points, showRemainedSelection):
        super(RankedYearAwardView, self)._onLoading()
        selectableRewardCount = self.__rankedController.getYearRewardCount()
        self.__removeSelectableYearRewards(rawAwards, int(selectableRewardCount == 0))
        self.__bonuses = getFormattedBonusesForYearAwardsWindow(rawAwards, selectionsLeft=selectableRewardCount)
        self.__points = points
        self.__showRemainedSelection = showRemainedSelection
        self.__setBonuses(self.__bonuses)
        self.__setViewData(self.__points)

    def __onDestroy(self, _=None):
        self.destroyWindow()

    def __setViewData(self, points):
        awardType = self.__rankedController.getAwardTypeByPoints(points)
        if awardType is None:
            awardType = YEAR_AWARDS_ORDER[0]
            _logger.warning("The number of points doesn't correspond to the award type")
        if self.__vehicleCD is not None:
            activeLabel = R.strings.ranked_battles.year_award.acceptButton.hangarLabel()
        else:
            activeLabel = R.strings.ranked_battles.year_award.acceptButton.acceptLabel()
        surplusPoints = self.__rankedController.getCompensation(points)
        rate = self.__rankedController.getCurrentPointToCrystalRate()
        with self.viewModel.transaction() as tx:
            tx.setAwardType(awardType)
            tx.setActionButtonLabel(activeLabel)
            if surplusPoints and rate:
                tx.setPointsTotal(points)
                tx.setPointsCompensated(surplusPoints)
                tx.setCrystals(rate * surplusPoints)
            tx.setIsRewardSelected(self.__showRemainedSelection)
            tx.setRewardsToSelect(self.__rankedController.getYearRewardCount())
        return

    def __setBonuses(self, bonuses):
        with self.getViewModel().transaction() as tx:
            vmRewardsList = tx.getRewards()
            vmRewardsList.clear()
            for index, reward in enumerate(bonuses):
                formatter = getRewardRendererModelPresenter(reward, presenters=RANKED_MODEL_PRESENTERS)
                showCongrats = False
                if reward.get('bonusName', '') == 'vehicles':
                    showCongrats = True
                    specialArgs = reward.get('specialArgs', None)
                    if specialArgs:
                        self.__vehicleCD = specialArgs[0]
                rewardRender = formatter.getModel(reward, index, showCongrats=showCongrats)
                vmRewardsList.addViewModel(rewardRender)
                self.__items[index] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))

            vmRewardsList.invalidate()
        return

    def __onActionButtonClick(self, _=None):
        if self.__vehicleCD is not None:
            event_dispatcher.selectVehicleInHangar(self.__vehicleCD)
            event_dispatcher.showHangar()
        self.viewModel.setStartClose(True)
        return

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            return self.__items[tooltipId] if tooltipId in self.__items else None

    @staticmethod
    def __removeSelectableYearRewards(rawAwards, count):
        selectableTokens = [ token for token in rawAwards.get('tokens', {}) if token.startswith(YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX) ]
        for token in selectableTokens:
            rewardCount = rawAwards['tokens'][token].get('count', 0) - count
            if rewardCount > 0:
                rawAwards['tokens'][token]['count'] = rewardCount
            elif rewardCount == 0:
                rawAwards['tokens'].pop(token)
            if not rawAwards['tokens']:
                rawAwards.pop('tokens')


class RankedYearAwardWindow(LobbyNotificationWindow):
    __slots__ = ('__args',)

    def __init__(self, rawAwards, points, showRemainedSelection):
        super(RankedYearAwardWindow, self).__init__(content=RankedYearAwardView(R.views.lobby.ranked.ranked_year_award.RankedYearAward(), rawAwards, points, showRemainedSelection), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN)
        self.__args = (rawAwards, points)

    def isParamsEqual(self, *args):
        return self.__args == args
