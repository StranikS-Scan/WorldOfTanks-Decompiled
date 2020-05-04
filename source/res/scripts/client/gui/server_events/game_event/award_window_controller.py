# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/award_window_controller.py
from functools import partial
from itertools import chain
from weakref import proxy
import gui.shared
from constants import QUEUE_TYPE
from gui.prb_control import prbEntityProperty
from gui.shared.events import GUICommonEvent
from gui.shared.utils import isPopupsWindowsOpenDisabled
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.server_events import IEventsCache
from skeletons.se20 import ICustomizableObjectsManager
from gui.server_events.game_event import BattleResultsOpenMixin
from skeletons.gui.shared import IItemsCache

class GameEventAwardWindowController(CallbackDelayer, BattleResultsOpenMixin):
    settingsCore = dependency.descriptor(ISettingsCore)
    eventsCache = dependency.descriptor(IEventsCache)
    customizableObjectsManager = dependency.descriptor(ICustomizableObjectsManager)
    itemsCache = dependency.descriptor(IItemsCache)
    _CALLBACK_SHOW_AWARD_WAIT_TIME = 2
    _TANK_DISCONT_MASK = 'se20_tank_discount'

    def __init__(self, gameEventController):
        super(GameEventAwardWindowController, self).__init__()
        self._lobbyInited = False
        self._inEventHangar = False
        self._gameEventController = proxy(gameEventController)
        self._messages = []
        self._awardTankCD = None
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    @property
    def isInQueue(self):
        return self.prbEntity and self.prbEntity.isInQueue()

    def start(self):
        self._lobbyInited = False
        self._inEventHangar = False
        self._gameEventController.onProgressChanged += self._onProgressChanged
        self.eventsCache.onSyncCompleted += self._onProgressChanged
        gui.shared.g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self._onLobbyInited)

    def stop(self):
        self._lobbyInited = False
        self._inEventHangar = False
        self._gameEventController.onProgressChanged -= self._onProgressChanged
        self.eventsCache.onSyncCompleted -= self._onProgressChanged
        gui.shared.g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self._onLobbyInited)
        self.customizableObjectsManager.onPrbEntityChanged -= self._onPrbEntityChanged
        self.destroy()

    def _onLobbyInited(self, _):
        self._lobbyInited = True
        self.customizableObjectsManager.onPrbEntityChanged += self._onPrbEntityChanged

    def _onPrbEntityChanged(self, queueType):
        self._inEventHangar = queueType == QUEUE_TYPE.EVENT_BATTLES
        self._messages = []
        if self._lobbyInited:
            self.delayCallback(self._CALLBACK_SHOW_AWARD_WAIT_TIME, self._onProgressChanged)

    def _onProgressChanged(self):
        if self._lobbyInited and not self._inEventHangar and not self.isInQueue and not self.isBattleResultsOpen:
            self.__showAwardWindow(heroTankAwardScreen=True)
        elif not self._inEventHangar or self._messages or self.isInQueue or self.isBattleResultsOpen or isPopupsWindowsOpenDisabled():
            self.delayCallback(self._CALLBACK_SHOW_AWARD_WAIT_TIME, self._onProgressChanged)
        else:
            self.stopCallback(self._onProgressChanged)
            self._messages = self._getMessages()
            self.__showAwardWindow()

    def _getMessages(self):
        return list(chain(self._getFrontAwards(), self._getCommanderAwards()))

    def _getCommanderAwards(self):
        for commander in self._gameEventController.getCommanders().itervalues():
            items = []
            for item in commander.getItems():
                level = item.getLevel()
                if level and not commander.isLevelAwardShown(level) and item.isCompleted():
                    items.append((level, item))

            if items:
                _, item = items[-1]
                yield {'name': 'general',
                 'contextObject': {'progress': commander,
                                   'item': item},
                 'bonuses': item.getBonuses(),
                 'setShown': partial(commander.setLevelAwardIsShown, *(level for level, _ in items)),
                 'flag': {'commander': commander,
                          'item': item}}

    def _getVehicleFromBonuses(self, item):
        vehicle = first(item.getBonuses('vehicles'))
        if vehicle:
            vehicle, _ = first(vehicle.getVehicles())
            return vehicle
        else:
            return None

    def _getFrontAwards(self, filterFunc=None):
        front = self._gameEventController.getCurrentFront()
        if front is not None:
            items = front.getItems()
            if filterFunc:
                items = (item for item in items if filterFunc(item))
            for item in items:
                level = item.getLevel()
                if level and not front.isAwardShown(level) and item.isCompleted():
                    bonuses = item.getBonuses()
                    vehicle = self._getVehicleFromBonuses(item)
                    result = {'name': 'front',
                     'contextObject': {'progress': front,
                                       'item': item},
                     'bonuses': bonuses,
                     'setShown': partial(front.setAwardIsShown, level)}
                    if vehicle:
                        self._awardTankCD = vehicle.intCD
                        result['contextObject']['vehicle'] = vehicle
                        result['name'] = 'vehicle'
                        result['bonuses'] = item.getBonuses()
                        result['onButton'] = partial(gui.shared.event_dispatcher.selectVehicleInHangar, vehicle.intCD)
                    yield result

        return

    def __filterBonuses(self, bonuses):
        for bonus in bonuses:
            name = bonus.getName()
            if name == 'vehicles':
                continue
            elif name == 'battleToken':
                if any((x.find(self._TANK_DISCONT_MASK) != -1 for x in bonus.getTokens())):
                    continue
            yield bonus

    def __showAwardWindow(self, heroTankAwardScreen=False):
        self.stopCallback(self.__showAwardWindow)
        if heroTankAwardScreen:
            self._messages = list(self._getFrontAwards(self._getVehicleFromBonuses))
        if self._messages:
            if self._awardTankCD:
                if not self.itemsCache.items.getItemByCD(self._awardTankCD).isInInventory:
                    self.delayCallback(self._CALLBACK_SHOW_AWARD_WAIT_TIME, self.__showAwardWindow, heroTankAwardScreen=heroTankAwardScreen)
                    return
            from gui.server_events import events_dispatcher
            events_dispatcher.showEventAwardScreen(self._messages)
        self._awardTankCD = None
        return
