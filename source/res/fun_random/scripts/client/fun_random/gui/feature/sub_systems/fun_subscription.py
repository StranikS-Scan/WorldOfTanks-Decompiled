# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_systems/fun_subscription.py
import typing
from Event import SuspendedEventManager, SuspendedEvent
from fun_random.gui.shared import g_funEventBus
from fun_random.gui.shared.events import EventBridge, FunEventScope, FunEventType
from gui.shared import events, EVENT_BUS_SCOPE
from skeletons.gui.game_control import IFunRandomController
if typing.TYPE_CHECKING:
    from gui.shared.event_bus import SharedEvent

class FunSubscription(IFunRandomController.IFunSubscription):

    def __init__(self):
        super(FunSubscription, self).__init__()
        self.__em = SuspendedEventManager()
        self.__handleEvent = SuspendedEvent(self.__em)
        self.__handleEvent += g_funEventBus.handleEvent
        self.__eventsBridges = ((events.AmmunitionInjectEvent(events.AmmunitionInjectEvent.INVALIDATE_INJECT_VIEW),
          EVENT_BUS_SCOPE.LOBBY,
          self.__addSubModesListener,
          (True,),
          {}),
         (events.BoostersControllerEvent(events.BoostersControllerEvent.UPDATE_GAMEMODE_STATUS),
          EVENT_BUS_SCOPE.LOBBY,
          self.__addSubModesListener,
          (True,),
          {}),
         (events.GameSessionEvent(events.GameSessionEvent.UPDATE_KICK_NOTIFICATION),
          EVENT_BUS_SCOPE.LOBBY,
          self.__addSubModesListener,
          (True,),
          {}),
         (events.DailyQuestWidgetEvent(events.DailyQuestWidgetEvent.UPDATE_QUESTS_VISIBILITY),
          EVENT_BUS_SCOPE.LOBBY,
          self.__addSubModesListener,
          (True,),
          {}),
         (events.HangarEvent(events.HangarEvent.UPDATE_ALERT_MESSAGE),
          EVENT_BUS_SCOPE.LOBBY,
          self.__addSubModesListener,
          (True, True),
          {}),
         (events.HangarEvent(events.HangarEvent.UPDATE_PREBATTLE_ENTITY),
          EVENT_BUS_SCOPE.LOBBY,
          self.__addSubModesListener,
          (True,),
          {}),
         (events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.UPDATE_PREBATTLE_CONTROLS),
          EVENT_BUS_SCOPE.LOBBY,
          self.__addSubModesListener,
          (True,),
          {}),
         (events.MissionsViewEvent(events.MissionsViewEvent.EVENTS_FULL_UPDATE),
          EVENT_BUS_SCOPE.LOBBY,
          self.__addSubModesListener,
          (),
          {}))

    def fini(self):
        self.__eventsBridges = ()
        self.__handleEvent -= g_funEventBus.handleEvent
        self.__em.clear()

    def clear(self):
        g_funEventBus.clear()

    def resume(self):
        self.__em.resume()

    def suspend(self):
        self.__em.suspend()

    def addListener(self, eventType, handler, scope=FunEventScope.DEFAULT):
        g_funEventBus.addListener(eventType, handler, scope)

    def removeListener(self, eventType, handler, scope=FunEventScope.DEFAULT):
        g_funEventBus.removeListener(eventType, handler, scope)

    def handleEvent(self, event, scope=FunEventScope.DEFAULT):
        self.__handleEvent(event, scope)

    def startCoreNotifications(self):
        for event, scope, bridgeMaker, bridgeArgs, bridgeKwargs in self.__eventsBridges:
            bridgeMaker(EventBridge(event, scope), *bridgeArgs, **bridgeKwargs)

    def __addSubModesListener(self, method, desiredOnly=False, withTicks=False):
        scope = FunEventScope.DESIRABLE if desiredOnly else FunEventScope.DEFAULT
        self.addListener(FunEventType.SUB_SELECTION, method)
        self.addListener(FunEventType.SUB_SETTINGS, method, scope=scope)
        self.addListener(FunEventType.SUB_STATUS_UPDATE, method, scope=scope)
        if withTicks:
            self.addListener(FunEventType.SUB_STATUS_TICK, method, scope=scope)
