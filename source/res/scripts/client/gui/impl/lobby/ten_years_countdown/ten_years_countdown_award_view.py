# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ten_years_countdown/ten_years_countdown_award_view.py
import logging
import WWISE
from constants import IS_CHINA
from frameworks.wulf import ViewSettings
from frameworks.wulf import WindowFlags
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent, getRewardRendererModelPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.ten_years_countdown_award_model import TenYearsCountdownAwardModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.backport import BackportTooltipWindow, TooltipData
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from gui.impl.auxiliary.rewards_helper import TEN_YEARS_MODEL_PRESENTER
from ten_year_countdown_config import EVENT_BADGE_MISSION_ID, EVENT_STYLE_MISSION_ID, TEN_YEAR_COUNTDOWN_QUEST_TOKEN_PREFIX, TEN_YEAR_COUNTDOWN_QUEST_TOKEN_POSTFIX
from gui.Scaleform.daapi.view.lobby.ten_years_event.ten_years_event_sound_controller import TenYearsEventSounds
_logger = logging.getLogger(__name__)

class TenYearsCountdownAwardView(ViewImpl):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __slots__ = ('__items', '__bonuses', '__closeCallback', '__specialRewardType')

    def __init__(self, specialRewardType, contentResId, *args, **kwargs):
        settings = ViewSettings(contentResId)
        settings.model = TenYearsCountdownAwardModel()
        settings.args = args
        settings.kwargs = kwargs
        super(TenYearsCountdownAwardView, self).__init__(settings)
        self.__items = {}
        self.__bonuses = []
        self.__closeCallback = None
        self.__specialRewardType = specialRewardType
        return

    @property
    def viewModel(self):
        return super(TenYearsCountdownAwardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(TenYearsCountdownAwardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def _initialize(self, rawAwards, closeCallback):
        super(TenYearsCountdownAwardView, self)._initialize()
        self.viewModel.onDestroyEvent += self.__onDestroy
        self.viewModel.onActionBtnClick += self.__onActionButtonClick
        self.__closeCallback = closeCallback
        WWISE.WW_eventGlobal(TenYearsEventSounds.EV_10Y_COUNTDOWN_AWARD_SCREEN)

    def _finalize(self):
        self.viewModel.onDestroyEvent -= self.__onDestroy
        self.viewModel.onActionBtnClick -= self.__onActionButtonClick
        del self.__bonuses[:]
        self.__items.clear()
        if self.__closeCallback is not None and callable(self.__closeCallback):
            self.__closeCallback()
        super(TenYearsCountdownAwardView, self)._finalize()
        return

    def _onLoading(self, rawAwards, closeCallback):
        super(TenYearsCountdownAwardView, self)._onLoading()
        self.__bonuses = rawAwards
        self.__setBonuses(self.__bonuses)

    def __onDestroy(self, _=None):
        self.destroyWindow()

    def __setBonuses(self, bonuses):
        with self.getViewModel().transaction() as tx:
            if self.__specialRewardType.startswith(EVENT_BADGE_MISSION_ID):
                title = R.strings.ten_year_countdown.awardView.title.badge()
            elif self.__specialRewardType.startswith(EVENT_STYLE_MISSION_ID):
                title = R.strings.ten_year_countdown.awardView.title.style()
                if IS_CHINA:
                    title = R.strings.ten_year_countdown.awardView.title_CN.style()
            elif self.__specialRewardType.startswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_PREFIX) and self.__specialRewardType.endswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_POSTFIX):
                title = R.strings.ten_year_countdown.awardView.title.token()
            else:
                title = R.invalid()
            tx.setTitle(title)
            vmRewardsList = tx.getRewards()
            vmRewardsList.clear()
            for index, reward in enumerate(bonuses):
                if self.__specialRewardType.startswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_PREFIX) and self.__specialRewardType.endswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_POSTFIX):
                    rewardtype = {'bonusName': 'tokens'}
                elif self.__specialRewardType.startswith(EVENT_BADGE_MISSION_ID):
                    rewardtype = {'bonusName': 'dossier'}
                elif self.__specialRewardType.startswith(EVENT_STYLE_MISSION_ID):
                    rewardtype = {'bonusName': 'customizations'}
                else:
                    continue
                formatter = getRewardRendererModelPresenter(rewardtype, presenters=TEN_YEARS_MODEL_PRESENTER)
                showCongrats = self.__specialRewardType.startswith(EVENT_BADGE_MISSION_ID) or self.__specialRewardType.startswith(EVENT_STYLE_MISSION_ID) or self.__specialRewardType.startswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_PREFIX) and self.__specialRewardType.endswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_POSTFIX)
                rewardRender = formatter.getModel(reward, index, showCongrats=showCongrats)
                vmRewardsList.addViewModel(rewardRender)
                self.__items[index] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))

            vmRewardsList.invalidate()
        return

    def __onActionButtonClick(self, _=None):
        self.viewModel.setStartClose(True)

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            return self.__items[tooltipId] if tooltipId in self.__items else None


class TenYearsCountdownAwardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, rawAwards, specialRewardType, closeCallback=None):
        super(TenYearsCountdownAwardWindow, self).__init__(content=TenYearsCountdownAwardView(specialRewardType, R.views.lobby.ten_years_countdown.ten_years_countdown_award.TenYearsCountdownAward(), rawAwards, closeCallback), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return
