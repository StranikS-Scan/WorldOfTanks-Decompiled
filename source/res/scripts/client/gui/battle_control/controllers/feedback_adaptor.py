# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/feedback_adaptor.py
import weakref
import BigWorld
import Event
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET, BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
import feedback_events
_CELL_BLINKING_DURATION = 3.0

class _DamagedDevicesExtraFetcher(object):
    __slots__ = ('__total', '__critical', '__destroyed', '__isInFire')

    def __init__(self, total, critical, destroyed):
        super(_DamagedDevicesExtraFetcher, self).__init__()
        self.__total = map(self.__convertExtra, total)
        self.__critical = critical
        self.__destroyed = destroyed
        self.__isInFire = False

    def getDamagedDevices(self):
        for idx in self.__critical:
            name = self.__total[idx]
            if name == 'fire':
                self.__isInFire = True
                continue
            yield (name, 'damaged')

        for idx in self.__destroyed:
            yield (self.__total[idx], 'destroyed')

    def isInFire(self):
        return self.__isInFire

    @staticmethod
    def __convertExtra(extra):
        return extra.name


class BattleFeedbackAdaptor(IBattleController):
    """
    Class adapts some events from Avatar, Vehicle, ... to GUI event (FEEDBACK_EVENT_ID) to display
    response on player actions.
    """
    __slots__ = ('onPlayerFeedbackReceived', 'onPlayerSummaryFeedbackReceived', 'onPostmortemSummaryReceived', 'onVehicleMarkerAdded', 'onVehicleMarkerRemoved', 'onVehicleFeedbackReceived', 'onMinimapVehicleAdded', 'onMinimapVehicleRemoved', 'onDevelopmentInfoSet', 'onMinimapFeedbackReceived', '__isPEEnabled', '__arenaDP', '__visible', '__pending', '__attrs', '__weakref__', '__arenaVisitor', '__devInfo', '__eventsCache')

    def __init__(self, setup):
        super(BattleFeedbackAdaptor, self).__init__()
        self.__isPEEnabled = False
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__arenaVisitor = weakref.proxy(setup.arenaVisitor)
        self.__visible = set()
        self.__pending = {}
        self.__attrs = {}
        self.__devInfo = {}
        self.__eventsCache = {}
        self.onPlayerFeedbackReceived = Event.Event()
        self.onPlayerSummaryFeedbackReceived = Event.Event()
        self.onPostmortemSummaryReceived = Event.Event()
        self.onVehicleMarkerAdded = Event.Event()
        self.onVehicleMarkerRemoved = Event.Event()
        self.onVehicleFeedbackReceived = Event.Event()
        self.onMinimapVehicleAdded = Event.Event()
        self.onMinimapVehicleRemoved = Event.Event()
        self.onMinimapFeedbackReceived = Event.Event()
        self.onDevelopmentInfoSet = Event.Event()

    def getControllerID(self):
        return BATTLE_CTRL_ID.FEEDBACK

    def startControl(self):
        pass

    def stopControl(self):
        self.__visible.clear()
        while self.__pending:
            _, callbackID = self.__pending.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__isPEEnabled = False
        self.__arenaDP = None
        self.__arenaVisitor = None
        self.__attrs = {}
        self.__devInfo.clear()
        self.__eventsCache.clear()
        return

    def getCachedEvent(self, eventID):
        """
        Returns the last cached event or None.
        :param eventID: FEEDBACK_EVENT_ID
        """
        return self.__eventsCache.get(eventID, None)

    def setPlayerVehicle(self, vID):
        """
        Sets player's vehicle to adaptor, which determines whether the player's events are
        available on specified data.
        
        :param vID: long containing ID of player's vehicle. If value equals 0L than players events
                    is disabled.
        """
        if vID:
            self.__isPEEnabled = True
        else:
            self.__isPEEnabled = False

    def getVehicleProxy(self, vehicleID):
        """ Gets proxy of vehicle's entity if it is visible.
        :param vehicleID: long containing ID of vehicle.
        :return: proxy of vehicle's entity or None.
        """
        proxy = None
        if vehicleID in self.__visible:
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is not None:
                proxy = vehicle.proxy
        return proxy

    def getVisibleVehicles(self):
        getInfo = self.__arenaDP.getVehicleInfo
        getProps = self.__arenaDP.getPlayerGuiProps
        for vehicleID in self.__visible:
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is None:
                continue
            info = getInfo(vehicleID)
            props = getProps(vehicleID, info.team)
            try:
                if not vehicle.isPlayerVehicle:
                    yield (vehicle.proxy, info, props)
            except AttributeError:
                LOG_CURRENT_EXCEPTION()

        return

    def handleBattleEventsSummary(self, summary):
        """
        RPC call from the server when user goes to Arena (including case with relogin). Summary
        data represented by dictionary with various 'summary ' parameters. Currently it is
        information about damage log total values (damage, blocked and assist damage) and
        an additional killer info for postmortem window.
        
        :param summary: dict
        """
        event = feedback_events.BattleSummaryFeedbackEvent.fromDict(summary)
        self.onPlayerSummaryFeedbackReceived(event)
        self.__eventsCache[event.getType()] = event
        event = feedback_events.PostmortemSummaryEvent.fromDict(summary)
        self.onPostmortemSummaryReceived(event)
        self.__eventsCache[event.getType()] = event

    def handleBattleEvents(self, events):
        """
        Handle on player action. Pushes feedback events based on battle event type.
        
        :param events: list of event data dicts.
        """
        if not self.__isPEEnabled:
            return
        feedbackEvents = []
        for data in events:
            feedbackEvent = feedback_events.PlayerFeedbackEvent.fromDict(data)
            if feedbackEvent.getType() == _FET.PLAYER_KILLED_ENEMY:
                vo = self.__arenaDP.getVehicleInfo(feedbackEvent.getTargetID())
                if self.__arenaDP.isEnemyTeam(vo.team):
                    feedbackEvents.append(feedbackEvent)
            feedbackEvents.append(feedbackEvent)

        if feedbackEvents:
            self.onPlayerFeedbackReceived(feedbackEvents)

    def startVehicleVisual(self, vProxy, isImmediate=False):
        vehicleID = vProxy.id
        vInfo = self.__arenaDP.getVehicleInfo(vehicleID)
        if vInfo.isObserver():
            return
        guiProps = self.__arenaDP.getPlayerGuiProps(vehicleID, vInfo.team)
        self.__visible.add(vehicleID)
        if not vProxy.isPlayerVehicle:

            def __addVehicleToUI():
                self.__pending[vehicleID] = None
                self.onVehicleMarkerAdded(vProxy, vInfo, guiProps)
                self.onMinimapVehicleAdded(vProxy, vInfo, guiProps)
                if not isImmediate and not vProxy.isAlive():
                    self.setVehicleState(vProxy.id, _FET.VEHICLE_DEAD, True)
                return

            if isImmediate:
                __addVehicleToUI()
            else:
                self.__pending[vehicleID] = BigWorld.callback(0.0, __addVehicleToUI)

    def stopVehicleVisual(self, vehicleID, isPlayerVehicle):
        callbackID = self.__pending.pop(vehicleID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        self.__visible.discard(vehicleID)
        if not isPlayerVehicle:
            self.onVehicleMarkerRemoved(vehicleID)
        self.onMinimapVehicleRemoved(vehicleID)
        return

    def setVehicleState(self, vehicleID, eventID, isImmediate=False):
        if vehicleID != avatar_getter.getPlayerVehicleID():
            self.onVehicleFeedbackReceived(eventID, vehicleID, isImmediate)

    def showActionMarker(self, vehicleID, vMarker='', mMarker=''):
        if vMarker and vehicleID != avatar_getter.getPlayerVehicleID():
            self.onVehicleFeedbackReceived(_FET.VEHICLE_SHOW_MARKER, vehicleID, vMarker)
        if mMarker:
            self.onMinimapFeedbackReceived(_FET.MINIMAP_SHOW_MARKER, vehicleID, mMarker)

    def setVehicleNewHealth(self, vehicleID, newHealth, attackerID=0, attackReasonID=0):
        self._setVehicleHealthChanged(vehicleID, newHealth, attackerID, attackReasonID)

    def markCellOnMinimap(self, cell):
        self.onMinimapFeedbackReceived(_FET.MINIMAP_MARK_CELL, 0, (cell, _CELL_BLINKING_DURATION))

    def showVehicleDamagedDevices(self, vehicleID, criticalExtras, destroyedExtras):
        totalExtras = self.__arenaVisitor.vehicles.getVehicleExtras(vehicleID)
        if totalExtras is not None:
            fetcher = _DamagedDevicesExtraFetcher(totalExtras, criticalExtras, destroyedExtras)
            self.onVehicleFeedbackReceived(_FET.SHOW_VEHICLE_DAMAGES_DEVICES, vehicleID, fetcher)
        return

    def hideVehicleDamagedDevices(self, vehicleID=0):
        self.onVehicleFeedbackReceived(_FET.HIDE_VEHICLE_DAMAGES_DEVICES, vehicleID, None)
        return

    def setVehicleAttrs(self, vehicleID, attrs):
        self.__attrs = attrs
        self.onVehicleFeedbackReceived(_FET.VEHICLE_ATTRS_CHANGED, vehicleID, dict(self.__attrs))

    def getVehicleAttrs(self):
        return dict(self.__attrs)

    def setTargetInFocus(self, vehicleID, isInFocus):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_IN_FOCUS, vehicleID, isInFocus)

    def setVehicleHasAmmo(self, vehicleID, hasAmmo):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_HAS_AMMO, vehicleID, hasAmmo)

    def setDevelopmentInfo(self, code, info):
        """ Sets some development information that are received from server.
        Adaptor stores last received information for one code (DEVELOPMENT_INFO).
        :param code: DEVELOPMENT_INFO.*.
        :param info: received information.
        """
        self.__devInfo[code] = info
        self.onDevelopmentInfoSet(code, info)

    def getDevelopmentInfo(self, code):
        """ Gets desired development information by code.
        :param code: DEVELOPMENT_INFO.*.
        :return: last received information or None.
        """
        if code in self.__devInfo:
            return self.__devInfo[code]
        else:
            return None
            return None

    def _setVehicleHealthChanged(self, vehicleID, newHealth, attackerID, attackReasonID):
        if attackerID:
            aInfo = self.__arenaDP.getVehicleInfo(attackerID)
        else:
            aInfo = None
        self.onVehicleFeedbackReceived(_FET.VEHICLE_HEALTH, vehicleID, (newHealth, aInfo, attackReasonID))
        return


def createFeedbackAdaptor(setup):
    return BattleFeedbackAdaptor(setup)
