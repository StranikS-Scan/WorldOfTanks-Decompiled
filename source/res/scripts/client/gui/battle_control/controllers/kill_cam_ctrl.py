# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/kill_cam_ctrl.py
from collections import namedtuple
from enum import Enum
import Event
import Math
import logging
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared.events import DeathCamEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
DistanceMarkerData = namedtuple('DistanceMarkerData', 'projectile phaseDuration impactPoint isAttackerSpotted')
GunMarkerData = namedtuple('GunMarkerData', 'projectile phaseDuration simulatedKillerGunInfo projectileOrigin')
ImpactMarkerData = namedtuple('ImpactMarkerData', 'projectile phaseDuration impactType victimIsNotSpotted relativeArmor causeOfDeath')

class KillCamInfoMarkerType(Enum):
    GUN = 'gunMarker'
    DISTANCE = 'distanceMarker'
    IMPACT = 'gunImpact'
    HIDDEN = 'hidden'


class KillCameraController(IBattleController):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__isKillCamActive = False
        self.__gunMarkerData = None
        self.__distanceMarkerData = None
        self.__impactMarkerData = None
        self.__totalSceneDuration = 0.0
        self.killCtrlState = None
        self.__eManager = Event.EventManager()
        self.onKillCamModeStateChanged = Event.Event(self.__eManager)
        self.onMarkerDisplayChanged = Event.Event(self.__eManager)
        self.onKillCamInterrupted = Event.Event(self.__eManager)
        self.onKillCamModeEffectsPlaced = Event.Event(self.__eManager)
        self.onSimulationSceneActive = Event.Event(self.__eManager)
        self.onRespawnRequested = Event.Event(self.__eManager)
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.KILL_CAM_CTRL

    def stopControl(self):
        pass

    def startControl(self, *args):
        pass

    def killCamModeActive(self, unspottedOrigin, simulatedKillerGunInfo, projectile, phaseDurations, hasSpottedData, hasAttackerVehicle, playerRelativeArmor, playerIsSpotted, totalSceneDuration, causeOfDeath):
        phase1Duration, phase2Duration, phase3Duration = phaseDurations
        self.__distanceMarkerData = self.__buildDistanceMarkerData(projectile=projectile, phaseDuration=phase2Duration, hasSpottedData=hasSpottedData)
        self.__impactMarkerData = self.__buildImpactMarkerData(projectile=projectile, phaseDuration=phase3Duration, playerRelativeArmor=playerRelativeArmor, playerIsSpotted=playerIsSpotted, causeOfDeath=causeOfDeath)
        self.__gunMarkerData = self.__buildGunMarkerData(projectile=projectile, phaseDuration=phase1Duration, simulatedKillerGunInfo=simulatedKillerGunInfo, hasSpottedData=hasSpottedData, hasAttackerVehicle=hasAttackerVehicle, unspottedOrigin=unspottedOrigin)
        self.__totalSceneDuration = round(totalSceneDuration, 1)
        self.__isKillCamActive = True

    def killCamModeEffectsPlaced(self, isSpotted=False):
        self.onKillCamModeEffectsPlaced(isSpotted)

    def killCamInterrupted(self):
        self.onKillCamInterrupted()

    def respawnRequested(self):
        self.onRespawnRequested()

    def simulationSceneActive(self, active=True):
        self.onSimulationSceneActive(active)

    def changeKillCamModeState(self, state):
        if state is DeathCamEvent.State.FINISHED:
            self.__isKillCamActive = False
            self.__gunMarkerData = None
            self.__distanceMarkerData = None
            self.__impactMarkerData = None
        self.killCtrlState = state
        self.onKillCamModeStateChanged(state, self.__totalSceneDuration)
        return

    def changeCameraState(self, state, ctx):
        if not self.__isKillCamActive:
            _logger.error('KillCam controller is not active.')
            return
        else:
            additionalCtxInfo = {}
            markerType = None
            if state is DeathCamEvent.EventType.ROTATING_KILLER:
                markerType, additionalCtxInfo = self.__gunMarkerData
            elif state is DeathCamEvent.EventType.UNSPOTTED_PHASE_ONE:
                markerType, additionalCtxInfo = self.__gunMarkerData
            elif state is DeathCamEvent.EventType.LAST_ROTATION:
                markerType, additionalCtxInfo = self.__impactMarkerData
            elif state is DeathCamEvent.EventType.UNSPOTTED_PHASE_TWO:
                markerType, additionalCtxInfo = self.__distanceMarkerData
            elif state is DeathCamEvent.EventType.MOVING_TO_PLAYER:
                markerType, additionalCtxInfo = self.__distanceMarkerData
            elif state is DeathCamEvent.EventType.TRANSITIONING:
                markerType = KillCamInfoMarkerType.HIDDEN
            ctx.update({'markerData': additionalCtxInfo})
            self.onMarkerDisplayChanged(markerType, ctx)
            return

    def __buildImpactMarkerData(self, projectile, phaseDuration, playerRelativeArmor, playerIsSpotted, causeOfDeath):
        markerData = ImpactMarkerData(projectile=projectile, phaseDuration=phaseDuration * 1000, impactType=projectile['impactType'], victimIsNotSpotted=playerIsSpotted, relativeArmor=playerRelativeArmor, causeOfDeath=causeOfDeath)
        return (KillCamInfoMarkerType.IMPACT, markerData)

    def __buildGunMarkerData(self, projectile, phaseDuration, simulatedKillerGunInfo, hasSpottedData, hasAttackerVehicle, unspottedOrigin):
        phaseDuration *= 1000
        useProjectileOrigin = hasAttackerVehicle and hasSpottedData
        markerData = GunMarkerData(projectile=projectile, phaseDuration=phaseDuration, simulatedKillerGunInfo=simulatedKillerGunInfo if hasSpottedData else None, projectileOrigin=projectile['trajectoryData'][0][0] if useProjectileOrigin else unspottedOrigin)
        return (KillCamInfoMarkerType.GUN, markerData)

    def __buildDistanceMarkerData(self, projectile, phaseDuration, hasSpottedData):
        markerData = DistanceMarkerData(projectile=projectile, phaseDuration=phaseDuration * 1000, impactPoint=projectile['impactPoint'], isAttackerSpotted=hasSpottedData)
        return (KillCamInfoMarkerType.DISTANCE, markerData)
