# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/daily_quest_widget.py
import logging
import typing
from constants import QUEUE_TYPE
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events.events_helpers import isDailyQuestsEnable
from gui.impl.lobby.missions.daily_quests_widget_view import DailyQuestsWidgetView
from gui.Scaleform.daapi.view.meta.DailyQuestMeta import DailyQuestMeta
from gui.Scaleform.managers import UtilsManager
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.game_control import IPromoController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Any
_logger = logging.getLogger(__name__)

class DailyQuestWidget(InjectComponentAdaptor, DailyQuestMeta, IGlobalListener):
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsCache = dependency.descriptor(IEventsCache)
    promoController = dependency.descriptor(IPromoController)
    __layout = 0

    def updateWidgetLayout(self, value):
        self.__layout = value
        if self._injectView is not None:
            self._injectView.setLayout(self.__layout)
        return

    def onPrbEntitySwitched(self):
        if not (self._isRandomBattleSelected() or self._isMapboxSelected()):
            self._animateHide()
        else:
            self._showOrHide()

    def _populate(self):
        super(DailyQuestWidget, self)._populate()
        self.__addListeners()
        self._timer = CallbackDelayer()
        self._showOrHide()

    def _onPopulate(self):
        pass

    def _dispose(self):
        self._timer.clearCallbacks()
        self.__removeListeners()
        super(DailyQuestWidget, self)._dispose()

    def _makeInjectView(self):
        return DailyQuestsWidgetView()

    def _isRandomBattleSelected(self):
        return self.__isQueueSelected(QUEUE_TYPE.RANDOMS)

    def _isMapboxSelected(self):
        return self.__isQueueSelected(QUEUE_TYPE.MAPBOX)

    def __isQueueSelected(self, queueType):
        return self.prbDispatcher.getFunctionalState().isQueueSelected(queueType) if self.prbDispatcher is not None else False

    def _show(self):
        if self._injectView is None:
            self._createInjectView()
        self._injectView.setVisible(True)
        self._injectView.viewModel.onDisappear += self._hide
        return

    def _animateHide(self):
        if self._injectView is not None:
            self._injectView.setVisible(False)
        return

    def _hide(self):
        if self._injectView is not None:
            self._injectView.viewModel.onDisappear -= self._hide
        self._destroyInjected()
        return

    def __delayedShowOrHide(self):
        self._timer.delayCallback(UtilsManager.ONE_SECOND, self._showOrHide)

    def _showOrHide(self):
        if not self._timer.hasDelayedCallback(self._executeShowOrHide):
            self._timer.delayCallback(0.0, self._executeShowOrHide)

    def _executeShowOrHide(self):
        if self._shouldHide():
            self._hide()
            return
        if self.__hasIncompleteQuests() or self._hasQuestStatusChanged():
            self._show()

    def _shouldHide(self):
        return not isDailyQuestsEnable() or self.promoController.isTeaserOpen() or not (self._isRandomBattleSelected() or self._isMapboxSelected())

    def __hasIncompleteQuests(self):
        for quest in self._getQuests():
            if not quest.isCompleted():
                return True

        return False

    def _hasQuestStatusChanged(self):
        for quest in self._getQuests():
            if self.eventsCache.questsProgress.getQuestCompletionChanged(quest.getID()):
                return True

        return False

    def __onServerSettingsChanged(self, _):
        self._showOrHide()

    def __onTeaserClosed(self):
        self.__delayedShowOrHide()

    def __onTeaserShown(self):
        self._timer.stopCallback(self._showOrHide)
        self._showOrHide()

    def __onSyncCompleted(self):
        self._showOrHide()

    def __addListeners(self):
        self.startGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.promoController.onTeaserShown += self.__onTeaserShown
        self.promoController.onTeaserClosed += self.__onTeaserClosed

    def __removeListeners(self):
        self.stopGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.promoController.onTeaserShown -= self.__onTeaserShown
        self.promoController.onTeaserClosed -= self.__onTeaserClosed
        if self._injectView is not None:
            self._injectView.viewModel.onDisappear -= self._hide
        return

    def _getQuests(self):
        return self.eventsCache.getDailyQuests().values()
