# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/quests_view.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport.backport_tooltip import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.rts.quests_view_model import QuestsViewModel, State
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModel
from gui.impl.lobby.rts.rts_i_tab_view import ITabView
from gui.impl.lobby.rts.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.lobby.rts.tooltips.tooltip_helpers import createRTSCurrencyTooltipView
from gui.impl.pub import ViewImpl, ToolTipWindow
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.server_events.bonuses import splitBonuses
from gui.server_events.events_helpers import EventInfoModel, rtsQuestsSortFunc
from gui.shared.missions.packers.events import RtsQuestUIDataPacker
from helpers import dependency
from helpers.time_utils import getTimeDeltaFromNowInLocal
from skeletons.gui.game_control import IRTSBattlesController, IRTSProgressionController
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent, Window
_logger = logging.getLogger(__name__)

class QuestsView(ViewImpl, ITabView):
    __slots__ = ('_bonusTooltipData', '_conditionTooltipData')
    _rtsController = dependency.descriptor(IRTSBattlesController)
    _progressionCtrl = dependency.instance(IRTSProgressionController)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = QuestsViewModel()
        self._bonusTooltipData = {}
        self._conditionTooltipData = {}
        super(QuestsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(QuestsView, self).getViewModel()

    def createToolTip(self, event):
        content = None
        window = None
        contentId = event.contentID
        tooltipData = None
        tooltipId = event.getArgument('tooltipId', None)
        if tooltipId is not None and tooltipId not in self._conditionTooltipData:
            tooltipData = self._bonusTooltipData.get(int(tooltipId), None)
            if not tooltipData:
                _logger.warning('[QuestsView] Tooltip data is missing for tooltip id %s.', tooltipId)
        if contentId == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent() and tooltipData:
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
        elif contentId == R.views.lobby.rts.StrategistCurrencyTooltip() and tooltipData:
            arg = tooltipData.specialArgs[0]
            content = createRTSCurrencyTooltipView(contentId, arg)
        elif contentId == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            questId = event.getArgument('questId', '')
            if not questId:
                return
            showCount = int(event.getArgument('showCount'))
            bonuses = splitBonuses(self._progressionCtrl.getQuestRewards(questId))[showCount:]
            content = AdditionalRewardsTooltip(bonuses, RtsQuestUIDataPacker.getBonusPacker())
        elif contentId == R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent() and tooltipId in self._conditionTooltipData:
            tooltipData = self._conditionTooltipData[tooltipId]
            resId = tooltipData[0]
            if len(tooltipData) > 1:
                body = backport.text(resId, **tooltipData[1])
            else:
                body = backport.text(resId)
            content = SimpleTooltipContent(contentId, body=body)
        else:
            return super(QuestsView, self).createToolTip(event)
        if content:
            window = ToolTipWindow(event, content, self.getParentWindow())
            window.move(event.mouse.positionX, event.mouse.positionY)
        if window:
            window.load()
        return window

    def _initialize(self):
        super(QuestsView, self)._initialize()
        self._eventsCache.onSyncCompleted += self._onSyncCompleted
        self._progressionCtrl.onUpdated += self._onControllerUpdated

    def _finalize(self):
        self._eventsCache.onSyncCompleted -= self._onSyncCompleted
        self._progressionCtrl.onUpdated -= self._onControllerUpdated
        super(QuestsView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        self._updateViewModel()

    def _onSyncCompleted(self):
        quests = self._progressionCtrl.getQuests()
        if needToUpdateQuestsInModel(quests, self.viewModel.getQuests()):
            self._updateViewModel()

    def _onControllerUpdated(self):
        self._setState(self.viewModel)

    def _setState(self, model):
        isEnabled = self._progressionCtrl.isEnabled() and self._rtsController.isAvailable()
        if not isEnabled:
            newState = State.EVENT_ENDED
        else:
            newState = self._getQuestsState(model)
        currentState = model.getState()
        if newState != currentState:
            model.setState(newState)

    def _getQuestsState(self, model):
        quests = model.getQuests()
        if not quests:
            return State.ERROR
        dailyResetTimeDelta = self._getCountdownUntilNextDay()
        questsAvailableNextDay = False
        for quest in quests:
            finishTimeLeft = getTimeDeltaFromNowInLocal(quest.getFinishDate())
            questsAvailableNextDay |= finishTimeLeft - dailyResetTimeDelta > 0
            if quest.getTotalCount() != quest.getCompletedCount():
                return State.QUESTS_AVAILABLE

        return State.QUESTS_FINISHED if questsAvailableNextDay else State.EVENT_ENDED

    def _updateViewModel(self):
        quests = self._progressionCtrl.getQuests()
        self._bonusTooltipData.clear()
        self._conditionTooltipData.clear()
        with self.viewModel.transaction() as model:
            questsArray = model.getQuests()
            questsArray.clear()
            questsArray.reserve(len(quests))
            for quest in sorted(quests, key=rtsQuestsSortFunc):
                packer = RtsQuestUIDataPacker(quest, tooltipData=self._bonusTooltipData)
                questsArray.addViewModel(packer.pack())
                packer.getConditionTooltipData(self._conditionTooltipData)

            questsArray.invalidate()
            self._setState(model)
            model.setCountdown(self._getCountdownUntilNextDay())

    def _getCountdownUntilNextDay(self):
        return int(EventInfoModel.getDailyProgressResetTimeDelta())
