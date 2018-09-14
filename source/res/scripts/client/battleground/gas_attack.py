# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/gas_attack.py
from collections import namedtuple
import math
from AvatarInputHandler import mathUtils
import BigWorld
from CTFManager import g_ctfManager
import Event
import MapActivities
from Math import Vector3
import Math
import ResMgr
import constants
from constants import ARENA_BONUS_TYPE_CAPS as caps
from debug_utils import LOG_DEBUG, LOG_ERROR
from helpers import EffectsList
from helpers.CallbackDelayer import CallbackDelayer
from GasAttackSettings import GasAttackSettings, GasAttackState
import BattlegroundElements
_ENABLE_DEBUG_LOG = constants.IS_DEVELOPMENT
_ENABLE_DEBUG_DRAW = constants.IS_DEVELOPMENT and False

class GasAttackMapSettings(namedtuple('GasAttackMapSettings', ('cloudModel', 'cloudClimbTime', 'cloudStartHeight', 'cloudEndHeight', 'cameraProximityDist', 'windSpeed', 'windGustiness', 'mapActivities', 'centerFogSettings', 'edgeFogSettings', 'soundSettings'))):

    @staticmethod
    def fromSection(dataSection):
        assert isinstance(dataSection, ResMgr.DataSection)
        it = iter(GasAttackMapSettings._fields)
        return GasAttackMapSettings(dataSection.readString(next(it)), dataSection.readFloat(next(it)), dataSection.readFloat(next(it)), dataSection.readFloat(next(it)), dataSection.readFloat(next(it)), dataSection.readVector2(next(it)), dataSection.readFloat(next(it)), tuple(dataSection.readString(next(it)).split()), dataSection[next(it)], dataSection[next(it)], dataSection[next(it)])


def _getSoundSettings():
    soundSettings = ResMgr.DataSection()
    soundSettings.createSectionFromString('\n\t<soundSettings>\n\t\t<wwalarm>fallout_gaz_alarm</wwalarm>\n\t\t<alarm>/GUI/fallout/fallout_gaz_alarm</alarm>\n\t</soundSettings>\n')
    return soundSettings


def _getDefaultMapSettings():
    edgeFogSettings = ResMgr.DataSection()
    edgeFogSettings.createSectionFromString('\n<Fog>\n\t<version>\t1.000000\t</version>\n\t<innerBB>\t-0.000000 -0.000000 0.000000 200.000000\t</innerBB>\n\t<outerBB>\t-200.000000 -200.000000 200.000000 400.000000\t</outerBB>\n\t<deferred>\n\t\t<heightFog>\ttrue\t</heightFog>\n\t\t<nearLow>\t0.000000\t</nearLow>\n\t\t<farLow>\t100.000000\t</farLow>\n\t\t<nearHigh>\t10.000000\t</nearHigh>\n\t\t<farHigh>\t100.000000\t</farHigh>\n\t\t<altitudeLow>\t-6.000000\t</altitudeLow>\n\t\t<altitudeMid>\t10.000000\t</altitudeMid>\n\t\t<altitudeHigh>\t100.000000\t</altitudeHigh>\n\t\t<skyAltitudeLow>\t-10.000000\t</skyAltitudeLow>\n\t\t<skyAltitudeMid>\t10.000000\t</skyAltitudeMid>\n\t\t<skyAltitudeHigh>\t1500.000000\t</skyAltitudeHigh>\n\t\t<exponent>\t0.650000\t</exponent>\n\t\t<sunAngle>\t35.000000\t</sunAngle>\n\t\t<sunExponent>\t0.500000\t</sunExponent>\n\t\t<colorLow>\t0.991500 1.000000 0.490000 0.400000\t</colorLow>\n\t\t<colorHigh>\t0.991501 1.000000 0.490000 0.300000\t</colorHigh>\n\t\t<colorSunLow>\t0.991500 1.000000 0.490000 0.500000\t</colorSunLow>\n\t\t<colorSunHigh>\t0.991500 1.000000 0.490000 0.450000\t</colorSunHigh>\n\t\t<useEdgeFog>\ttrue\t</useEdgeFog>\n\t</deferred>\n\t<forward>\n\t\t<heightFog>\ttrue\t</heightFog>\n\t\t<nearLow>\t0.000000\t</nearLow>\n\t\t<farLow>\t100.000000\t</farLow>\n\t\t<nearHigh>\t10.000000\t</nearHigh>\n\t\t<farHigh>\t100.000000\t</farHigh>\n\t\t<altitudeLow>\t-18.000000\t</altitudeLow>\n\t\t<altitudeMid>\t9.000000\t</altitudeMid>\n\t\t<altitudeHigh>\t200.000000\t</altitudeHigh>\n\t\t<skyAltitudeLow>\t0.000000\t</skyAltitudeLow>\n\t\t<skyAltitudeMid>\t10.000000\t</skyAltitudeMid>\n\t\t<skyAltitudeHigh>\t1300.000000\t</skyAltitudeHigh>\n\t\t<colorLow>\t0.684355 0.694268 0.552637 0.000000\t</colorLow>\n\t\t<colorHigh>\t0.684363 0.694268 0.552761 0.000000\t</colorHigh>\n\t\t<useEdgeFog>\ttrue\t</useEdgeFog>\n\t</forward>\n\t<enable>\ttrue\t</enable>\n</Fog>\n')
    return GasAttackMapSettings(cloudModel='particles/mesh_particles/funnel_death/gas_ring.model', cloudClimbTime=5, cloudStartHeight=0, cloudEndHeight=150, cameraProximityDist=30, windSpeed=Math.Vector2(50, 50), windGustiness=50, mapActivities=(), centerFogSettings=edgeFogSettings, edgeFogSettings=edgeFogSettings, soundSettings=_getSoundSettings())


def _getDefaultScenario():
    settings = BigWorld.player().arena.arenaType.gasAttackSettings
    if settings is not None:
        return (BigWorld.serverTime() + 2, settings)
    else:
        return (BigWorld.serverTime() + 2, GasAttackSettings(attackLength=100, preparationPeriod=5, position=Math.Vector3(BigWorld.camera().position.x, 0, BigWorld.camera().position.z), startRadius=300, endRadius=100, compressionTime=10))


class GasCloud(object):

    def __setModel(self, model):
        if self.__cloud is None or model is None:
            return
        else:
            self.__model = model
            self.__model.addMotor(BigWorld.Servo(self.__cloud.cloudMatrixProvider))
            BigWorld.addModel(self.__model)
            tintFashion = BattlegroundElements.TintFashion(self.__cloud.tintColorLink)
            self.__model.fashion = tintFashion
            return

    model = property(lambda self: self.__model, __setModel)
    cloudControl = property(lambda self: self.__cloud)

    def __init__(self, mapSettings = None, startTime = None, gasAttackSettings = None, cloudModel = None):
        if mapSettings is None:
            mapSettings = _getDefaultMapSettings()
        if gasAttackSettings is None or startTime is None:
            startTime, gasAttackSettings = _getDefaultScenario()
        assert isinstance(mapSettings, GasAttackMapSettings)
        gasCloudSettings = (gasAttackSettings.position,
         startTime,
         mapSettings.cameraProximityDist,
         gasAttackSettings.compressionTime,
         gasAttackSettings.startRadius,
         gasAttackSettings.endRadius,
         mapSettings.cloudClimbTime,
         mapSettings.cloudStartHeight,
         mapSettings.cloudEndHeight,
         math.radians(36.45),
         mapSettings.centerFogSettings,
         mapSettings.edgeFogSettings)
        self.__cloud = BattlegroundElements.GasCloud(gasCloudSettings)
        self.__cloud.start()
        self.__model = None
        self.model = cloudModel
        weather = BigWorld.weather(BigWorld.player().spaceID)
        weather.windAverage(*mapSettings.windSpeed.tuple())
        weather.windGustiness(mapSettings.windGustiness)
        self.__cloud.setProximityCallback(self.__onProximity)
        self.__started = False
        if _ENABLE_DEBUG_DRAW:
            import Flock
            d = Flock.DebugGizmo(BigWorld.player().spaceID, 'helpers/models/unit_cube.model')
            d.motor.signal = self.__cloud.cloudMatrixProvider
        ctrlName = BigWorld.player().inputHandler.ctrlModeName
        self.__cloud.enableEdgeFogEffects = ctrlName != 'postmortem' or BigWorld.player().vehicle is not None
        BigWorld.player().inputHandler.onPostmortemVehicleChanged += self.__onPostmortemVehicleChanged
        return

    def destroy(self):
        BigWorld.player().inputHandler.onPostmortemVehicleChanged -= self.__onPostmortemVehicleChanged
        self.__cloud = None
        if self.__model is not None:
            BigWorld.delModel(self.__model)
        return

    def __onProximity(self, entered):
        pass

    def __onPostmortemVehicleChanged(self, vehicleID):
        self.__cloud.enableEdgeFogEffects = BigWorld.player().vehicle is not None
        return


class GasSoundManager(object):

    def __init__(self, settings):
        import FMOD
        import SoundGroups
        if settings is None:
            settings = _getSoundSettings()['soundSettings']
        if FMOD.enabled:
            alarmSnd = settings['alarm'].asString
        else:
            alarmSnd = settings['wwalarm'].asString
        self.__gazAlarm = SoundGroups.g_instance.getSound2D(alarmSnd)
        return

    def __del__(self):
        self.__gazAlarm.stop()
        self.__gazAlarm = None
        return

    def playAlarm(self):
        self.__gazAlarm.play()


class GasAttackManager(CallbackDelayer):
    _ALLOWED_ACTIVITIES_LAG = 2.0
    state = property(lambda self: self.__state)
    settings = property(lambda self: self.__gasAttackSettings)
    startTime = property(lambda self: self.__startTime)

    def __getCloudRadius(self):
        if self.__cloud is None:
            return 0.0
        else:
            cloudMatrix = Math.Matrix(self.__cloud.cloudControl.cloudMatrixProvider)
            return cloudMatrix.applyVector(Vector3(1, 0, 0)).x

    cloudRadius = property(__getCloudRadius)

    def __getCloudPosition(self):
        if self.__gasAttackSettings is None:
            return Vector3(0, 0, 0)
        else:
            return self.__gasAttackSettings.position

    cloudPosition = property(__getCloudPosition)

    def __init__(self, mapSettings = None):
        if mapSettings is None:
            mapSettings = _getDefaultMapSettings()
        CallbackDelayer.__init__(self)
        self.__mapSettings = mapSettings
        self.__gasAttackSettings = None
        self.__state = GasAttackState.NO
        self.__startTime = 0
        self.__cloud = None
        if _ENABLE_DEBUG_LOG:
            self.__windupTime = 0
        self.__evtManager = Event.EventManager()
        self.onAttackPreparing = Event.Event(self.__evtManager)
        self.onAttackStarted = Event.Event(self.__evtManager)
        self.onAttackStopped = Event.Event(self.__evtManager)
        if not mapSettings.cloudModel:
            LOG_ERROR('Empty model name for cloud model')
        else:
            BigWorld.loadResourceListBG([mapSettings.cloudModel], self.__onCloudModelLoaded)
        self.__cloudModelResource = None
        return

    def destroy(self):
        CallbackDelayer.destroy(self)
        if self.__cloud is not None:
            self.__cloud.destroy()
        self.__evtManager.clear()
        self.__state = GasAttackState.DONE
        return

    def launchScenario(self, startTime = None, gasAttackSettings = None):
        if self.__gasAttackSettings is not None:
            LOG_DEBUG('Already started gas attack  at %f with settings %s' % (self.__startTime, self.__gasAttackSettings))
            return
        else:
            if gasAttackSettings is None:
                startTime, gasAttackSettings = _getDefaultScenario()
            self.__startTime = startTime
            if _ENABLE_DEBUG_LOG:
                self.__windupTime = BigWorld.serverTime()
                LOG_DEBUG('===Gas attack launch order received at %f===\n%s\n======' % (self.__windupTime, gasAttackSettings))
            self.stopCallback(self.__startPreparation)
            self.stopCallback(self.__startAttack)
            self.__gasAttackSettings = gasAttackSettings
            self.__state = GasAttackState.NO
            curTime = BigWorld.serverTime()
            if curTime < self.__startTime:
                self.delayCallback(self.__startTime - curTime, self.__startPreparation)
            else:
                self.__startPreparation(True)
            self.__soundMgr = GasSoundManager(self.__mapSettings.soundSettings)
            self.__soundMgr.playAlarm()
            return

    def __startPreparation(self, alreadyStarted = False):
        g_ctfManager.hideAll()
        self.__state = GasAttackState.PREPARE
        attackTime = self.__startTime + self.__gasAttackSettings.preparationPeriod
        curTime = BigWorld.serverTime()
        timeDelta = attackTime - curTime
        if timeDelta <= 0.001:
            self.__startAttack(alreadyStarted)
        else:
            self.delayCallback(timeDelta, self.__startAttack)
        if alreadyStarted and curTime - self.__startTime > GasAttackManager._ALLOWED_ACTIVITIES_LAG:
            return
        if _ENABLE_DEBUG_LOG:
            LOG_DEBUG('===Gas attack preparation started at %f, windup delay %f===' % (BigWorld.serverTime(), BigWorld.serverTime() - self.__windupTime))
            self.__windupTime = BigWorld.serverTime()
        for mapActivity in self.__mapSettings.mapActivities:
            MapActivities.startActivity(mapActivity)

        self.onAttackPreparing()

    def __startAttack(self, alreadyStarted = False):
        curTime = BigWorld.serverTime()
        endTime = self.__startTime + self.__gasAttackSettings.preparationPeriod + self.__gasAttackSettings.compressionTime
        self.delayCallback(endTime - curTime, self.__stopAttack)
        if _ENABLE_DEBUG_LOG:
            LOG_DEBUG('===Gas attack LAUNCHED! At %f, windup delay %f===' % (BigWorld.serverTime(), BigWorld.serverTime() - self.__windupTime))
            self.__windupTime = BigWorld.serverTime()
        self.__state = GasAttackState.ATTACK
        if not alreadyStarted:
            pass
        self.__cloud = GasCloud(self.__mapSettings, self.__startTime + self.__gasAttackSettings.preparationPeriod, self.__gasAttackSettings, self.__cloudModelResource)
        self.onAttackStarted()

    def __stopAttack(self):
        if _ENABLE_DEBUG_LOG:
            LOG_DEBUG('==GAS ATTACK ENDED AT %f, windup delay %f===' % (BigWorld.serverTime(), BigWorld.serverTime() - self.__windupTime))
        self.__state = GasAttackState.DONE
        self.onAttackStopped()

    def __onCloudModelLoaded(self, resources):
        if self.__state == GasAttackState.DONE:
            return
        else:
            values = resources.values()
            if not values:
                LOG_ERROR('No cloud model found during loading!')
            self.__cloudModelResource = values[0]
            if self.__cloud is not None:
                self.__cloud.model = self.__cloudModelResource
            return

    def soundManager(self):
        return self.__soundMgr


_g_instance = None

def gasAttackManager():
    global _g_instance
    return _g_instance


def initAttackManager(arena):
    global _g_instance
    if caps.get(arena.bonusType) & caps.GAS_ATTACK_MECHANICS > 0 and arena.arenaType.gameplayName in ('fallout', 'fallout2', 'fallout3'):
        visual = getattr(arena.arenaType, 'gasAttackVisual', None)
        assert visual is not None, 'Gas attack visual should be defined for arena bonus type: %d' % arena.bonusType
        _g_instance = GasAttackManager(visual)
    return


def finiAttackManager():
    global _g_instance
    if _g_instance is not None:
        _g_instance.destroy()
    _g_instance = None
    return
