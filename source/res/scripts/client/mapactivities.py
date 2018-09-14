# Embedded file name: scripts/client/MapActivities.py
import BigWorld
import Math
import ResMgr
import Pixie
import PlayerEvents
import math
import random
import copy
import SoundGroups
from constants import ARENA_PERIOD
from debug_utils import *
from functools import partial

class Timer:
    __timeMethod = None

    @staticmethod
    def init():
        if BigWorld.serverTime() < 0.0:
            Timer.__timeMethod = BigWorld.time
        else:
            Timer.__timeMethod = BigWorld.serverTime

    @staticmethod
    def getTime():
        return Timer.__timeMethod()


class IMapActivity:

    def create(self, settings, startTime):
        pass

    def destroy(self):
        self.stop()

    def start(self):
        pass

    def stop(self):
        pass

    def canStart(self):
        return False

    def isActive(self):
        return False

    def isPeriodic(self):
        return False

    def isOver(self):
        return False


class MapActivities(object):

    def __init__(self):
        self.__cbID = None
        self.__isOnArena = False
        self.__pendingActivities = []
        self.__currActivities = []
        PlayerEvents.g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        PlayerEvents.g_playerEvents.onAvatarBecomeNonPlayer += self._onAvatarBecomeNonPlayer
        PlayerEvents.g_playerEvents.onAvatarReady += self.__onAvatarReady
        return

    def destroy(self):
        BigWorld.cancelCallback(self.__cbID)
        self.__cbID = None
        self.stop()
        PlayerEvents.g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        PlayerEvents.g_playerEvents.onAvatarBecomeNonPlayer -= self._onAvatarBecomeNonPlayer
        PlayerEvents.g_playerEvents.onAvatarReady -= self.__onAvatarReady
        return

    def stop(self):
        for activity in self.__currActivities:
            activity.stop()

        for activity in self.__pendingActivities:
            activity.stop()

        self.__currActivities = []
        self.__pendingActivities = []

    def generateOfflineActivities(self, spacePath, usePossibility = True):
        xmlName = spacePath.split('/')[-1]
        settings = ResMgr.openSection('scripts/arena_defs/' + xmlName + '.xml/mapActivities')
        chooser = random.uniform if usePossibility else (lambda a, b: (a + b) / 2)
        if settings is not None:
            if usePossibility:
                SoundGroups.g_instance.enableArenaSounds(True)
        else:
            return
        startTimes = []
        for activityXML in settings.values():
            timeframe = activityXML.readVector2('startTime')
            possibility = activityXML.readFloat('possibility', 1.0)
            if possibility < chooser(0, 1) and usePossibility:
                startTimes.append(-1)
            else:
                startTimes.append(Timer.getTime() + chooser(timeframe[0], timeframe[1]))

        self.__generateActivities(settings, startTimes)
        self.__onPeriodicTimer()
        return

    def generateArenaActivities(self, startTimes):
        arenaType = BigWorld.player().arena.arenaType
        Timer.init()
        self.__generateActivities(arenaType.mapActivitiesSection, startTimes)

    def __generateActivities(self, settings, startTimes):
        self.__pendingActivities = []
        if settings is None or len(startTimes) != len(settings.items()):
            return
        else:
            i = -1
            for activityType, activityXML in settings.items():
                i += 1
                startTime = startTimes[i]
                if startTime == -1:
                    continue
                activity = _createActivity(activityType)
                if activity is not None:
                    activity.create(activityXML, startTime)
                    self.__pendingActivities.append(activity)

            return

    def __onPeriodicTimer(self):
        self.__cbID = None
        for activity in self.__currActivities:
            if activity.isOver():
                activity.stop()
                self.__currActivities.remove(activity)

        for activity in self.__pendingActivities:
            if activity.canStart():
                activity.start()
                if not activity.isPeriodic():
                    self.__currActivities.append(activity)
                    self.__pendingActivities.remove(activity)

        self.__cbID = BigWorld.callback(0.1, self.__onPeriodicTimer)
        return

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        isOnArena = period == ARENA_PERIOD.BATTLE
        if isOnArena and not self.__isOnArena:
            self.generateArenaActivities(periodAdditionalInfo)
        elif not isOnArena and self.__isOnArena:
            self.stop()
        self.__isOnArena = isOnArena

    def __onAvatarReady(self):
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
        self.__onPeriodicTimer()
        return

    def _onAvatarBecomeNonPlayer(self):
        self.__isOnArena = False
        self.stop()


class WarplaneActivity(IMapActivity):

    def create(self, settings, startTime):
        self.__settings = settings
        self.__curve = None
        self.__model = None
        self.__motor = None
        self.__sound = None
        self.__particles = None
        self.__particlesNode = None
        self.__cbID = None
        self.__startTime = startTime
        self.__fadedIn = False
        self.__period = self.__settings.readFloat('period', 0.0)
        self.__possibility = self.__settings.readFloat('possibility', 1.0)
        self.clampStartTime()
        self.__firstLaunch = True
        self.__curve = BigWorld.WGActionCurve(self.__settings)
        self.__modelName = self.__curve.getChannelProperty(0, 'modelName').asString
        BigWorld.loadResourceListBG((self.__modelName,), self.__onModelLoaded)
        return

    def isActive(self):
        return self.__model is not None

    def canStart(self):
        return Timer.getTime() >= self.__startTime and self.__model is not None

    def isPeriodic(self):
        return self.__period > 0.0

    def isOver(self):
        return Timer.getTime() > self.__endTime

    def clampStartTime(self):
        if self.isPeriodic() and Timer.getTime() > self.__startTime:
            self.__startTime = math.floor((Timer.getTime() - self.__startTime) / self.__period) * self.__period + self.__startTime

    def setStartTime(self, parentStartTime):
        if not self.__firstLaunch:
            self.pause()
        timeFrame = self.__settings.readVector2('startTime')
        self.__startTime = parentStartTime + random.uniform(timeFrame[0], timeFrame[1])
        self.clampStartTime()

    def setPeriod(self, period):
        self.__period = period

    def start(self):
        if self.isPeriodic() and self.__possibility < random.uniform(0.0, 1.0):
            self.__startTime += self.__period
            return
        else:
            if self.__firstLaunch is True:
                BigWorld.addModel(self.__model)
                self.__model.forceReflect = True
                self.__motor = BigWorld.WGWarplaneMotor(self.__curve, 0)
                self.__model.addMotor(self.__motor)
                self.__endTime = self.__motor.totalTime + self.__startTime
                if self.__endTime <= Timer.getTime():
                    self.__fadedIn = True
                else:
                    self.__motor.restart(Timer.getTime() - self.__startTime)
                self.__firstLaunch = False
            else:
                self.pause()
                if self.__motor is not None:
                    self.__model.addMotor(self.__motor)
                    self.__motor.restart()
                    self.__endTime = self.__motor.totalTime + self.__startTime
                if self.__cbID is not None:
                    BigWorld.cancelCallback(self.__cbID)
                if self.__sound is not None:
                    self.__sound.stop()
                    self.__sound = None
                self.__fadedIn = False
            self.__model.visible = 1
            self.__startTime += self.__period
            self.__waitEnterWorld()
            return

    def stop(self):
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        if self.__model is not None:
            if self.__motor is not None and self.__motor in self.__model.motors:
                self.__model.delMotor(self.__motor)
            if self.__model in BigWorld.models():
                BigWorld.delModel(self.__model)
            self.__model = None
            self.__motor = None
            self.__curve = None
        if self.__sound is not None:
            self.__sound.stop()
            self.__sound = None
        if self.__particles is not None:
            self.__particlesNode.detach(self.__particles)
            self.__particlesNode = None
            self.__particles = None
        self.__firstLaunch = True
        return

    def pause(self):
        if self.__sound is not None:
            self.__sound.stop()
            self.__sound = None
        if self.__particles is not None:
            self.__particlesNode.detach(self.__particles)
            self.__particlesNode = None
            self.__particles = None
        if self.__model is not None:
            if self.__motor is not None and self.__motor in self.__model.motors:
                self.__model.delMotor(self.__motor)
            self.__model.visible = 0
        return

    def __waitEnterWorld(self):
        self.__cbID = None
        if self.__model.inWorld is True:
            self.__update()
            return
        else:
            self.__cbID = BigWorld.callback(0.1, self.__waitEnterWorld)
            return

    def __update(self):
        self.__cbID = None
        visibility = self.__motor.warplaneAlpha
        if visibility == 1.0 and not self.__fadedIn:
            self.__fadedIn = True
            ds = self.__curve.getChannelProperty(0, 'effectName')
            effectName = ds.asString if ds is not None else ''
            if effectName != '':
                Pixie.createBG(effectName, partial(self.__onParticlesLoaded, effectName))
        elif visibility <= 0.1 and self.__fadedIn or Timer.getTime() > self.__endTime:
            self.pause()
            return
        if self.__sound is not None:
            if self.__sound.isPlaying:
                self.__sound.volume = visibility
        else:
            self.__playSound()
        self.__cbID = BigWorld.callback(0.25, self.__update)
        return

    def __onModelLoaded(self, resourceRefs):
        if self.__modelName not in resourceRefs.failedIDs:
            self.__model = resourceRefs[self.__modelName]
        else:
            LOG_ERROR('Could not load model %s' % self.__modelName)

    def __onParticlesLoaded(self, effectName, particles):
        if self.__curve is None:
            return
        else:
            propValue = self.__curve.getChannelProperty(0, 'effectHardpoint')
            if particles is None:
                LOG_ERROR("Can't create pixie '%s'." % effectName)
                return
            if propValue is None:
                return
            hardPointName = propValue.asString
            if hardPointName != '':
                self.__particles = particles
                self.__particlesNode = self.__model.node(hardPointName)
                self.__particlesNode.attach(self.__particles)
            return

    def __playSound(self):
        ds = self.__curve.getChannelProperty(0, 'soundName')
        soundName = ds.asString if ds is not None else ''
        if soundName != '':
            try:
                self.__sound = SoundGroups.g_instance.playSoundModel(self.__model, soundName)
                self.__sound.volume = 0.0
            except:
                self.__sound = None
                LOG_CURRENT_EXCEPTION()

        return


class ScenarioActivity(IMapActivity):

    def __init__(self):
        self.__cbID = None
        self.__currentActivities = []
        self.__pendingActivities = []
        self.__startTime = sys.maxint
        self.__period = 0.0
        return

    def create(self, settings, startTime):
        self.__startTime = startTime
        trajectories = settings['trajectories']
        if trajectories is None:
            return
        else:
            self.__period = settings.readFloat('period', 0.0)
            for activityType, activityXML in trajectories.items():
                activity = _createActivity(activityType)
                if activity is not None:
                    activity.create(activityXML, sys.maxint)
                    self.__pendingActivities.append(activity)

            return

    def clampStartTime(self):
        if self.isPeriodic() and Timer.getTime() > self.__startTime:
            self.__startTime = math.floor((Timer.getTime() - self.__startTime) / self.__period) * self.__period + self.__startTime

    def start(self):
        self.__pendingActivities.extend(self.__currentActivities)
        self.__currentActivities = []
        for activity in self.__pendingActivities:
            activity.setStartTime(self.__startTime)

        self.__startTime += self.__period
        self.__onPeriodicTimer()

    def stop(self):
        for activity in self.__currentActivities:
            activity.stop()

        for activity in self.__pendingActivities:
            activity.stop()

        self.__currentActivities = []
        self.__pendingActivities = []

    def canStart(self):
        return Timer.getTime() >= self.__startTime

    def isActive(self):
        return Timer.getTime() >= self.__startTime

    def isPeriodic(self):
        return self.__period > 0.0

    def __onPeriodicTimer(self):
        self.__cbID = None
        if not self.isPeriodic():
            for activity in self.__currentActivities:
                if activity.isOver():
                    activity.stop()
                    self.__currentActivities.remove(activity)

        for activity in self.__pendingActivities:
            if activity.canStart():
                activity.start()
                if not activity.isPeriodic():
                    self.__currentActivities.append(activity)
                    self.__pendingActivities.remove(activity)

        BigWorld.callback(0.1, self.__onPeriodicTimer)
        return


def _createActivity(typeName):
    if typeName == 'warplane':
        return WarplaneActivity()
    elif typeName == 'scenario':
        return ScenarioActivity()
    else:
        return None


g_mapActivities = MapActivities()
Timer.init()
