# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/ranked_year_award_view.py
import logging
from frameworks.wulf import ViewSettings
from frameworks.wulf import WindowFlags
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent, getRewardRendererModelPresenter, RANKED_MODEL_PRESENTERS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ranked.ranked_year_award_model import RankedYearAwardModel
from gui.ranked_battles.constants import YEAR_AWARDS_ORDER
from gui.ranked_battles.ranked_formatters import getFormattedBonusesForYearAwardsWindow
from gui.shared import event_dispatcher
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.ranked_battles.ranked_helpers.sound_manager import RankedSoundManager
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
_logger = logging.getLogger(__name__)

class RankedYearAwardView(ViewImpl):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __slots__ = ('__items', '__bonuses', '__points', '__vehicleCD', '__closeCallback')

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
        self.__closeCallback = None
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

    def _initialize(self, rawAwards, points, closeCallback):
        super(RankedYearAwardView, self)._initialize()
        self.viewModel.onDestroyEvent += self.__onDestroy
        self.viewModel.onActionBtnClick += self.__onActionButtonClick
        self.__closeCallback = closeCallback
        RankedSoundManager().setOverlayStateOn()

    def _finalize(self):
        self.viewModel.onDestroyEvent -= self.__onDestroy
        self.viewModel.onActionBtnClick -= self.__onActionButtonClick
        del self.__bonuses[:]
        self.__items.clear()
        RankedSoundManager().setOverlayStateOff()
        if self.__closeCallback is not None and callable(self.__closeCallback):
            self.__closeCallback()
        super(RankedYearAwardView, self)._finalize()
        return

    def _onLoading(self, rawAwards, points, closeCallback):
        super(RankedYearAwardView, self)._onLoading()
        self.__bonuses = getFormattedBonusesForYearAwardsWindow(rawAwards)
        self.__points = points
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
        surplusPoints = self.__rankedController.calculateCompensation(points)
        rate = self.__rankedController.getCurrentPointToCrystalRate()
        with self.viewModel.transaction() as tx:
            tx.setAwardType(awardType)
            tx.setActionButtonLabel(activeLabel)
            if surplusPoints and rate:
                tx.setPointsTotal(points)
                tx.setPointsCompensated(surplusPoints)
                tx.setCrystals(rate * surplusPoints)
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


class RankedYearAwardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, rawAwards, points, closeCallback):
        super(RankedYearAwardWindow, self).__init__(content=RankedYearAwardView(R.views.lobby.ranked.ranked_year_award.RankedYearAward(), rawAwards, points, closeCallback), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return
