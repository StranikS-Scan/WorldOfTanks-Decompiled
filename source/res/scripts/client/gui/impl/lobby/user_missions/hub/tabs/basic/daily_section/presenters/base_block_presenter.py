# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/daily_section/presenters/base_block_presenter.py
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.tab_id import TabId
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.lobby.user_missions.hub.update_children_mixin import UpdateChildrenMixin
from gui.impl.pub.view_component import ViewComponent
from gui.impl.pub.view_impl import TViewModel
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import UserMissionsEvent
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.server_events import IEventsCache

class BaseBlockPresenter(UpdateChildrenMixin, ViewComponent[TViewModel]):
    eventsCache = dependency.descriptor(IEventsCache)
    gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self, model):
        super(BaseBlockPresenter, self).__init__(model=model)
        self.__isInRequiredTab = True
        self._tooltipData = {}
        self._rewardsGetterByQuestID = {}

    def createToolTip(self, event):
        if event.contentID != R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            return super(BaseBlockPresenter, self).createToolTip(event)
        else:
            tooltipData = self._getTooltipData(event)
            if not tooltipData:
                return super(BaseBlockPresenter, self).createToolTip(event)
            if tooltipData and isinstance(tooltipData, TooltipData):
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event) if tooltipData is not None else None
                if window is not None:
                    window.load()
            else:
                window = super(BaseBlockPresenter, self).createToolTip(event)
            return window

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        elif contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showFromIndex = event.getArgument('showFromIndex')
            questId = event.getArgument('questId')
            getBonuses = self._rewardsGetterByQuestID.get(questId, None)
            if getBonuses is None:
                return
            return AdditionalRewardsTooltip(getBonuses()[int(showFromIndex):])
        else:
            return super(BaseBlockPresenter, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def isInRequiredTab(self):
        return self.__isInRequiredTab

    def _onLoaded(self, *_, **__):
        super(BaseBlockPresenter, self)._onLoaded()
        self._markQuestsAsVisited()

    def _getCallbacks(self):
        return (('tokens', self._onSyncCompleted),)

    def _getEvents(self):
        return ((self.eventsCache.onSyncCompleted, self._onSyncCompleted),)

    def _getListeners(self):
        return ((UserMissionsEvent.CHANGE_TAB, self.__onTabChange, EVENT_BUS_SCOPE.LOBBY),)

    def _getTooltipData(self, event):
        missionParam = event.getArgument('tooltipId', '')
        missionParams = missionParam.rsplit(':', 1)
        if len(missionParams) != 2:
            return self._tooltipData.get(missionParam)
        missionId, tooltipId = missionParams
        tooltipsData = self._tooltipData.get(missionId, {})
        return tooltipsData.get(tooltipId, {})

    def _markQuestsAsVisited(self):
        pass

    def _onLeaveTab(self):
        pass

    def _onSyncCompleted(self, *_):
        if self.__isInRequiredTab:
            self._markQuestsAsVisited()

    def _finalize(self):
        self._rewardsGetterByQuestID.clear()
        self._rewardsGetterByQuestID = None
        super(BaseBlockPresenter, self)._finalize()
        return

    def __onTabChange(self, ume):
        self.__isInRequiredTab = ume.tabID == TabId.BASIC
        if self.__isInRequiredTab:
            self._markQuestsAsVisited()
        else:
            self._onLeaveTab()
