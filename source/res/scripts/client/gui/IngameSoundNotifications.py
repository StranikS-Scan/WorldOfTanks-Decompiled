# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/IngameSoundNotifications.py
# Compiled at: 2011-09-15 19:06:37
import BigWorld
import ResMgr
from functools import partial
from debug_utils import *
from Vehicle import Vehicle

class IngameSoundNotifications(object):
    __CFG_SECTION_PATH = 'gui/sound_notifications.xml'

    def __init__(self):
        self.__readConfig()
        self.__isEnabled = False

    def start(self):
        self.__soundQueues = {'fx': [],
         'voice': []}
        self.__enabledSoundCategories = set(('fx', 'voice'))
        self.__isEnabled = True
        self.__activeEvents = {'fx': None,
         'voice': None}
        self.__lastTimePlayed = {}
        return

    def destroy(self):
        for event in self.__activeEvents.itervalues():
            if event is not None:
                event['sound'].stop()

        self.__activeEvents = None
        self.__soundQueues = None
        self.__isEnabled = False
        return

    def cancel(self, eventName, continuePlaying=True):
        for category in ('fx', 'voice'):
            eventDesc = self.__events[eventName].get(category, None)
            if eventDesc is not None:
                activeEvent = self.__activeEvents[category]
                soundPath = eventDesc['sound']
                if activeEvent is not None and activeEvent['soundPath'] == soundPath:
                    activeEvent['sound'].stop()
                    self.__activeEvents[category] = None
                    if continuePlaying:
                        self.__playFirstFromQueue(category)
                if soundPath in self.__soundQueues[category]:
                    self.__soundQueues[category].remove(soundPath)

        return

    def play(self, eventName, vehicleIdToBind=None):
        if not self.__isEnabled or BigWorld.isWindowVisible() == False:
            return
        else:
            event = self.__events.get(eventName, None)
            if event is None:
                LOG_WARNING("Couldn't find %s event" % eventName)
                return
            queues = self.__soundQueues
            enabledCategories = self.__enabledSoundCategories
            time = BigWorld.time()
            for category, soundDesc in event.iteritems():
                if category in enabledCategories and soundDesc['sound'] != '':
                    rules = soundDesc['playRules']
                    idToBind = vehicleIdToBind
                    if idToBind is None and soundDesc['shouldBindToPlayer']:
                        if BigWorld.player().vehicle is not None:
                            idToBind = BigWorld.player().vehicle.id
                    queueItem = (soundDesc['sound'],
                     time + soundDesc['timeout'],
                     soundDesc['minTimeBetweenEvents'],
                     idToBind)
                    if rules == 0:
                        try:
                            BigWorld.playSound(soundDesc['sound'])
                        except:
                            pass

                        continue
                    elif rules == 1:
                        self.__clearQueue(category)
                        queues[category].append(queueItem)
                    elif rules == 2:
                        queues[category].insert(0, queueItem)
                    elif rules == 3:
                        queues[category].append(queueItem)
                    if self.__activeEvents[category] is None:
                        self.__playFirstFromQueue(category)

            return

    def enable(self, isEnabled):
        self.__isEnabled = isEnabled
        if not isEnabled:
            for category in ('fx', 'voice'):
                self.__clearQueue(category)

    def enableFX(self, isEnabled):
        self.enableCategory('fx', isEnabled)

    def enableVoices(self, isEnabled):
        self.enableCategory('voice', isEnabled)

    def enableCategory(self, category, isEnabled):
        if isEnabled:
            self.__enabledSoundCategories.add(category)
        else:
            self.__enabledSoundCategories.remove(category)
            self.__clearQueue(category)

    def __clearQueue(self, category):
        if self.__activeEvents[category] is not None:
            self.__activeEvents[category]['sound'].stop()
            self.__activeEvents[category] = None
        self.__soundQueues[category] = []
        return

    def __onSoundEnd(self, category, sound):
        self.__activeEvents[category] = None
        if sound.state == 'playing':
            sound.stop()
        BigWorld.callback(0.01, partial(self.__playFirstFromQueue, category))
        return

    def __playFirstFromQueue(self, category):
        if not self.__isEnabled:
            return
        else:
            queue = self.__soundQueues[category]
            succes = False
            time = BigWorld.time()
            while 1:
                if not succes and len(queue) > 0:
                    soundPath, timeout, minTimeBetweenEvents, vehicleIdToBind = queue[0]
                    del queue[0]
                    if vehicleIdToBind is not None:
                        if not BigWorld.entities.has_key(vehicleIdToBind):
                            continue
                        vehicle = BigWorld.entities.get(vehicleIdToBind)
                        if not isinstance(vehicle, Vehicle) or not vehicle.isAlive():
                            continue
                    if time > timeout:
                        continue
                    lastPlayed = self.__lastTimePlayed.get(soundPath)
                    if lastPlayed is not None and time - lastPlayed < minTimeBetweenEvents:
                        continue
                    succes = True
                    try:
                        sound = BigWorld.playSound(soundPath)
                        if sound is None:
                            succes = False
                        else:
                            self.__lastTimePlayed[soundPath] = time
                    except:
                        succes = False

                    succes or LOG_ERROR('Failed to load sound %s' % soundPath)

            if succes:
                if sound.duration == 0:
                    LOG_WARNING('Sound notification %s has zero duration and was skipped' % soundPath)
                    BigWorld.callback(0.01, partial(self.__playFirstFromQueue, category))
                else:
                    sound.setCallback('SOUNDDEF_END', partial(self.__onSoundEnd, category))
                    self.__activeEvents[category] = {'sound': sound,
                     'soundPath': soundPath}
            return

    def __readConfig(self):
        sec = ResMgr.openSection(self.__CFG_SECTION_PATH)
        events = {}
        for eventSec in sec.values():
            event = events[eventSec.name] = {}
            for category in ('fx', 'voice'):
                soundSec = eventSec[category]
                if soundSec is not None:
                    event[category] = {'sound': soundSec.readString('sound'),
                     'playRules': soundSec.readInt('playRules'),
                     'timeout': soundSec.readFloat('timeout', 3.0),
                     'minTimeBetweenEvents': soundSec.readFloat('minTimeBetweenEvents', 0),
                     'shouldBindToPlayer': soundSec.readBool('shouldBindToPlayer', False)}

        self.__events = events
        return


class ComplexSoundNotifications(object):

    def __init__(self, ingameSoundNotifications):
        self.__isAimingEnded = False
        self.__ingameSoundNotifications = ingameSoundNotifications

    def destroy(self):
        pass

    def setAimingEnded(self, isEnded):
        if not self.__isAimingEnded and isEnded:
            self.__ingameSoundNotifications.play('sight_convergence')
        self.__isAimingEnded = isEnded


class __SightNotifications(object):
    NOTIFICATION_DELAY = 2.0
    ENEMY_SIGHTED_SOUND = ''
    ENEMIES_SIGHTED_SOUND = ''
    SIGHTED_ENEMY_KILLED_SOUND = ''
    SIGHTED_ENEMIES_KILLED_SOUND = ''

    def __init__(self, ingameSoundNotifications):
        self.__ingameSoundNotifications = ingameSoundNotifications
        self.__enemySightedCallbackId = None
        self.__isOneSighted = True
        self.__sightedEnemyKilledCallbackId = None
        self.__isOneKilled = True
        return

    def destroy(self):
        if self.__enemySightedCallbackId is not None:
            BigWorld.cancelCallback(self.__enemySightedCallbackId)
        if self.__sightedEnemyKilledCallbackId is not None:
            BigWorld.cancelCallback(self.__sightedEnemyKilledCallbackId)
        return

    def __playEnemySighted(self):
        self.__enemySightedCallbackId = None
        if self.__isOneSighted:
            self.__ingameSoundNotifications.play(SightNotifications.ENEMY_SIGHTED_SOUND)
        else:
            self.__ingameSoundNotifications.play(SightNotifications.ENEMIES_SIGHTED_SOUND)
        return

    def notifyEnemySighted(self):
        if self.__enemySightedCallbackId is None:
            self.__enemySightedCallbackId = BigWorld.callback(SightNotifications.NOTIFICATION_DELAY, self.__playEnemySighted)
            self.__isOneSighted = True
        else:
            self.__isOneSighted = False
        return

    def __playSightedEnemyKilled(self):
        self.__sightedEnemyKilledCallbackId = None
        if self.____isOneKilled:
            self.__ingameSoundNotifications.play(SightNotifications.ENEMY_SIGHTED_SOUND)
        else:
            self.__ingameSoundNotifications.play(SightNotifications.ENEMIES_SIGHTED_SOUND)
        return

    def notifySightedEnemyKilled(self):
        if self.__sightedEnemyKilledCallbackId is None:
            self.__sightedEnemyKilledCallbackId = BigWorld.callback(SightNotifications.NOTIFICATION_DELAY, self.__playSightedEnemyKilled)
            self.____isOneKilled = True
        else:
            self.____isOneKilled = False
        return
