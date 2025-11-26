# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/daily_quest_widget.py
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from BonusCaps import BonusCapsConst
from constants import DAILY_QUESTS_CONFIG
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.prb_control.entities.listener import IGlobalListener
from gui.impl.lobby.missions.daily_quests_widget_view import DailyQuestsWidgetView
from gui.Scaleform.daapi.view.meta.DailyQuestMeta import DailyQuestMeta
from gui.Scaleform.managers import UtilsManager
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.server_settings import serverSettingsChangeListener
from skeletons.gui.game_control import IPromoController, ILimitedUIController, IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Type, List

class BaseQuestsWidgetComponent(object):
    injectQuestsWidgetViewType = DailyQuestsWidgetView
    __eventsCache = dependency.descriptor(IEventsCache)
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __promoController = dependency.descriptor(IPromoController)
    __slots__ = ('__timer', '_injector')

    def __init__(self, dailyQuestWidget):
        self.__timer = None
        self._injector = dailyQuestWidget
        return

    def populateQuestsWidgetComponent(self):
        self.__addListeners()
        self.__timer = CallbackDelayer()
        self.__showOrHide()

    def disposeOfQuestsWidgetComponent(self):
        self.__timer.clearCallbacks()
        self.__removeListeners()
        self._injector = None
        return

    @classmethod
    def shouldComponentBeActive(cls):
        return True

    def updateQuestsVisibility(self, *_):
        if self.__isQueueEnabled():
            self.__showOrHide()
        else:
            self.__animateHide()

    def _hasIncompleteQuests(self):
        for quest in self.__eventsCache.getDailyQuests().itervalues():
            if not quest.isCompleted():
                return True

        return False

    def _injectAndSetVisibilityOfWidgetView(self):
        injector = self._injector
        view = injector.createInjectView()
        view.setVisible(True)
        view.getViewModel().onDisappear += injector.destroyQuestsWidgetView

    def _delayedShowOrHide(self):
        self.__timer.delayCallback(UtilsManager.ONE_SECOND, self.__showOrHide)

    def _executeShowOrHide(self):
        injector = self._injector
        if injector is None:
            return
        else:
            isEnabled = False
            if self._shouldHide():
                injector.destroyQuestsWidgetView()
            elif self._hasIncompleteQuests() or self.__hasQuestStatusChanged():
                isEnabled = True
                self._injectAndSetVisibilityOfWidgetView()
            injector.as_setEnabledS(isEnabled)
            return

    def _shouldHide(self):
        return True

    def _onSyncCompleted(self):
        self.__showOrHide()

    def __isQueueEnabled(self):
        return self.__hangarGuiCtrl.dynamicEconomics.checkCurrentBonusCaps(ARENA_BONUS_TYPE_CAPS.DAILY_QUESTS)

    def __isQueueSelected(self, queueType):
        injector = self._injector
        return False if injector.prbDispatcher is None else injector.prbDispatcher.getFunctionalState().isQueueSelected(queueType)

    def __animateHide(self):
        injector = self._injector
        view = injector.getInjectView()
        if view:
            view.setVisible(False)
        injector.as_setEnabledS(False)

    def __showOrHide(self):
        if not self.__timer.hasDelayedCallback(self._executeShowOrHide):
            self.__timer.delayCallback(0.0, self._executeShowOrHide)

    def __hasQuestStatusChanged(self):
        for quest in self.__eventsCache.getDailyQuests().itervalues():
            if self.__eventsCache.questsProgress.getQuestCompletionChanged(quest.getID()):
                return True

        return False

    def __isLimitedUiRuleCompleted(self):
        return self.__limitedUIController.isRuleCompleted(LUI_RULES.DailyMissions)

    @serverSettingsChangeListener(BonusCapsConst.CONFIG_NAME, DAILY_QUESTS_CONFIG)
    def __onServerSettingsChanged(self, _):
        self.__showOrHide()

    def __onTeaserClosed(self):
        self._delayedShowOrHide()

    def __onTeaserShown(self):
        self.__timer.stopCallback(self.__showOrHide)
        self.__showOrHide()

    def __addListeners(self):
        injector = self._injector
        injector.startGlobalListening()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__eventsCache.onSyncCompleted += self._onSyncCompleted
        self.__promoController.onTeaserShown += self.__onTeaserShown
        self.__promoController.onTeaserClosed += self.__onTeaserClosed
        self.__limitedUIController.startObserve(LUI_RULES.DailyMissions, self.updateQuestsVisibility)
        injector.addListener(events.DailyQuestWidgetEvent.UPDATE_QUESTS_VISIBILITY, self.updateQuestsVisibility, EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        injector = self._injector
        injector.stopGlobalListening()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.__promoController.onTeaserShown -= self.__onTeaserShown
        self.__promoController.onTeaserClosed -= self.__onTeaserClosed
        self.__limitedUIController.stopObserve(LUI_RULES.DailyMissions, self.updateQuestsVisibility)
        injector.removeListener(events.DailyQuestWidgetEvent.UPDATE_QUESTS_VISIBILITY, self.updateQuestsVisibility, EVENT_BUS_SCOPE.LOBBY)
        view = injector.getInjectView()
        if view:
            view.getViewModel().onDisappear -= injector.destroyQuestsWidgetView


class DailyQuestWidget(InjectComponentAdaptor, DailyQuestMeta, IGlobalListener):
    COMPONENT_TYPES = []

    def __init__(self):
        self.__component = None
        super(DailyQuestWidget, self).__init__()
        return

    def updateWidgetLayout(self, value):
        view = self.getInjectView()
        if view:
            view.setLayout(value)

    def onPrbEntitySwitched(self):
        oldComponent = self.__component
        newComponentType = self.__getActiveComponentType()
        if type(oldComponent) is newComponentType:
            oldComponent.updateQuestsVisibility()
            return
        else:
            self.destroyQuestsWidgetView()
            oldComponent.disposeOfQuestsWidgetComponent()
            self.__component = None
            newComponent = newComponentType(self)
            newComponent.populateQuestsWidgetComponent()
            self.__component = newComponent
            return

    def createInjectView(self):
        view = self.getInjectView()
        if view:
            return view
        self._createInjectView()
        return self.getInjectView()

    def destroyQuestsWidgetView(self):
        view = self.getInjectView()
        if view:
            view.getViewModel().onDisappear -= self.destroyQuestsWidgetView
            self._destroyInjected()

    def _populate(self):
        super(DailyQuestWidget, self)._populate()
        componentType = self.__getActiveComponentType()
        self.__component = componentType(self)
        self.__component.populateQuestsWidgetComponent()

    def _onPopulate(self):
        pass

    def _dispose(self):
        self.__component.disposeOfQuestsWidgetComponent()
        self.__component = None
        super(DailyQuestWidget, self)._dispose()
        return

    def _makeInjectView(self):
        return self.__component.injectQuestsWidgetViewType()

    @classmethod
    def __getActiveComponentType(cls):
        for componentType in cls.COMPONENT_TYPES:
            if componentType.shouldComponentBeActive():
                return componentType

        return BaseQuestsWidgetComponent
