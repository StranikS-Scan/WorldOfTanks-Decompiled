# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MapActivities.py
import math
import random
import sys
import BigWorld
import ResMgr
import PlayerEvents
from constants import ARENA_PERIOD
import SoundGroups
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from helpers.PixieBG import PixieBG
from helpers import dependency
from skeletons.map_activities import IMapActivities

class Timer(object):
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


class BaseMapActivity(object):
    arenaPeriod = property(lambda self: self._arenaPeriod)
    name = property(lambda self: self._name)

    def __init__(self):
        self._startTime = sys.maxint
        self._interval = 0.0
        self._arenaPeriod = 0
        self._name = ''

    def create(self, settings):
        self._settings = settings
        self._arenaPeriod = settings.readInt('arenaPeriod', 0)

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

    def isRepeating(self):
        return self._interval > 0.0

    def isOver(self):
        return False

    def setStartTime(self, startTime):
        self._startTime = startTime

    def _readInterval(self):
        self._interval = self._settings.readFloat('interval', 0.0)

    def _readName(self):
        self._name = self._settings.readString('name', '')


class MapActivities(IMapActivities):

    def __init__(self):
        self.__cbID = None
        self.__isOnArena = False
        self.__pendingActivities = []
        self.__currActivities = []
        self.__arenaPeriod = None
        PlayerEvents.g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
        PlayerEvents.g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        PlayerEvents.g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer
        PlayerEvents.g_playerEvents.onAvatarReady += self.__onAvatarReady
        return

    def destroy(self):
        self.stop()
        PlayerEvents.g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        PlayerEvents.g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        PlayerEvents.g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        PlayerEvents.g_playerEvents.onAvatarReady -= self.__onAvatarReady

    def start(self, name, targetTime):
        for _, activity in self.__pendingActivities:
            if activity.name == name:
                activity.setStartTime(targetTime)

    def stop(self):
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        for activity in self.__currActivities:
            activity.stop()

        for _, activity in self.__pendingActivities:
            activity.stop()

        del self.__currActivities[:]
        del self.__pendingActivities[:]
        return

    def generateOfflineActivities(self, spacePath, usePossibility=True):
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
            startTimes.append(Timer.getTime() + chooser(timeframe[0], timeframe[1]))

        self.__generateActivities(settings)
        self.__setStartTimes(startTimes)
        self.__startArenaPeriodSpecificActivities(0, 0)
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        self.__onPeriodicTimer()
        return

    def generateArenaActivitiesTests(self):
        self._generateArenaActivities()

    def _generateArenaActivities(self):
        Timer.init()
        arenaType = BigWorld.player().arena.arenaType
        self.__generateActivities(arenaType.mapActivitiesSection)

    def __generateActivities(self, settings):
        self.__pendingActivities = []
        if settings is None:
            return
        else:
            for activityType, activityXML in settings.items():
                activity = _createActivity(activityType)
                if activity is not None:
                    if activity.create(activityXML):
                        self.__pendingActivities.append((sys.maxint, activity))

            return

    def __setStartTimes(self, startTimes):
        startTimeLength = len(startTimes)
        if startTimeLength != len(self.__pendingActivities):
            return
        for index in range(startTimeLength):
            _, activity = self.__pendingActivities[index]
            self.__pendingActivities[index] = (startTimes[index], activity)

    def __onPeriodicTimer(self):
        self.__cbID = None
        for activity in self.__currActivities:
            if activity.isOver():
                activity.stop()
                self.__currActivities.remove(activity)

        for time, activity in self.__pendingActivities:
            if activity.arenaPeriod == self.__arenaPeriod or activity.arenaPeriod == 0:
                if activity.canStart():
                    activity.start()
                    if not activity.isRepeating():
                        self.__currActivities.append(activity)
                        self.__pendingActivities.remove((time, activity))

        self.__cbID = BigWorld.callback(0.1, self.__onPeriodicTimer)
        return

    def __onAvatarBecomePlayer(self):
        self._generateArenaActivities()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        isOnArena = period in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE, ARENA_PERIOD.AFTERBATTLE)
        if period in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE):
            self.__setStartTimes(periodAdditionalInfo)
        self.__isOnArena = isOnArena
        self.__arenaPeriod = period
        if self.__isOnArena:
            periodStartTime = periodEndTime - periodLength
            self.__startArenaPeriodSpecificActivities(period, periodStartTime)

    def __startArenaPeriodSpecificActivities(self, period, periodStartTime):
        for relativeStartTime, activity in self.__pendingActivities:
            if activity.arenaPeriod == period:
                activity.setStartTime(periodStartTime + relativeStartTime)

    def __onAvatarReady(self):
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        self.__onPeriodicTimer()
        return

    def __onAvatarBecomeNonPlayer(self):
        self.__isOnArena = False
        self.stop()


class WaveImpulse(object):

    def __init__(self, startImpulse, endImpulse, deltaTime, deltaImpulse):
        self.__position = (0.0, 0.0, 0.0)
        self.__impulse = startImpulse
        self.__endImpulse = endImpulse
        self.__deltaTime = deltaTime
        self.__deltaImpulse = deltaImpulse
        self.__cbkId = None
        return

    def start(self, position):
        if self.__cbkId is not None:
            BigWorld.cancelCallback(self.__cbkId)
            self.__cbkId = None
        if self.__deltaImpulse < 0.0:
            self.__position = position
            self.__cbkId = BigWorld.callback(self.__deltaTime, self.__loop)
        return

    def __loop(self):
        player = BigWorld.player()
        if player is not None:
            player.inputHandler.onExplosionImpulse(self.__position, self.__impulse)
        if self.__impulse > self.__endImpulse:
            self.__impulse += self.__deltaImpulse
            self.__cbkId = BigWorld.callback(self.__deltaTime, self.__loop)
        else:
            self.__cbkId = None
        return

    def destroy(self):
        if self.__cbkId is not None:
            BigWorld.cancelCallback(self.__cbkId)
            self.__cbkId = None
        return


class WarplaneActivity(BaseMapActivity):
    FADE_TIME = 450.0

    def __init__(self):
        BaseMapActivity.__init__(self)
        self.__endTime = sys.maxint

    def create(self, settings):
        BaseMapActivity.create(self, settings)
        self.__isStopped = False
        self.__curve = None
        self.__model = None
        self.__motor = None
        self.__particle = (None, None)
        self.__cbID = None
        self.__fadedIn = False
        self.__possibility = self._settings.readFloat('possibility', 1.0)
        self.clampStartTime()
        self.__firstLaunch = True
        self.__curve = BigWorld.WGActionCurve(self._settings)
        self.__modelName = self.__curve.getChannelProperty(0, 'modelName').asString
        ds = self.__curve.getChannelProperty(0, 'wwsoundName')
        soundName = ds.asString if ds is not None else ''
        if soundName != '':
            self.__sound = SoundGroups.g_instance.getSound3D(None, soundName)
        else:
            self.__sound = None
        BigWorld.loadResourceListBG((self.__modelName,), self.__onModelLoaded)
        return True

    def isActive(self):
        return self.__model is not None

    def canStart(self):
        return self._startTime != -1.0 and Timer.getTime() >= self._startTime and self.__model is not None

    def isOver(self):
        return Timer.getTime() > self.__endTime

    def clampStartTime(self):
        if self.isRepeating() and Timer.getTime() > self._startTime:
            self._startTime += math.floor((Timer.getTime() - self._startTime) / self._interval) * self._interval

    def setStartTime(self, parentStartTime):
        if not self.__firstLaunch:
            self.pause()
        timeFrame = self._settings.readVector2('startTime')
        self._startTime = parentStartTime + random.uniform(timeFrame[0], timeFrame[1])
        self.clampStartTime()

    def setPeriod(self, period):
        self._interval = period

    def start(self):
        self.__isStopped = False
        if self.isRepeating() and self.__possibility < random.uniform(0.0, 1.0):
            self._startTime += self._interval
            return
        else:
            if self.__firstLaunch is True:
                BigWorld.addModel(self.__model)
                self.__model.forceReflect = True
                self.__motor = BigWorld.WGWarplaneMotor(self.__curve, 0)
                self.__model.addMotor(self.__motor)
                self.__endTime = self.__motor.totalTime + self._startTime
                if self.__endTime <= Timer.getTime():
                    self.__fadedIn = True
                else:
                    self.__motor.restart(Timer.getTime() - self._startTime)
                self.__firstLaunch = False
            else:
                self.pause()
                if self.__motor is not None:
                    self.__model.addMotor(self.__motor)
                    self.__motor.restart(Timer.getTime() - self._startTime)
                    self.__endTime = self.__motor.totalTime + self._startTime
                self.__fadedIn = False
            self.__model.visible = 1
            self._startTime += self._interval
            if self.__cbID is not None:
                BigWorld.cancelCallback(self.__cbID)
                self.__cbID = None
            self.__waitEnterWorld()
            return

    def stop(self):
        self.__isStopped = True
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
            self.__sound.stop(self.FADE_TIME)
            self.__sound.releaseMatrix()
        if self.__particle[1] is not None and self.__particle[1].pixie is not None:
            self.__particle[0].detach(self.__particle[1].pixie)
            self.__particle[1].destroy()
        self.__particle = (None, None)
        self.__firstLaunch = True
        return

    def pause(self):
        if self.__sound is not None:
            self.__sound.stop(self.FADE_TIME)
            self.__sound.releaseMatrix()
        if self.__particle[1] is not None and self.__particle[1].pixie is not None:
            self.__particle[0].detach(self.__particle[1].pixie)
        self.__particle = (None, None)
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
        if visibility > 0.7:
            self.__loadEffects()
        if visibility > 0.1:
            if not self.__fadedIn:
                self.__fadedIn = True
                if self.__sound is not None:
                    self.__sound.play()
                    self.__sound.volume = visibility
                    if self.__model is not None:
                        self.__sound.matrixProvider = self.__model.root
            elif self.__sound is not None:
                self.__sound.volume = visibility
        elif visibility <= 0.1 and self.__fadedIn or Timer.getTime() > self.__endTime:
            self.pause()
            return
        self.__cbID = BigWorld.callback(0.25, self.__update)
        return

    def __onModelLoaded(self, resourceRefs):
        if self.__modelName not in resourceRefs.failedIDs and not self.__isStopped:
            self.__model = resourceRefs[self.__modelName]
        else:
            LOG_ERROR('Could not load model %s' % self.__modelName)

    def __loadEffects(self):
        if self.__particle[0] is None and self.__particle[1] is None:
            if self.__curve is None:
                return
            propValue = self.__curve.getChannelProperty(0, 'effectHardpoint')
            hardPointName = propValue.asString if propValue is not None else ''
            if hardPointName == '':
                return
            ds = self.__curve.getChannelProperty(0, 'effectName')
            effectName = ds.asString if ds is not None else ''
            if effectName != '':
                modelNode = self.__model.node(hardPointName)
                self.__particle = (modelNode, PixieBG(effectName, self.__onParticlesLoaded))
        return

    def __onParticlesLoaded(self, pixieBG):
        if self.__particle[0] is not None:
            self.__particle[0].attach(pixieBG.pixie)
        return


class ExplosionActivity(BaseMapActivity):

    def create(self, settings):
        BaseMapActivity.create(self, settings)
        self.__isStopped = False
        self.__model = None
        self.__sound = None
        self.__cbID = None
        self.__fadedIn = False
        self._readInterval()
        self.__possibility = self._settings.readFloat('possibility', 1.0)
        self.__position = self._settings.readVector3('position', (0.0, 0.0, 0.0))
        curveSettings = BigWorld.WGActionCurve(self._settings)
        self.__soundName = None
        self.__soundName = curveSettings.getChannelProperty(0, 'wwsoundName')
        if self.__soundName is not None:
            self.__soundName = self.__soundName.asString
        else:
            self.__soundName = ''
        waveImpulseDs = curveSettings.getChannelProperty(0, 'waveImpulse')
        if waveImpulseDs is not None:
            startImpulse = waveImpulseDs.readFloat('start', 0.0)
            endImpulse = waveImpulseDs.readFloat('end', 0.0)
            count = waveImpulseDs.readInt('count', 0) - 1
            time = waveImpulseDs.readFloat('time', 0.0)
            if count >= 0 and time > 0.0:
                deltaTime = time / count
                deltaImpulse = (endImpulse - startImpulse) / count
                self.__waveImpulse = WaveImpulse(startImpulse, endImpulse, deltaTime, deltaImpulse)
        self.clampStartTime()
        self.__firstLaunch = True
        self.__modelName = curveSettings.getChannelProperty(0, 'modelName').asString
        BigWorld.loadResourceListBG((self.__modelName,), self.__onModelLoaded)
        self.__isOver = True
        return True

    def __del__(self):
        if self.__waveImpulse is not None:
            self.__waveImpulse.destroy()
            self.__waveImpulse = None
        return

    def isActive(self):
        return self.__model is not None

    def canStart(self):
        return Timer.getTime() >= self._startTime and self.__model is not None

    def isOver(self):
        return self.__isOver

    def clampStartTime(self):
        if self.isRepeating() and Timer.getTime() > self._startTime:
            self._startTime = math.floor((Timer.getTime() - self._startTime) / self._interval) * self._interval + self._startTime

    def setStartTime(self, parentStartTime):
        if not self.__firstLaunch:
            self.pause()
        timeFrame = self._settings.readVector2('startTime')
        self._startTime = parentStartTime + random.uniform(timeFrame[0], timeFrame[1])
        self.clampStartTime()

    def setPeriod(self, interval):
        self._interval = interval

    def start(self):
        self.__isOver = False
        if self.isRepeating() and self.__possibility < random.uniform(0.0, 1.0):
            self._startTime += self._interval
            return
        else:
            if self.__firstLaunch is True:
                BigWorld.addModel(self.__model)
                self.__model.forceReflect = True
                self.__firstLaunch = False
            else:
                self.pause()
            self.__model.visible = 1
            self._startTime += self._interval
            if self.__cbID is not None:
                BigWorld.cancelCallback(self.__cbID)
                self.__cbID = None
            self.__waitEnterWorld()
            return

    def stop(self):
        self.__isStopped = True
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        if self.__model is not None:
            if self.__model in BigWorld.models():
                BigWorld.delModel(self.__model)
            self.__model = None
            self.__motor = None
        if self.__sound is not None:
            self.__sound.stop()
            self.__sound.releaseMatrix()
            self.__sound = None
        self.__firstLaunch = True
        if self.__waveImpulse is not None:
            self.__waveImpulse.destroy()
            self.__waveImpulse = None
        return

    def pause(self):
        if self.__sound is not None:
            self.__sound.stop()
            self.__sound.releaseMatrix()
            self.__sound = None
        if self.__model is not None:
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
        if self.__sound is None:
            self.__playSound()
            self.__waveImpulse.start(self.__model.position)
        self.__cbID = BigWorld.callback(0.25, self.__update)
        return

    def __endEventCallback(self, sound):
        self.pause()
        self.__isOver = True
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        return

    def __onModelLoaded(self, resourceRefs):
        if self.__modelName not in resourceRefs.failedIDs and not self.__isStopped:
            self.__model = resourceRefs[self.__modelName]
            self.__model.position = self.__position
        else:
            LOG_ERROR('Could not load model %s' % self.__modelName)

    def __playSound(self):
        if self.__soundName != '':
            try:
                self.__sound = SoundGroups.g_instance.getSound3D(self.__model.root, self.__soundName)
                self.__sound.setCallback(self.__endEventCallback)
                self.__sound.play()
            except Exception:
                self.__sound = None
                LOG_CURRENT_EXCEPTION()

        return


class ScenarioActivity(BaseMapActivity):

    def __init__(self):
        BaseMapActivity.__init__(self)
        self.__cbID = None
        self.__currentActivities = []
        self.__pendingActivities = []
        return

    def create(self, settings):
        BaseMapActivity.create(self, settings)
        trajectories = settings['trajectories']
        if trajectories is None:
            return
        else:
            self._readInterval()
            self._readName()
            for activityType, activityXML in trajectories.items():
                activity = _createActivity(activityType)
                if activity is not None:
                    activity.create(activityXML)
                    self.__pendingActivities.append(activity)

            return True

    def setStartTime(self, time):
        self._startTime = time

    def start(self):
        self.__pendingActivities.extend(self.__currentActivities)
        self.__currentActivities = []
        for activity in self.__pendingActivities:
            activity.setStartTime(self._startTime)

        self._startTime += self._interval
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        self.__onPeriodicTimer()
        return

    def stop(self):
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        for activity in self.__currentActivities:
            activity.stop()

        for activity in self.__pendingActivities:
            activity.stop()

        del self.__currentActivities[:]
        del self.__pendingActivities[:]
        return

    def canStart(self):
        return Timer.getTime() >= self._startTime

    def isActive(self):
        return Timer.getTime() >= self._startTime and (len(self.__pendingActivities) != 0 or len(self.__currentActivities) != 0)

    def isOver(self):
        over = Timer.getTime() >= self._startTime and all(map(lambda subActivity: subActivity.isOver(), self.__currentActivities + self.__pendingActivities))
        return over

    def __onPeriodicTimer(self):
        self.__cbID = None
        if not self.isRepeating():
            for activity in self.__currentActivities:
                if activity.isOver():
                    activity.stop()
                    self.__currentActivities.remove(activity)

        for activity in self.__pendingActivities:
            if activity.canStart():
                activity.start()
                if not activity.isRepeating():
                    self.__currentActivities.append(activity)
                    self.__pendingActivities.remove(activity)

        self.__cbID = BigWorld.callback(0.1, self.__onPeriodicTimer)
        return


def _createActivity(typeName):
    if typeName == 'warplane':
        return WarplaneActivity()
    elif typeName == 'scenario':
        return ScenarioActivity()
    else:
        return ExplosionActivity() if typeName == 'explosion' else None


def startActivity(name, timeOffset=0.0):
    mapActivities = dependency.instance(IMapActivities)
    mapActivities.start(name, Timer.getTime() + timeOffset)


Timer.init()
