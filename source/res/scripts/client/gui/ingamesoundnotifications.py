# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/IngameSoundNotifications.py
from random import randrange
from functools import partial
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

class IngameSoundNotifications(CallbackDelayer, TimeDeltaMeter):
    __EVENTS_PATH = 'gui/sound_notifications.xml'
    __CIRCUMSTANCES_PATH = 'gui/sound_circumstances.xml'
    __DEFAULT_LIFETIME = 3.0
    QueueItem = namedtuple('QueueItem', ('eventName', 'priority', 'time', 'vehicleID', 'checkFn', 'position', 'boundVehicleID'))
    PlayingEvent = namedtuple('PlayingEvent', ('eventName', 'vehicle', 'position', 'boundVehicle', 'is2D'))

    def __init__(self):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__isEnabled = False
        self.__enabledSoundCategories = set()
        self.__remappedNotifications = {}
        self.__events = {}
        self.__eventsPriorities = {}
        self.__eventsCooldowns = {}
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
        self.delayCallback(0.0, self.__tick)

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
            event = self.__events.get(eventName, None)
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
        event = self.__events.get(eventName, None)
        queueNum = int(event['queue'])
        priority = int(self.getEventInfo(eventName, 'priority'))
        queueItem = self.QueueItem(eventName, priority, BigWorld.time(), vehicleID, checkFn, position, boundVehicleID)
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
            event = self.__events.get(eventName, None)
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
        return self.__events[eventName][parameter] if eventName in self.__events and parameter in self.__events[eventName] else ''

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
        if eventName in self.__events:
            self.__eventsCooldowns[eventName] = {'time': cooldown}

    def setEventPriority(self, eventName, priority, hold):
        if eventName in self.__events:
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

    def __playFirstFromQueue(self, queueNum):
        if not self.__queues[queueNum]:
            self.__playingEvents[queueNum] = None
            return
        else:
            queueItem = self.__queues[queueNum][0]
            del self.__queues[queueNum][0]
            checkCooldown = queueItem.eventName not in self.__eventsCooldowns or not self.__eventsCooldowns[queueItem.eventName]
            checkVehicle = queueItem.vehicleID is None or BigWorld.entity(queueItem.vehicleID) is not None
            checkFunction = queueItem.checkFn() if queueItem.checkFn else True
            if checkFunction and checkVehicle and checkCooldown:
                vehicle = BigWorld.entity(queueItem.vehicleID) if queueItem.vehicleID is not None else None
                boundVehicle = BigWorld.entity(queueItem.boundVehicleID) if queueItem.boundVehicleID is not None else None
                position = vehicle.position if vehicle else queueItem.position
                self.__playingEvents[queueNum] = self.PlayingEvent(queueItem.eventName, vehicle, position, boundVehicle, position is None)
                self.onPlayEvent(queueItem.eventName)
            else:
                self.__playFirstFromQueue(queueNum)
            return

    def __readConfigs(self):
        eventsSec = ResMgr.openSection(self.__EVENTS_PATH)
        self.__events = {}
        for eventSec in eventsSec.values():
            eventName = eventSec.readString('name')
            self.__events[eventName] = {}
            for infoSec in eventSec.values():
                self.__events[eventName][infoSec.name] = infoSec.asString
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
        self.__tickGroup(self.__eventsCooldowns)
        self.__tickGroup(self.__fxCooldowns)
        self.__tickGroup(self.__eventsPriorities)
        self.__tickGroup(self.__circumstancesWeights)
        self.__tickGroup(self.__circumstancesGroupsWeights)
        for queueNum in self.__queues:
            self.__queues[queueNum] = [ item for item in self.__queues[queueNum] if self.__checkLifetime(item) ]

    def __checkLifetime(self, queueItem):
        event = self.__events[queueItem.eventName]
        lifetime = float(event['lifetime']) if 'lifetime' in event else self.__DEFAULT_LIFETIME
        return queueItem.time + lifetime > BigWorld.time()

    def __tickGroup(self, group):
        delta = self.measureDeltaTime()
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
