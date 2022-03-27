# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/IngameSoundNotifications.py
import logging
from random import randrange
from functools import partial
import random
from collections import namedtuple
from debug_utils import LOG_WARNING
import Math
import BigWorld
import ResMgr
import BattleReplay
import Event
import SoundGroups
import VSE
from visual_script_client.contexts.sound_notifications_context import SoundNotificationsContext
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from gui.sounds.r4_sound_constants import R4_SOUND, TANK_TYPE_TO_SWITCH
from gui.battle_control import avatar_getter
from helpers import dependency
from constants import ARENA_PERIOD
from skeletons.gui.battle_session import IBattleSessionProvider
_DORMANT_EVENTS_NAMES = [R4_SOUND.R4_ALLY_DETECTED, R4_SOUND.R4_ENEMY_DETECTED]
_DORMANT_EVENTS_NAMES.extend(R4_SOUND.R4_ALLY_DAMAGE_EVENTS)
_DORMANT_EVENTS_NAMES.extend(R4_SOUND.R4_ORDER_EVENTS)
_COOLDOWN_TYPE_VEHICLE_ID = 'VehicleID'
_COOLDOWN_TYPE_VEHICLE_CLASS = 'VehicleClass'
_COOLDOWN_TYPES = {_COOLDOWN_TYPE_VEHICLE_ID, _COOLDOWN_TYPE_VEHICLE_CLASS}
_logger = logging.getLogger(__name__)

class IngameSoundNotifications(CallbackDelayer, TimeDeltaMeter):
    __EVENTS_PATH = 'gui/sound_notifications.xml'
    __CIRCUMSTANCES_PATH = 'gui/sound_circumstances.xml'
    __DEFAULT_LIFETIME = 3.0
    __TICK_DELAY = 0.5
    QueueItem = namedtuple('QueueItem', ('eventName', 'priority', 'time', 'vehicleID', 'checkFn', 'position', 'boundVehicleID', 'cooldownType'))
    PlayingEvent = namedtuple('PlayingEvent', ('eventName', 'vehicle', 'position', 'boundVehicle', 'is2D'))

    def __init__(self):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__isEnabled = False
        self.__enabledSoundCategories = set()
        self.__remappedNotifications = {}
        self._events = {}
        self.__eventsPriorities = {}
        self.__eventsCooldowns = {}
        self.__eventCooldownPerCooldownType = {}
        self.__fxCooldowns = {}
        self.__circumstances = {}
        self.__circumstancesWeights = {}
        self.__circumstancesGroupsWeights = {}
        self.__playingEvents = {}
        self.__queues = {}
        self.onPlayEvent = Event.Event()
        self.onAddEvent = Event.Event()
        self.__readConfigs()
        self._vsePlan = VSE.Plan()
        self._vsePlan.load('soundNotifications', 'CLIENT')
        self.__soundNotificationsContext = None
        return

    def start(self):
        self.__enabledSoundCategories = set(('fx', 'voice'))
        self.__isEnabled = True
        self.__soundNotificationsContext = SoundNotificationsContext()
        self._vsePlan.setContext(self.__soundNotificationsContext)
        self._vsePlan.start()
        self.measureDeltaTime()
        self.delayCallback(self.__TICK_DELAY, self.__tick)

    def destroy(self):
        CallbackDelayer.destroy(self)
        self.__isEnabled = False
        self._vsePlan.stop()
        self._vsePlan = None
        if self.__soundNotificationsContext is not None:
            self.__soundNotificationsContext.destroy()
            self.__soundNotificationsContext = None
        self.clear()
        self.__eventsPriorities = {}
        self.__eventsCooldowns = {}
        self.__fxCooldowns = {}
        self.__circumstancesWeights = {}
        self.__circumstancesGroupsWeights = {}
        return

    def isPlaying(self, eventName):
        for event in self.__playingEvents.values():
            if event and event.eventName == eventName:
                return True

        return False

    def setRemapping(self, remap):
        self.__remappedNotifications = remap

    def play(self, eventName, vehicleID=None, checkFn=None, position=None, boundVehicleID=None):
        if self.__checkPause():
            return
        else:
            eventName = self.__remappedNotifications.get(eventName, eventName)
            if eventName is None:
                return
            event = self._events.get(eventName, None)
            if event is None:
                LOG_WARNING("Couldn't find %s event" % eventName)
                return
            if 'chance' in event and randrange(1, 100) > int(event['chance']):
                return
            self.__playFX(eventName, vehicleID, position)
            if 'queue' not in event or not self.isCategoryEnabled('voice'):
                return
            predelay = float(event['predelay']) if 'predelay' in event else 0
            BigWorld.callback(predelay, partial(self.__playDelayed, eventName, vehicleID, checkFn, position, boundVehicleID))
            return

    def __playDelayed(self, eventName, vehicleID=None, checkFn=None, position=None, boundVehicleID=None):
        event = self._events.get(eventName, None)
        queueNum = int(event['queue'])
        priority = int(self.getEventInfo(eventName, 'priority'))
        cooldownType = self.getEventInfo(eventName, 'cooldownType')
        queueItem = self.QueueItem(eventName, priority, BigWorld.time(), vehicleID, checkFn, position, boundVehicleID, cooldownType)
        index = 0
        for item in self.__queues[queueNum]:
            if item.priority < queueItem.priority:
                break
            index += 1

        self.__queues[queueNum].insert(index, queueItem)
        if not self.__playingEvents[queueNum]:
            self.__playFirstFromQueue(queueNum)
        else:
            self.onAddEvent(eventName)
        return

    def __playFX(self, eventName, vehicleID, position):
        if eventName in self.__fxCooldowns and self.__fxCooldowns[eventName]:
            return
        else:
            event = self._events.get(eventName, None)
            if 'fxEvent' not in event or not self.isCategoryEnabled('fx'):
                return
            if 'cooldownFx' in event and float(event['cooldownFx']) > 0:
                self.__fxCooldowns[eventName] = {'time': float(event['cooldownFx'])}
            if vehicleID is not None:
                vehicle = BigWorld.entity(vehicleID)
                if vehicle:
                    SoundGroups.g_instance.playSoundPos(event['fxEvent'], vehicle.position)
            elif position is not None:
                SoundGroups.g_instance.playSoundPos(event['fxEvent'], position)
            else:
                SoundGroups.g_instance.playSound2D(event['fxEvent'])
            return

    def playNextQueueEvent(self, queueNum):
        if self.__checkPause():
            return
        else:
            self.__playingEvents[queueNum] = None
            self.__playFirstFromQueue(queueNum)
            return

    def replayLastQueueEvent(self, queueNum):
        if self.__checkPause():
            return
        if self.__playingEvents[queueNum]:
            self.onPlayEvent(self.__playingEvents[queueNum].eventName)

    def getFirstQueueEvent(self, queueNum):
        return self.__queues[queueNum][0].eventName if self.__queues[queueNum] else ''

    def clear(self):
        for queueNum in self.__queues:
            self.__queues[queueNum] = []

        for queueNum in self.__playingEvents:
            self.__playingEvents[queueNum] = None

        return

    def clearQueue(self, queueNum):
        self.__queues[queueNum] = []

    def enableFX(self, isEnabled):
        if isEnabled:
            self.__enabledSoundCategories.add('fx')
        else:
            self.__enabledSoundCategories.remove('fx')

    def enableVoices(self, isEnabled, clearQueues=True):
        if isEnabled:
            self.__enabledSoundCategories.add('voice')
        else:
            self.__enabledSoundCategories.remove('voice')
            if clearQueues:
                self.clear()

    def isCategoryEnabled(self, category):
        return True if category in self.__enabledSoundCategories else False

    def getEventInfo(self, eventName, parameter):
        if parameter == 'priority' and eventName in self.__eventsPriorities and self.__eventsPriorities[eventName]:
            return self.__eventsPriorities[eventName]['priority']
        return self._events[eventName][parameter] if eventName in self._events and parameter in self._events[eventName] else ''

    def getPlayingEventData(self, queueNum, parameter):
        playingEvent = self.__playingEvents[queueNum]
        return getattr(playingEvent, parameter) if playingEvent and hasattr(playingEvent, parameter) else None

    def getCircumstanceInfo(self, circIndex, parameter):
        if parameter == 'weight':
            if circIndex in self.__circumstancesWeights and self.__circumstancesWeights[circIndex]:
                return self.__circumstancesWeights[circIndex]['weight']
            if circIndex in self.__circumstances and 'group' in self.__circumstances[circIndex]:
                groupName = self.__circumstances[circIndex]['group']
                if groupName in self.__circumstancesGroupsWeights and self.__circumstancesGroupsWeights[groupName]:
                    return self.__circumstancesGroupsWeights[groupName]['weight']
        return self.__circumstances[circIndex][parameter] if circIndex in self.__circumstances and parameter in self.__circumstances[circIndex] else ''

    def getCircumstanceIndex(self, circGroup, circName):
        for circ in self.__circumstances.values():
            if 'group' and 'name' and 'index' in circ and circ['group'] == circGroup and circ['name'] == circName:
                return circ['index']

    def setEventCooldown(self, eventName, cooldown):
        if eventName in self._events:
            cooldownType = self.getEventInfo(eventName, 'cooldownType')
            if cooldownType not in _COOLDOWN_TYPES:
                self.__eventsCooldowns[eventName] = {'time': cooldown}

    def setEventPriority(self, eventName, priority, hold):
        if eventName in self._events:
            self.__eventsPriorities[eventName] = {'priority': priority,
             'time': hold}

    def setCircumstanceWeight(self, circIndex, weight, hold):
        if circIndex in self.__circumstances:
            self.__circumstancesWeights[circIndex] = {'weight': weight,
             'time': hold}

    def setCircumstanceGroupWeight(self, groupName, weight, hold):
        self.__circumstancesGroupsWeights[groupName] = {'weight': weight,
         'time': hold}

    def __checkPause(self):
        shouldPause = False
        if not self.__isEnabled or BigWorld.isWindowVisible() is False:
            shouldPause = True
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            if replayCtrl.isTimeWarpInProgress or replayCtrl.isPaused:
                shouldPause = True
        if shouldPause:
            self.clear()
        return shouldPause

    def __getVehicleClassByVehicleID(self, vID):
        vehicle = BigWorld.entity(vID)
        if vehicle is None:
            return
        else:
            vehicleClass = vehicle.typeDescriptor.type.getVehicleClass()
            return None if vehicleClass is None else vehicleClass

    def __getCooldownTypeKey(self, vID, cooldownType):
        cooldownTypeKey = None
        if cooldownType == _COOLDOWN_TYPE_VEHICLE_CLASS:
            if vID is not None:
                cooldownTypeKey = self.__getVehicleClassByVehicleID(vID)
            else:
                LOG_WARNING('_COOLDOWN_TYPE_VEHICLE_CLASS has no vehicleID: ', vID)
        elif cooldownType == _COOLDOWN_TYPE_VEHICLE_ID:
            if vID:
                cooldownTypeKey = vID
            else:
                LOG_WARNING('_COOLDOWN_TYPE_VEHICLE_ID has no vehicleID: ', vID)
        return cooldownTypeKey

    def __checkEventCooldownUsingCooldownType(self, vehicleID=None, cooldownType=None, eventName=None):
        cooldownTypeKey = self.__getCooldownTypeKey(vehicleID, cooldownType)
        if cooldownTypeKey is None:
            return False
        else:
            if eventName not in self.__eventCooldownPerCooldownType:
                self.__eventCooldownPerCooldownType[eventName] = {}
            if cooldownTypeKey not in self.__eventCooldownPerCooldownType[eventName]:
                self.__eventCooldownPerCooldownType[eventName][cooldownTypeKey] = BigWorld.time()
                return True
            lastTimeEventWasPlayed = self.__eventCooldownPerCooldownType[eventName][cooldownTypeKey]
            cooldownTime = float(self.getEventInfo(eventName, 'cooldownEvent'))
            if lastTimeEventWasPlayed + cooldownTime > BigWorld.time():
                return False
            self.__eventCooldownPerCooldownType[eventName][cooldownTypeKey] = BigWorld.time()
            return True

    def __checkCooldown(self, queueItem):
        if queueItem.cooldownType in _COOLDOWN_TYPES:
            checkCooldown = self.__checkEventCooldownUsingCooldownType(queueItem.vehicleID, queueItem.cooldownType, queueItem.eventName)
            return checkCooldown
        checkCooldown = queueItem.eventName not in self.__eventsCooldowns or not self.__eventsCooldowns[queueItem.eventName]
        return checkCooldown

    def __playFirstFromQueue(self, queueNum):
        if not self.__queues[queueNum]:
            self.__playingEvents[queueNum] = None
            return
        else:
            queueItem = self.__queues[queueNum][0]
            del self.__queues[queueNum][0]
            checkCooldown = self.__checkCooldown(queueItem)
            checkVehicle = queueItem.vehicleID is None or BigWorld.entity(queueItem.vehicleID) is not None
            checkFunction = queueItem.checkFn() if queueItem.checkFn else True
            if checkFunction and checkVehicle and checkCooldown:
                vehicle = BigWorld.entity(queueItem.vehicleID) if queueItem.vehicleID is not None else None
                boundVehicle = BigWorld.entity(queueItem.boundVehicleID) if queueItem.boundVehicleID is not None else None
                position = vehicle.position if vehicle else queueItem.position
                self.__playingEvents[queueNum] = self.PlayingEvent(queueItem.eventName, vehicle, position, boundVehicle, position is None)
                self.onPlayEvent(queueItem.eventName)
                if hasattr(self, 'setVehicleSpeaking'):
                    self.setVehicleSpeaking(queueItem.vehicleID, True)
            else:
                self.__playFirstFromQueue(queueNum)
            return

    def __readConfigs(self):
        eventsSec = ResMgr.openSection(self.__EVENTS_PATH)
        self._events = {}
        for eventSec in eventsSec.values():
            eventName = eventSec.readString('name')
            self._events[eventName] = {}
            for infoSec in eventSec.values():
                self._events[eventName][infoSec.name] = infoSec.asString
                if infoSec.name == 'queue' and infoSec.asInt not in self.__queues:
                    self.__queues[infoSec.asInt] = []
                    self.__playingEvents[infoSec.asInt] = None

        circsSec = ResMgr.openSection(self.__CIRCUMSTANCES_PATH)
        self.__circumstances = {}
        for circSec in circsSec.values():
            index = circSec.readString('index')
            self.__circumstances[index] = {}
            for infoSec in circSec.values():
                self.__circumstances[index][infoSec.name] = infoSec.asString

        return

    def __tick(self):
        delta = self.measureDeltaTime()
        self.__tickGroup(self.__eventsCooldowns, delta)
        self.__tickGroup(self.__fxCooldowns, delta)
        self.__tickGroup(self.__eventsPriorities, delta)
        self.__tickGroup(self.__circumstancesWeights, delta)
        self.__tickGroup(self.__circumstancesGroupsWeights, delta)
        for queueNum in self.__queues:
            self.__queues[queueNum] = [ item for item in self.__queues[queueNum] if self.__checkLifetime(item) ]

        return self.__TICK_DELAY

    def __checkLifetime(self, queueItem):
        event = self._events[queueItem.eventName]
        lifetime = float(event['lifetime']) if 'lifetime' in event else self.__DEFAULT_LIFETIME
        return queueItem.time + lifetime > BigWorld.time()

    @staticmethod
    def __tickGroup(group, delta):
        for name, info in group.items():
            if not info:
                continue
            info['time'] = info['time'] - delta
            if info['time'] < 0:
                group[name] = None

        return


class ComplexSoundNotifications(object):
    SPG_DISTANT_THREAT_SOUND = 'wpn_artillery_distant_threat'
    RTPC_EXT_SPG_SIGHT = 'RTPC_ext_artillery_sight'

    def __init__(self):
        self.__activeSounds = {}

    def destroy(self):
        for sound in self.__activeSounds.values():
            sound.stop()

        self.__activeSounds.clear()

    def notifyEnemySPGShotSound(self, distToTarget, shooterPosition):
        soundMatrix = Math.Matrix()
        soundMatrix.translation = shooterPosition
        sound = SoundGroups.g_instance.getSound3D(soundMatrix, ComplexSoundNotifications.SPG_DISTANT_THREAT_SOUND)
        if sound is not None:
            soundId = id(sound)
            self.__activeSounds[soundId] = sound
            sound.setRTPC(ComplexSoundNotifications.RTPC_EXT_SPG_SIGHT, distToTarget)
            sound.setCallback(lambda s: self.__endSoundCallback(soundId))
            sound.play()
        return

    def __endSoundCallback(self, soundID):
        del self.__activeSounds[soundID]


class R4SoundNotifications(IngameSoundNotifications, CallbackDelayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _VEHICLE_SPEAKING_TIME = 3.0

    def __init__(self):
        IngameSoundNotifications.__init__(self)
        CallbackDelayer.__init__(self)
        self.__vehicleLastActivityTime = {}
        self.__vehicleStartedSpeaking = {}
        self.__dormantCooldown = 0
        dormantEvent = self._events.get(R4_SOUND.R4_DORMANT, None)
        if dormantEvent is not None:
            self.__dormantCooldown = float(dormantEvent['cooldownEvent'])
        mannerUIEvent = self._events.get(R4_SOUND.R4_MANNER_UI)
        if mannerUIEvent is not None:
            R4_SOUND.R4_MANNER_UI_EVENT_NAME = mannerUIEvent['fxEvent']
        return

    def start(self):
        IngameSoundNotifications.start(self)
        self.delayCallback(0.0, self.__tick)
        arena = avatar_getter.getArena()
        if arena and arena.period == ARENA_PERIOD.BATTLE:
            vehicleIDs = self.__getVehicleIDs()
            for vID in vehicleIDs:
                self.setVehicleLastActivityTime(vID)

    def destroy(self):
        IngameSoundNotifications.destroy(self)
        CallbackDelayer.destroy(self)
        self.stopCallback(self.__tick)

    def startBattle(self):
        self.playOnRandomVehicle(R4_SOUND.R4_START_BATTLE)
        vehicles = [ v for v in BigWorld.player().vehicles if self.__isAliveControlledAlly(v.id) and not self.__isPlayerArcadeVehicle(v.id) ]
        for vehicle in vehicles:
            self.setVehicleLastActivityTime(vehicle.id)

    def play(self, eventName, vehicleID=None, checkFn=None, position=None, boundVehicleID=None):
        if eventName in R4_SOUND.R4_MUTED_SOUNDS and eventName:
            return
        else:
            if vehicleID is not None and eventName in _DORMANT_EVENTS_NAMES:
                self.setVehicleLastActivityTime(vehicleID)
            if eventName not in R4_SOUND.R4_EVENTS_FORCED_TO_PLAY_IN_ARCADE_MODE:
                if vehicleID is not None and self.__isPlayerArcadeVehicle(vehicleID):
                    return
            if eventName:
                IngameSoundNotifications.play(self, eventName, vehicleID, checkFn, position, boundVehicleID)
            return

    def setVehicleLastActivityTime(self, vehicleID):
        self.__vehicleLastActivityTime[vehicleID] = BigWorld.time()

    def cancel(self, event, category=None):
        pass

    def playOnRandomVehicle(self, eventName):
        vehicleIDs = self.__getVehicleIDs()
        if vehicleIDs:
            vID = random.choice(vehicleIDs)
            self.play(eventName, vID)

    def playOnHeadVehicle(self, eventName, vIDs=None):
        if not vIDs:
            vIDs = self.__getVehicleIDs()
        headVehicleIDFound = False
        for key in TANK_TYPE_TO_SWITCH.keys():
            if headVehicleIDFound:
                break
            for vID in vIDs:
                if self.__isPlayerArcadeVehicle(vID):
                    continue
                vehicle = BigWorld.entity(vID)
                if vehicle is None:
                    continue
                vehicleType = vehicle.typeDescriptor.type.getVehicleClass()
                if vehicleType is None:
                    continue
                if vehicleType == key:
                    self.play(eventName, vID)
                    headVehicleIDFound = True
                    break

        return

    def setVehicleSpeaking(self, vehicleID, value):
        if vehicleID is None:
            return
        else:
            if value:
                self.__vehicleStartedSpeaking[vehicleID] = BigWorld.time()
            elif vehicleID in self.__vehicleStartedSpeaking:
                self.__vehicleStartedSpeaking.pop(vehicleID)
            rtsCommander = self.__sessionProvider.dynamic.rtsCommander
            if rtsCommander:
                vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
                if not vehicle:
                    _logger.warning('The requested vehicle is not available as commander vehicle')
                    return
                if vehicle.isAlly:
                    self.__sessionProvider.dynamic.rtsCommander.vehicles.onVehicleSpeaking(vehicleID, value)
            return

    def __isSupply(self, vID):
        arenaDP = self.__sessionProvider.getArenaDP()
        return arenaDP.isSupply(vID) if arenaDP and vID else False

    def __getVehicleIDs(self):
        vehicleIDs = [ v.id for v in BigWorld.player().vehicles if self.__isAliveControlledAlly(v.id) and not self.__isPlayerArcadeVehicle(v.id) and not self.__isSupply(v.id) ]
        return vehicleIDs

    def __tick(self):
        currentTime = BigWorld.time()
        for vID, spokenTime in self.__vehicleStartedSpeaking.items():
            if currentTime - spokenTime > self._VEHICLE_SPEAKING_TIME:
                self.setVehicleSpeaking(vID, False)

        arena = avatar_getter.getArena()
        if not arena or arena.period != ARENA_PERIOD.BATTLE:
            return 1.0
        vehicles = [ v for v in BigWorld.player().vehicles if self.__isAliveControlledAlly(v.id) and not self.__isPlayerArcadeVehicle(v.id) and not self.__isSupply(v.id) ]
        enemies = self.__sessionProvider.dynamic.rtsCommander.vehicles.itervalues(lambda e: e.isAlive and e.isEnemy)
        for vehicle in vehicles:
            vehicleType = vehicle.typeDescriptor.type.getVehicleClass()
            if vehicleType == 'SPG':
                continue
            anyLessThanSightRadius = any((vehicle.position.distTo(enemy.position) < R4_SOUND.R4_DORMANT_ENEMY_SIGHT_RADIUS for enemy in enemies if enemy.initialized))
            if vehicle.hasMovingFlags or anyLessThanSightRadius:
                self.setVehicleLastActivityTime(vehicle.id)
                continue
            if vehicle.id in self.__vehicleLastActivityTime and self.__vehicleLastActivityTime[vehicle.id] + self.__dormantCooldown < currentTime:
                self.play(R4_SOUND.R4_DORMANT, vehicle.id)
                self.setVehicleLastActivityTime(vehicle.id)
                return 1.0
            if vehicle.id not in self.__vehicleLastActivityTime:
                self.setVehicleLastActivityTime(vehicle.id)

    def __isPlayerArcadeVehicle(self, vehicleId):
        return not avatar_getter.isCommanderCtrlMode() and BigWorld.player().vehicle and BigWorld.player().vehicle.id == vehicleId

    def __isAliveControlledAlly(self, vehicleID):
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if not rtsCommander:
            return None
        else:
            vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
            return vehicle is not None and vehicle.isAlive and vehicle.isAllyBot and not vehicle.isObserver
