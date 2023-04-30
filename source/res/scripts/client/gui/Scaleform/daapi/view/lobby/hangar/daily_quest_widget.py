# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/daily_quest_widget.py
import typing
from constants import QUEUE_TYPE, DAILY_QUESTS_CONFIG
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
        if not self._isQueueEnabled():
            self.__animateHide()
        else:
            self.__showOrHide()

    def _populate(self):
        super(DailyQuestWidget, self)._populate()
        self.__addListeners()
        self.__timer = CallbackDelayer()
        self.__showOrHide()

    def _onPopulate(self):
        pass

    def _dispose(self):
        self.__timer.clearCallbacks()
        self.__removeListeners()
        super(DailyQuestWidget, self)._dispose()

    def _makeInjectView(self):
        return DailyQuestsWidgetView()

    def _isQueueEnabled(self):
        enabledQueues = (QUEUE_TYPE.RANDOMS,
         QUEUE_TYPE.MAPBOX,
         QUEUE_TYPE.COMP7,
         QUEUE_TYPE.WINBACK)
        return any((self.__isQueueSelected(queueType) for queueType in enabledQueues))

    def __isQueueSelected(self, queueType):
        return self.prbDispatcher.getFunctionalState().isQueueSelected(queueType) if self.prbDispatcher is not None else False

    def __show(self):
        if self._injectView is None:
            self._createInjectView()
        self._injectView.setVisible(True)
        self._injectView.viewModel.onDisappear += self.__hide
        return

    def __animateHide(self):
        if self._injectView is not None:
            self._injectView.setVisible(False)
        self.as_setEnabledS(False)
        return

    def __hide(self):
        if self._injectView is not None:
            self._injectView.viewModel.onDisappear -= self.__hide
        self._destroyInjected()
        return

    def __delayedShowOrHide(self):
        self.__timer.delayCallback(UtilsManager.ONE_SECOND, self.__showOrHide)

    def __showOrHide(self):
        if not self.__timer.hasDelayedCallback(self.__executeShowOrHide):
            self.__timer.delayCallback(0.0, self.__executeShowOrHide)

    def __executeShowOrHide(self):
        isEnabled = False
        if self.__shouldHide():
            self.__hide()
        elif self.__hasIncompleteQuests() or self.__hasQuestStatusChanged():
            isEnabled = True
            self.__show()
        self.as_setEnabledS(isEnabled)

    def __shouldHide(self):
        return not isDailyQuestsEnable() or self.promoController.isTeaserOpen() or not self._isQueueEnabled()

    def __hasIncompleteQuests(self):
        for quest in self.eventsCache.getDailyQuests().values():
            if not quest.isCompleted():
                return True

        return False

    def __hasQuestStatusChanged(self):
        for quest in self.eventsCache.getDailyQuests().values():
            if self.eventsCache.questsProgress.getQuestCompletionChanged(quest.getID()):
                return True

        return False

    def __onServerSettingsChanged(self, diff):
        if DAILY_QUESTS_CONFIG in diff:
            self.__showOrHide()

    def __onTeaserClosed(self):
        self.__delayedShowOrHide()

    def __onTeaserShown(self):
        self.__timer.stopCallback(self.__showOrHide)
        self.__showOrHide()

    def __onSyncCompleted(self):
        self.__showOrHide()

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
            self._injectView.viewModel.onDisappear -= self.__hide
        return
