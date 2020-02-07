# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/daily_quest_widget.py
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
        if not self._isRandomBattleSelected():
            if self._injectView is not None:
                self._injectView.setIsVisible(False)
        else:
            self.__showOrHide()
        return

    def _populate(self):
        super(DailyQuestWidget, self)._populate()
        self.__addListeners()
        self.__timer = CallbackDelayer()
        self.__showOrHide()

    def _dispose(self):
        self.__timer.clearCallbacks()
        self.__removeListeners()
        super(DailyQuestWidget, self)._dispose()

    def _makeInjectView(self):
        return DailyQuestsWidgetView()

    def _isRandomBattleSelected(self):
        return self.prbDispatcher.getFunctionalState().isQueueSelected(QUEUE_TYPE.RANDOMS)

    def __show(self):
        self.as_showWidgetS()
        if self._injectView is not None:
            self._injectView.setIsVisible(True)
        return

    def __hide(self):
        self.as_hideWidgetS()
        if self._injectView is not None:
            self._injectView.setIsVisible(False)
        return

    def __delayedShowOrHide(self):
        self.__timer.delayCallback(UtilsManager.ONE_SECOND, self.__showOrHide)

    def __showOrHide(self):
        if self.__shouldHide():
            self.__hide()
            return
        if self.__hasUncompletedQuests():
            self.__show()

    def __shouldHide(self):
        return not isDailyQuestsEnable() or self.promoController.isTeaserOpen() or not self._isRandomBattleSelected()

    def __hasUncompletedQuests(self):
        for quest in self.eventsCache.getDailyQuests().values():
            if not quest.isCompleted():
                return True

        return False

    def __onServerSettingsChanged(self, diff):
        self.__showOrHide()

    def __onTeaserClosed(self):
        self.__delayedShowOrHide()

    def __onTeaserShown(self):
        self.__timer.stopCallback(self.__showOrHide)
        self.__showOrHide()

    def __onSyncCompleted(self):
        self.__showOrHide()

    def __onNothingToDisplay(self):
        if self.__shouldHide() or not self.__hasUncompletedQuests():
            self.__hide()

    def __addListeners(self):
        self.startGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.promoController.onTeaserShown += self.__onTeaserShown
        self.promoController.onTeaserClosed += self.__onTeaserClosed
        if self._injectView is not None:
            self._injectView.viewModel.onNothingToDisplay += self.__onNothingToDisplay
        return

    def __removeListeners(self):
        self.stopGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.promoController.onTeaserShown -= self.__onTeaserShown
        self.promoController.onTeaserClosed -= self.__onTeaserClosed
        if self._injectView is not None:
            self._injectView.viewModel.onNothingToDisplay -= self.__onNothingToDisplay
        return
