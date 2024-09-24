# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/IngameSoundNotifications.py
from random import randrange
from functools import partial
from collections import namedtuple
from debug_utils import LOG_WARNING, LOG_DEBUG
import Math
import BigWorld
import ResMgr
import BattleReplay
import Event
import SoundGroups
import VSE
import WWISE
from helpers import isPlayerAvatar
from account_helpers import AccountSettings
from account_helpers.settings_core.settings_constants import SOUND
from visual_script_client.contexts.sound_notifications_context import SoundNotificationsContext
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
_ENABLE_VO_LOGS = False
_SUBTITLE_PREFIX = '#'
_SUBTITLES_END_MARKER = '#end'

def LOG_VO(msg, *kargs, **kwargs):
    if _ENABLE_VO_LOGS:
        LOG_DEBUG('[SOUND][VO] {}'.format(msg), *kargs, **kwargs)


class IngameSoundNotifications(CallbackDelayer, TimeDeltaMeter):
    __EVENTS_PATH = 'gui/sound_notifications.xml'
    __CIRCUMSTANCES_PATH = 'gui/sound_circumstances.xml'
    __DEFAULT_LIFETIME = 3.0
    __TICK_DELAY = 0.5
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
        self._currentSubtitle = ''
        self.onPlayEvent = Event.Event()
        self.onAddEvent = Event.Event()
        self.onSubtitleShow = Event.Event()
        self.onSubtitleHide = Event.Event()
        self.__readConfigs()
        self._vsePlan = VSE.Plan()
        self._vsePlan.load('soundNotifications', 'CLIENT')
        self.__soundNotificationsContext = None
        return

    def start(self):
        self.__enabledSoundCategories = set(('fx', 'voice'))
        self.__isEnabled = True
        self.__soundNotificationsContext = SoundNotificationsContext()
        WWISE.WW_addMarkerListener(self._soundMarkerHandler)
        self._vsePlan.setContext(self.__soundNotificationsContext)
        self._vsePlan.start()
        self.measureDeltaTime()
        self.delayCallback(self.__TICK_DELAY, self.__tick)

    def destroy(self):
        CallbackDelayer.destroy(self)
        self.__isEnabled = False
        self._vsePlan.stop()
        self._vsePlan = None
        WWISE.WW_removeMarkerListener(self._soundMarkerHandler)
        if self.__soundNotificationsContext is not None:
            self.__soundNotificationsContext.destroy()
            self.__soundNotificationsContext = None
        self.clear()
        self.__eventsPriorities = {}
        self.__eventsCooldowns = {}
        self.__fxCooldowns = {}
        self.__circumstancesWeights = {}
        self.__circumstancesGroupsWeights = {}
        self.__remappedNotifications = {}
        return

    def isPlaying(self, eventName):
        for event in self.__playingEvents.values():
            if event and event.eventName == eventName:
                return True

        return False

    def setRemapping(self, remap):
        self.__remappedNotifications = remap

    def play(self, vo, vehicleID=None, checkFn=None, position=None, boundVehicleID=None):
        LOG_VO('Request: "{}"'.format(vo))
        if self.__checkPause():
            LOG_VO('Request "{}" is rejected. Reason: {}'.format(vo, 'pause'))
            return
        else:
            eventName = self.__remappedNotifications.get(vo, vo)
            if eventName is None:
                LOG_VO('Request "{}" is rejected. Reason: {}'.format(vo, 'remapping with empty'))
                return
            if vo in self.__remappedNotifications:
                LOG_VO('"{}" is overrode with "{}"'.format(vo, eventName))
            event = self.__events.get(eventName, None)
            if event is None:
                LOG_WARNING("Couldn't find %s event" % eventName)
                LOG_VO('Request "{}" is rejected. Reason: {}'.format(eventName, 'missed in sound_notifications.xml'))
                return
            if 'chance' in event and randrange(1, 100) > int(event['chance']):
                LOG_VO('Request "{}" is rejected. Reason: {}'.format(eventName, 'chance'))
                return
            self.__playFX(eventName, vehicleID, position)
            isQueueSpecified = 'queue' not in event
            if isQueueSpecified or not self.isCategoryEnabled('voice'):
                if 'fxEvent' not in event:
                    LOG_VO('Request "{}" is rejected. Reason: {}'.format(vo, 'queue is not specified' if isQueueSpecified else 'voices are disabled'))
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
        LOG_VO('Event "{}" added to queue "{}". {}'.format(eventName, queueNum, [ item.eventName for item in self.__queues[queueNum] ]))
        if not self.__playingEvents[queueNum]:
            self.__playFirstFromQueue(queueNum)
        else:
            LOG_VO('"{}" is playing now'.format(self.__playingEvents[queueNum].eventName))
            self.onAddEvent(eventName)
        return

    def __playFX(self, eventName, vehicleID, position):
        event = self.__events.get(eventName, {})
        isFX = 'fxEvent' in event
        if eventName in self.__fxCooldowns and self.__fxCooldowns[eventName]:
            if isFX:
                LOG_VO('Request "{}" is rejected. Reason: {}'.format(eventName, 'FX cooldown'))
            return
        elif not isFX or not self.isCategoryEnabled('fx'):
            if isFX:
                LOG_VO('Request "{}" is rejected. Reason: {}'.format(eventName, 'FX sounds are disabled'))
            return
        else:
            if 'cooldownFx' in event and float(event['cooldownFx']) > 0:
                self.__fxCooldowns[eventName] = {'time': float(event['cooldownFx'])}
            fxEvent = event['fxEvent']
            LOG_VO('Play fx  "{}". fxEvent: "{}"'.format(eventName, fxEvent))
            if vehicleID is not None:
                vehicle = BigWorld.entity(vehicleID)
                if vehicle:
                    SoundGroups.g_instance.playSoundPos(fxEvent, vehicle.position)
            elif position is not None:
                SoundGroups.g_instance.playSoundPos(fxEvent, position)
            else:
                SoundGroups.g_instance.playSound2D(fxEvent)
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
            LOG_VO('Clear queue "{}". Removed events: {}'.format(queueNum, [ eventItem.eventName for eventItem in self.__queues[queueNum] ]))
            self.__queues[queueNum] = []

        for queueNum in self.__playingEvents:
            self.__playingEvents[queueNum] = None

        return

    def clearQueue(self, queueNum):
        LOG_VO('Clear queue "{}". Removed events: {}'.format(queueNum, [ eventItem.eventName for eventItem in self.__queues[queueNum] ]))
        self.__queues[queueNum] = []

    def enableFX(self, isEnabled):
        LOG_VO('fx sounds are {}'.format('enabled' if isEnabled else 'disabled'))
        if isEnabled:
            self.__enabledSoundCategories.add('fx')
        else:
            self.__enabledSoundCategories.remove('fx')

    def enableVoices(self, isEnabled, clearQueues=True):
        LOG_VO('voice sounds are {}'.format('enabled' if isEnabled else 'disabled'))
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

    def onNotificationBegins(self, eventName):
        LOG_VO('Play voice "{}"'.format(eventName))
        self._hideSubtitle()

    def log(self, msg):
        LOG_VO(msg)

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
            checkFunction = queueItem.checkFn() if isPlayerAvatar() and queueItem.checkFn else True
            if checkFunction and checkVehicle and checkCooldown:
                LOG_VO('Try to play voice "{}". infEvent: "{}"'.format(queueItem.eventName, self.__events[queueItem.eventName].get('infEvent')))
                vehicle = BigWorld.entity(queueItem.vehicleID) if queueItem.vehicleID is not None else None
                boundVehicle = BigWorld.entity(queueItem.boundVehicleID) if queueItem.boundVehicleID is not None else None
                position = vehicle.position if vehicle else queueItem.position
                self.__playingEvents[queueNum] = self.PlayingEvent(queueItem.eventName, vehicle, position, boundVehicle, position is None)
                self.onPlayEvent(queueItem.eventName)
            else:
                skipReason = 'cooldown' if checkCooldown else ("vehicle doesn't found" if checkVehicle else 'external')
                LOG_VO('Skip "{}". Reason: {}'.format(queueItem.eventName, skipReason))
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
                self.__circumstances[index][infoSec.name] = infoSec.asWideString

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

        if not BigWorld.isWindowVisible():
            self._hideSubtitle()
        return self.__TICK_DELAY

    def __checkLifetime(self, queueItem):
        event = self.__events[queueItem.eventName]
        lifetime = float(event['lifetime']) if 'lifetime' in event else self.__DEFAULT_LIFETIME
        result = queueItem.time + lifetime > BigWorld.time()
        if not result:
            LOG_VO('"{}" is removed from queue. Reason: lifetime'.format(queueItem.eventName))
        return result

    @staticmethod
    def __tickGroup(group, delta):
        for name, info in group.items():
            if not info:
                continue
            info['time'] = info['time'] - delta
            if info['time'] < 0:
                group[name] = None

        return

    def _showSubtitle(self, subtitle):
        self._currentSubtitle = subtitle
        LOG_VO('Request subtitle: "{}"'.format(subtitle))
        self.onSubtitleShow(subtitle)

    def _hideSubtitle(self):
        if self._currentSubtitle:
            self._currentSubtitle = ''
            LOG_VO('Hide subtitle')
            self.onSubtitleHide()

    def _soundMarkerHandler(self, marker):
        if not AccountSettings.getSettings(SOUND.SUBTITLES):
            return
        marker = marker.strip()
        if marker == _SUBTITLES_END_MARKER:
            self._hideSubtitle()
        elif marker.startswith(_SUBTITLE_PREFIX):
            self._showSubtitle(marker)


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
