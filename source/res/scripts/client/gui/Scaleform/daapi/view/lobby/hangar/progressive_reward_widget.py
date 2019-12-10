# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/progressive_reward_widget.py
import logging
from constants import SENIORITY_AWARDS_CONFIG
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PROGRESSIVE_REWARD_VISITED
from gui.Scaleform.daapi.view.meta.ProgressiveRewardWidgetMeta import ProgressiveRewardWidgetMeta
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getProgressiveRewardVO
from gui.impl.gen import R
from gui.shared import events
from gui.shared.event_dispatcher import showProgressiveRewardWindow, showSeniorityRewardWindow
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class ProgressiveRewardWidget(ProgressiveRewardWidgetMeta):
    _eventsCache = dependency.descriptor(IEventsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)

    def onWidgetClick(self):
        self.fireEvent(events.HidePopoverEvent(events.HidePopoverEvent.HIDE_POPOVER))
        showProgressiveRewardWindow()

    def onOpenBtnClick(self):
        showSeniorityRewardWindow()

    def _populate(self):
        super(ProgressiveRewardWidget, self)._populate()
        self._itemsCache.onSyncCompleted += self.__onItemsCacheSyncCompleted
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__update()
        wasVisited = AccountSettings.getNotifications(PROGRESSIVE_REWARD_VISITED)
        if not wasVisited:
            self.fireEvent(events.ProgressiveRewardEvent(events.ProgressiveRewardEvent.WIDGET_WAS_SHOWN))

    def _dispose(self):
        self._itemsCache.onSyncCompleted -= self.__onItemsCacheSyncCompleted
        self._eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        super(ProgressiveRewardWidget, self)._dispose()

    def __onSyncCompleted(self, *_):
        self.__update()

    def __onServerSettingsChange(self, diff):
        configs = {'progressive_reward_config', SENIORITY_AWARDS_CONFIG}
        if configs.intersection(diff):
            self.__update()

    def __onItemsCacheSyncCompleted(self, reason, diff):
        self.__update()

    def __update(self):
        pr = self._eventsCache.getProgressiveReward()
        if pr is None:
            _logger.warning('There is not info about progressive reward')
            self.as_setDataS({'isEnabled': False})
            return
        else:
            progressiveEnabled = self._lobbyContext.getServerSettings().getProgressiveRewardConfig().isEnabled
            if pr.currentStep >= pr.maxSteps:
                progressiveEnabled = False
                _logger.warning('Current step more than max step in progressive reward')
            descText = text_styles.main(backport.text(R.strings.menu.progressiveReward.widget.desc()))
            self.as_setDataS(getProgressiveRewardVO(currentStep=pr.currentStep, probability=pr.probability, maxSteps=pr.maxSteps, isEnabled=progressiveEnabled, showBg=False, descText=descText, showSeniorityAwards=True))
            return
