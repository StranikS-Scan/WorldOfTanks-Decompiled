# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MapActivities.py
import sys
import math
import random
import BigWorld
import ResMgr
import PlayerEvents
import SoundGroups
from constants import ARENA_PERIOD
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from helpers.PixieBG import PixieBG

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


class IMapActivity(object):

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

    def name(self):
        pass


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

    def start(self, name):
        for activity in self.__pendingActivities:
            if activity.name() == name:
                activity.setStartTime(Timer.getTime())

    def stop(self):
        for activity in self.__currActivities:
            activity.stop()

        for activity in self.__pendingActivities:
            activity.stop()

        self.__currActivities = []
        self.__pendingActivities = []

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
                activity = _createActivity(activityType)
                if activity is not None:
                    if activity.create(activityXML, startTime):
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
        isOnArena = period in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE)
        if isOnArena and not self.__isOnArena:
            self.generateArenaActivities(periodAdditionalInfo)
        self.__isOnArena = isOnArena

    def __onAvatarReady(self):
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
        self.__onPeriodicTimer()
        return

    def _onAvatarBecomeNonPlayer(self):
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
        if self.__deltaImpulse < 0.0:
            self.__position = position
            self.__cbkId = BigWorld.callback(self.__deltaTime, self.__loop)

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


class WarplaneActivity(IMapActivity):

    def create(self, settings, startTime):
        self.__settings = settings
        self.__curve = None
        self.__model = None
        self.__motor = None
        self.__sound = None
        self.__particle = (None, None)
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
        return True

    def isActive(self):
        return self.__model is not None

    def canStart(self):
        return self.__startTime != -1.0 and Timer.getTime() >= self.__startTime and self.__model is not None

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
                    self.__sound.stopAll()
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
            self.__sound.stopAll()
            self.__sound = None
        if self.__particle[1] is not None and self.__particle[1].pixie is not None:
            self.__particle[0].detach(self.__particle[1].pixie)
            self.__particle[1].destroy()
        self.__particle = (None, None)
        self.__firstLaunch = True
        return

    def pause(self):
        if self.__sound is not None:
            self.__sound.stopAll()
            self.__sound = None
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
        if visibility == 1.0 and not self.__fadedIn:
            self.__fadedIn = True
        elif visibility <= 0.1 and self.__fadedIn or Timer.getTime() > self.__endTime:
            self.pause()
            return
        if self.__sound is not None:
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

    def __playSound(self):
        ds = self.__curve.getChannelProperty(0, 'wwsoundName')
        soundName = ds.asString if ds is not None else ''
        if soundName != '':
            try:
                objectName = soundName + ' : ' + str(self.__model.root)
                self.__sound = SoundGroups.g_instance.WWgetSoundObject(objectName, self.__model.root)
                self.__sound.play(soundName)
                self.__sound.volume = 0.0
            except Exception:
                self.__sound = None
                LOG_CURRENT_EXCEPTION()

        return


class ExplosionActivity(IMapActivity):

    def create(self, settings, startTime):
        self.__settings = settings
        self.__model = None
        self.__sound = None
        self.__cbID = None
        self.__startTime = startTime
        self.__fadedIn = False
        self.__period = self.__settings.readFloat('period', 0.0)
        self.__possibility = self.__settings.readFloat('possibility', 1.0)
        self.__position = self.__settings.readVector3('position', (0.0, 0.0, 0.0))
        curveSettings = BigWorld.WGActionCurve(self.__settings)
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
        return Timer.getTime() >= self.__startTime and self.__model is not None

    def isPeriodic(self):
        return self.__period > 0.0

    def isOver(self):
        return self.__isOver

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
        self.__isOver = False
        if self.isPeriodic() and self.__possibility < random.uniform(0.0, 1.0):
            self.__startTime += self.__period
            return
        if self.__firstLaunch is True:
            BigWorld.addModel(self.__model)
            self.__model.forceReflect = True
            self.__firstLaunch = False
        else:
            self.pause()
        self.__model.visible = 1
        self.__startTime += self.__period
        self.__waitEnterWorld()

    def stop(self):
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
        if self.__modelName not in resourceRefs.failedIDs:
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


class ScenarioActivity(IMapActivity):

    def __init__(self):
        self.__cbID = None
        self.__currentActivities = []
        self.__pendingActivities = []
        self.__startTime = sys.maxint
        self.__period = 0.0
        self.__name = ''
        return

    def name(self):
        return self.__name

    def create(self, settings, startTime):
        trajectories = settings['trajectories']
        if trajectories is None:
            return
        else:
            self.__period = settings.readFloat('period', 0.0)
            self.__name = settings.readString('name', '')
            if self.__name == '':
                if startTime == -1:
                    return False
            if self.__period > -1.0:
                self.__startTime = startTime
            for activityType, activityXML in trajectories.items():
                activity = _createActivity(activityType)
                if activity is not None:
                    activity.create(activityXML, sys.maxint)
                    self.__pendingActivities.append(activity)

            return True

    def clampStartTime(self):
        if self.isPeriodic() and Timer.getTime() > self.__startTime:
            self.__startTime = math.floor((Timer.getTime() - self.__startTime) / self.__period) * self.__period + self.__startTime

    def setStartTime(self, time):
        self.__startTime = time

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
        return ExplosionActivity() if typeName == 'explosion' else None


def startActivity(name):
    global g_mapActivities
    g_mapActivities.start(name)


g_mapActivities = MapActivities()
Timer.init()
