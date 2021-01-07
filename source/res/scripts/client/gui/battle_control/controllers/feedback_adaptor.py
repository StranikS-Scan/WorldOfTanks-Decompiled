# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/feedback_adaptor.py
import weakref
from collections import namedtuple
import BigWorld
import Event
import TriggersManager
import feedback_events
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET, BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
FEEDBACK_TO_TRIGGER_ID = {_FET.VEHICLE_VISIBILITY_CHANGED: TriggersManager.TRIGGER_TYPE.PLAYER_DETECT_ENEMY}
EntityInFocusData = namedtuple('EntityInFocusData', ['isInFocus', 'entityTypeInFocus'])
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
    __slots__ = ('onPlayerFeedbackReceived', 'onPlayerSummaryFeedbackReceived', 'onPostmortemSummaryReceived', 'onVehicleMarkerAdded', 'onVehicleMarkerRemoved', 'onVehicleFeedbackReceived', 'onMinimapVehicleAdded', 'onMinimapVehicleRemoved', 'onRoundFinished', 'onDevelopmentInfoSet', 'onStaticMarkerAdded', 'onStaticMarkerRemoved', 'onReplyFeedbackReceived', 'onRemoveCommandReceived', 'setInFocusForPlayer', 'onMinimapFeedbackReceived', 'onVehicleDetected', 'onActionAddedToMarkerReceived', 'onShotDone', 'onAddCommandReceived', '__arenaDP', '__visible', '__pending', '__attrs', '__weakref__', '__arenaVisitor', '__devInfo', '__eventsCache', '__eManager')

    def __init__(self, setup):
        super(BattleFeedbackAdaptor, self).__init__()
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__arenaVisitor = weakref.proxy(setup.arenaVisitor)
        self.__visible = set()
        self.__pending = {}
        self.__attrs = {}
        self.__devInfo = {}
        self.__eventsCache = {}
        self.__eManager = Event.EventManager()
        self.onPlayerFeedbackReceived = Event.Event(self.__eManager)
        self.onPlayerSummaryFeedbackReceived = Event.Event(self.__eManager)
        self.onPostmortemSummaryReceived = Event.Event(self.__eManager)
        self.onVehicleMarkerAdded = Event.Event(self.__eManager)
        self.onVehicleMarkerRemoved = Event.Event(self.__eManager)
        self.onVehicleFeedbackReceived = Event.Event(self.__eManager)
        self.onMinimapVehicleAdded = Event.Event(self.__eManager)
        self.onMinimapVehicleRemoved = Event.Event(self.__eManager)
        self.onMinimapFeedbackReceived = Event.Event(self.__eManager)
        self.onVehicleDetected = Event.Event(self.__eManager)
        self.onDevelopmentInfoSet = Event.Event(self.__eManager)
        self.onStaticMarkerAdded = Event.Event(self.__eManager)
        self.onStaticMarkerRemoved = Event.Event(self.__eManager)
        self.onRoundFinished = Event.Event(self.__eManager)
        self.onShotDone = Event.Event(self.__eManager)
        self.onReplyFeedbackReceived = Event.Event(self.__eManager)
        self.onRemoveCommandReceived = Event.Event(self.__eManager)
        self.onAddCommandReceived = Event.Event(self.__eManager)
        self.setInFocusForPlayer = Event.Event(self.__eManager)
        self.onActionAddedToMarkerReceived = Event.Event(self.__eManager)

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

        self.__arenaDP = None
        self.__arenaVisitor = None
        self.__attrs = {}
        self.__devInfo.clear()
        self.__eventsCache.clear()
        self.__eManager.clear()
        return

    def getCachedEvent(self, eventID):
        return self.__eventsCache.get(eventID, None)

    def getVehicleProxy(self, vehicleID):
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
        event = feedback_events.BattleSummaryFeedbackEvent.fromDict(summary)
        self.onPlayerSummaryFeedbackReceived(event)
        self.__eventsCache[event.getType()] = event
        event = feedback_events.PostmortemSummaryEvent.fromDict(summary)
        self.onPostmortemSummaryReceived(event)
        self.__eventsCache[event.getType()] = event

    def handleBattleEvents(self, events):
        feedbackEvents = []
        for data in events:
            feedbackEvent = feedback_events.PlayerFeedbackEvent.fromDict(data)
            feedbackType = feedbackEvent.getType()
            if feedbackType == _FET.PLAYER_KILLED_ENEMY:
                vo = self.__arenaDP.getVehicleInfo(feedbackEvent.getTargetID())
                if self.__arenaDP.isEnemyTeam(vo.team):
                    feedbackEvents.append(feedbackEvent)
            if feedbackType == _FET.VEHICLE_VISIBILITY_CHANGED:
                extraVis = feedbackEvent.getExtra()
                targetId = feedbackEvent.getTargetID()
                triggerId = TriggersManager.TRIGGER_TYPE.PLAYER_DETECT_ENEMY
                TriggersManager.g_manager.activateTrigger(triggerId, targetId=targetId, isVisible=extraVis.isVisible(), isDirect=extraVis.isDirect)
            if feedbackType == _FET.VEHICLE_DETECTED:
                self.onVehicleDetected(feedbackEvent)
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

    def setRoundFinished(self, winningTeam, reason):
        self.onRoundFinished(winningTeam, reason)

    def setVehicleState(self, vehicleID, eventID, isImmediate=False):
        if vehicleID != avatar_getter.getPlayerVehicleID():
            self.onVehicleFeedbackReceived(eventID, vehicleID, isImmediate)

    def showActionMarker(self, vehicleID, vMarker='', mMarker='', numberOfReplies=0, isTargetForPlayer=False, isPermanent=True):
        if vMarker and vehicleID != avatar_getter.getPlayerVehicleID():
            self.onVehicleFeedbackReceived(_FET.VEHICLE_SHOW_MARKER, vehicleID, (vMarker,
             numberOfReplies,
             isTargetForPlayer,
             isPermanent))
        if mMarker:
            self.onMinimapFeedbackReceived(_FET.MINIMAP_SHOW_MARKER, vehicleID, (mMarker, numberOfReplies))

    def setVehicleNewHealth(self, vehicleID, newHealth, attackerID=0, attackReasonID=0):
        self._setVehicleHealthChanged(vehicleID, newHealth, attackerID, attackReasonID)

    def invalidateStun(self, vehicleID, stunDuration):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_STUN, vehicleID, stunDuration)

    def invalidateDebuff(self, vehicleID, debuffInfo):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_DEBUFF, vehicleID, debuffInfo)

    def invalidateBuffEffect(self, feedbackEventID, vehicleID, data):
        self.onVehicleFeedbackReceived(feedbackEventID, vehicleID, data)

    def invalidatePassiveEngineering(self, vehicleID, data):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_PASSIVE_ENGINEERING, vehicleID, data)

    def invalidateActiveGunChanges(self, vehicleID, data):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_ACTIVE_GUN_CHANGED, vehicleID, data)

    def markObjectiveOnMinimap(self, senderID, hqIdx, cmdName):
        self.onMinimapFeedbackReceived(_FET.MINIMAP_MARK_OBJECTIVE, senderID, (hqIdx, _CELL_BLINKING_DURATION, cmdName))

    def onActionAddedToMarker(self, senderID, commandID, markerType, markerID):
        self.onActionAddedToMarkerReceived(senderID, commandID, markerType, markerID)

    def onReplyToCommand(self, uniqueCommandID, replierID, markerType, oldReplyCount, newReplyCount):
        self.onReplyFeedbackReceived(uniqueCommandID, replierID, markerType, oldReplyCount, newReplyCount)

    def onCommandAdded(self, addedID, markerType):
        self.onAddCommandReceived(addedID, markerType)

    def onCommandRemoved(self, removedID, markerType):
        self.onRemoveCommandReceived(removedID, markerType)

    def showVehicleDamagedDevices(self, vehicleID, criticalExtras, destroyedExtras):
        totalExtras = self.__arenaVisitor.vehicles.getVehicleExtras(vehicleID)
        if totalExtras is not None:
            fetcher = _DamagedDevicesExtraFetcher(totalExtras, criticalExtras, destroyedExtras)
            self.onVehicleFeedbackReceived(_FET.SHOW_VEHICLE_DAMAGES_DEVICES, vehicleID, fetcher)
        return

    def hideVehicleDamagedDevices(self, vehicleID=0):
        self.onVehicleFeedbackReceived(_FET.HIDE_VEHICLE_DAMAGES_DEVICES, vehicleID, None)
        return

    def showActionMessage(self, vehicleID, message, isAlly):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_SHOW_MESSAGE, vehicleID, (message, isAlly))

    def setVehicleAttrs(self, vehicleID, attrs):
        self.__attrs = attrs
        self.onVehicleFeedbackReceived(_FET.VEHICLE_ATTRS_CHANGED, vehicleID, dict(self.__attrs))

    def getVehicleAttrs(self):
        return dict(self.__attrs)

    def setTargetInFocus(self, vehicleID, isInFocus, entityTypeInFocus):
        entityInFocusData = EntityInFocusData(isInFocus, entityTypeInFocus)
        self.onVehicleFeedbackReceived(_FET.ENTITY_IN_FOCUS, vehicleID, entityInFocusData)

    def setVehicleHasAmmo(self, vehicleID, hasAmmo):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_HAS_AMMO, vehicleID, hasAmmo)

    def setDevelopmentInfo(self, code, info):
        self.__devInfo[code] = info
        self.onDevelopmentInfoSet(code, info)

    def getDevelopmentInfo(self, code):
        return self.__devInfo[code] if code in self.__devInfo else None

    def setVehicleRecoveryState(self, vehicleID, activated, state, timerDuration, endOfTimer):
        attrs = (activated,
         state,
         timerDuration,
         endOfTimer)
        self.onVehicleFeedbackReceived(_FET.VEHICLE_RECOVERY_STATE_UPDATE, vehicleID, attrs)

    def setVehicleRecoveryCanceled(self, vehicleID):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_RECOVERY_CANCELED, vehicleID, None)
        return

    def setVehicleRecoveryKeyPressed(self, vehicleID):
        self.onVehicleFeedbackReceived(_FET.VEHICLE_RECOVERY_KEY_PRESSED, vehicleID, None)
        return

    def _setVehicleHealthChanged(self, vehicleID, newHealth, attackerID, attackReasonID):
        if attackerID:
            aInfo = self.__arenaDP.getVehicleInfo(attackerID)
        else:
            aInfo = None
        self.onVehicleFeedbackReceived(_FET.VEHICLE_HEALTH, vehicleID, (newHealth, aInfo, attackReasonID))
        return


def createFeedbackAdaptor(setup):
    return BattleFeedbackAdaptor(setup)
