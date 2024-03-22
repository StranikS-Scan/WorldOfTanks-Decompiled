# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/death_cam/marker_view.py
import logging
import math
from typing import Optional
import GUI
import BigWorld
from constants import IMPACT_TYPES
import Math
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.battle_control.controllers.kill_cam_ctrl import KillCamInfoMarkerType, ImpactMarkerData, GunMarkerData, DistanceMarkerData
from gui.impl.gen.view_models.views.battle.death_cam.marker_view_model import MarkerViewModel, ShellType, Phase, DeathReason, ImpactMode, CaliberRule
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.events import DeathCamEvent
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

def hasShellPenetrationDistanceLoss(shellType):
    return shellType == ShellType.ARMORPIERCING or shellType == ShellType.ARMORPIERCINGPREMIUM or shellType == ShellType.ARMORPIERCINGCR or shellType == ShellType.ARMORPIERCINGCRPREMIUM


class DeathCamMarkerView(SubModelPresenter, IGlobalListener):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HIDE_MARKERS_DURING_PAUSE = False
    shellIconMap = {'ARMOR_PIERCING': ShellType.ARMORPIERCING,
     'ARMOR_PIERCING_CR': ShellType.ARMORPIERCINGCR,
     'ARMOR_PIERCING_CR_GOLD': ShellType.ARMORPIERCINGCRPREMIUM,
     'ARMOR_PIERCING_GOLD': ShellType.ARMORPIERCINGPREMIUM,
     'HIGH_EXPLOSIVE': ShellType.HIGHEXPLOSIVE,
     'HIGH_EXPLOSIVE_MODERN': ShellType.HIGHEXPLOSIVEMODERN,
     'HIGH_EXPLOSIVE_MODERN_GOLD': ShellType.HIGHEXPLOSIVEMODERNPREMIUM,
     'HIGH_EXPLOSIVE_GOLD': ShellType.HIGHEXPLOSIVEPREMIUM,
     'HIGH_EXPLOSIVE_LEGACY_NO_STUN': ShellType.HIGHEXPLOSIVESPG,
     'HIGH_EXPLOSIVE_LEGACY_STUN': ShellType.HIGHEXPLOSIVESPGSTUN,
     'HOLLOW_CHARGE': ShellType.HOLLOWCHARGE,
     'HOLLOW_CHARGE_GOLD': ShellType.HOLLOWCHARGEPREMIUM}
    __DEATH_REASONS = {'hp': DeathReason.HP,
     'crew': DeathReason.CREW,
     'ignition': DeathReason.IGNITION,
     'detonation': DeathReason.DETONATION}
    __IMPACT_MODES = {IMPACT_TYPES.PENETRATION: ImpactMode.PENETRATION,
     IMPACT_TYPES.LEGACY_HE: ImpactMode.LEGACYHE,
     IMPACT_TYPES.MODERN_HE: ImpactMode.MODERNHE}

    def __init__(self, viewModel, parentView):
        super(DeathCamMarkerView, self).__init__(viewModel, parentView)
        self.__gunPosConfig = 0.5
        self.__markerMatrix = None
        self.__callbackDelayer = CallbackDelayer()
        self.__positionController = GUI.WGMarkerPositionController()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self):
        super(DeathCamMarkerView, self).initialize()
        self.__addListeners()
        self.__initializeModel()

    def finalize(self):
        self.__removeListeners()
        super(DeathCamMarkerView, self).finalize()

    def __addListeners(self):
        if self.__guiSessionProvider.shared.killCamCtrl:
            self.__guiSessionProvider.shared.killCamCtrl.onKillCamModeStateChanged += self.__onKillCamStateChanged
            self.__guiSessionProvider.shared.killCamCtrl.onMarkerDisplayChanged += self.__onMarkerDisplayChanged

    def __removeListeners(self):
        if self.__guiSessionProvider.shared.killCamCtrl:
            self.__guiSessionProvider.shared.killCamCtrl.onKillCamModeStateChanged -= self.__onKillCamStateChanged
            self.__guiSessionProvider.shared.killCamCtrl.onMarkerDisplayChanged -= self.__onMarkerDisplayChanged

    def __onKillCamStateChanged(self, killCamState, _):
        if killCamState is DeathCamEvent.State.PREPARING:
            self.viewModel.setIsSimplified(self.__isSimplifiedView())
        elif killCamState is DeathCamEvent.State.PAUSE:
            self.viewModel.setIsAdvanced(True)
        elif killCamState is DeathCamEvent.State.RESUME:
            self.viewModel.setIsAdvanced(False)
        elif killCamState in [DeathCamEvent.State.ENDING, DeathCamEvent.State.FINISHED]:
            self.viewModel.setIsMarkerVisible(False)
            self.viewModel.setIsAdvanced(False)

    def __onMarkerDisplayChanged(self, markerType, ctx):
        if markerType is KillCamInfoMarkerType.HIDDEN:
            self.viewModel.setIsMarkerVisible(False)
        if markerType is KillCamInfoMarkerType.IMPACT:
            markerData = ctx['markerData']
            self.__showImpactMarker(markerData)
        if markerType is KillCamInfoMarkerType.GUN:
            markerData = ctx['markerData']
            if not self.__isSimplifiedView():
                self.__showGunMarker(markerData)
        if markerType is KillCamInfoMarkerType.DISTANCE:
            markerData = ctx['markerData']
            self.__showDistanceMarker(markerData)

    def __showDistanceMarker(self, distanceMarkerData):
        self.__updateDistanceMarkerModel(distanceMarkerData)
        projectileHitPos = distanceMarkerData.impactPoint
        if projectileHitPos is None:
            return
        else:
            self.__markerMatrix = Math.createTranslationMatrix(projectileHitPos)
            self.__updateMarkerPosition()
            return

    def __showImpactMarker(self, impactMarkerData):
        phaseDuration = impactMarkerData.phaseDuration
        projectileData = impactMarkerData.projectile
        relativeArmor = impactMarkerData.relativeArmor
        causeOfDeath = impactMarkerData.causeOfDeath
        shellKind = projectileData['shellKind']
        self.__updateImpactMarkerModel(phaseDuration, projectileData, relativeArmor, shellKind, causeOfDeath)
        self.__updateMarkerPosition()

    def __showGunMarker(self, gunMarkerData):
        phaseDuration = gunMarkerData.phaseDuration
        projectileData = gunMarkerData.projectile
        shellType = self.shellIconMap[projectileData['shellType']]
        self.__updateGunMarkerModel(phaseDuration, projectileData, shellType)
        self.__markerMatrix, markerOffsetMatrix = self.__getCaliberMarkerPositions(gunMarkerData)
        if self.viewModel is not None:
            gunMatrixProvider = BigWorld.LerpPositionMatrixProvider(self.__markerMatrix, markerOffsetMatrix, self.__gunPosConfig)
            self.__positionController.add(self.viewModel.base.proxy, gunMatrixProvider)
            self.__showMarker()
        return

    def __updateGunMarkerModel(self, phaseDuration, projectileData, shellType):
        self.__updateGunMarkerParameters(projectileData, shellType)
        self.__updateViewModelSettings(Phase.KILLER, 0, phaseDuration, True)

    def __updateImpactMarkerModel(self, phaseDuration, projectileData, relativeArmor, shellKind, causeOfDeath):
        self.__updateImpactMarkerParameters(projectileData, relativeArmor, shellKind, causeOfDeath)
        self.__updateViewModelSettings(Phase.IMPACT, 0, phaseDuration, True)

    def __updateDistanceMarkerModel(self, distanceMarkerData):
        phaseDuration = distanceMarkerData.phaseDuration
        projectileData = distanceMarkerData.projectile
        shellType = self.shellIconMap[projectileData['shellType']]
        isAttackerSpotted = distanceMarkerData.isAttackerSpotted
        self.__updateDistanceMarkerParameters(projectileData, shellType, isAttackerSpotted)
        self.__updateViewModelSettings(Phase.TRAJECTORY, 0, phaseDuration, True)

    def __updateGunMarkerParameters(self, projectileData, shellType):
        self.viewModel.setShellType(shellType)
        self.viewModel.setShellIcon(projectileData['shellIcon'])
        self.viewModel.setShellCaliber(projectileData['shellCaliber'])
        self.viewModel.setShellDamageBasic(projectileData['averageDamageOfShell'])
        velocity = projectileData['velocity']
        self.viewModel.setShellVelocityBasic(velocity.length)
        caliberRule = CaliberRule.NONE
        if projectileData['is3CaliberRuleActive']:
            caliberRule = CaliberRule.THREECALIBER
        elif projectileData['is2CaliberRuleActive']:
            caliberRule = CaliberRule.TWOCALIBER
        self.viewModel.setCaliberRule(caliberRule)

    def __updateDistanceMarkerParameters(self, projectileData, shellType, isAttackerSpotted):
        impactType = self.__IMPACT_MODES[projectileData['impactType']]
        self.viewModel.setImpactMode(impactType)
        if self.__isSimplifiedView():
            self.viewModel.setShellType(shellType)
            self.viewModel.setShellIcon(projectileData['shellIcon'])
        if isAttackerSpotted and 'distanceOfShot' in projectileData:
            self.viewModel.setIsKillerUnspotted(False)
            self.viewModel.setShootDistance(projectileData['distanceOfShot'])
        else:
            self.viewModel.setIsKillerUnspotted(True)
        self.viewModel.setShellPenetrationBasic(projectileData['nominalPiercingPower'])
        effectivePenetration = int(projectileData['piercingPower'])
        self.viewModel.setShellPenetrationEffective(effectivePenetration)

    def __updateImpactMarkerParameters(self, projectileData, relativeArmor, shellKind, causeOfDeath):
        impactType = self.__IMPACT_MODES[projectileData['impactType']]
        effectiveDamage = projectileData['effectiveShellDamage']
        self.viewModel.setShellDamageEffective(effectiveDamage)
        self.viewModel.setArmorNominal(projectileData['nominalArmor'])
        self.viewModel.setArmorRelative(relativeArmor)
        self.viewModel.setShellArmorAngleGain(projectileData['angleGain'])
        self.viewModel.setShellDamageRandomizationFactor(projectileData['damageRandomizationFactor'])
        self.viewModel.setHasDistanceFalloff(projectileData['hasDistanceFalloff'])
        if 'damageDistanceModifier' in projectileData:
            self.viewModel.setDamageDistanceModifier(projectileData['damageDistanceModifier'])
        hitAngleDegree = int(round(math.degrees(math.acos(projectileData['hitAngleCos']))))
        self.viewModel.setAngleImpact(hitAngleDegree)
        if projectileData['is3CaliberRuleActive']:
            ricochetAngle = maxPenetrationAngle = 90
        else:
            ricochetAngle = self.__guiSessionProvider.arenaVisitor.modifiers.getShellRicochetCos(shellKind)
            ricochetAngle = math.degrees(math.acos(ricochetAngle))
            maxPenetrationAngle = min(projectileData['maxPenetrationAngle'], ricochetAngle)
        self.viewModel.setAngleFailure(maxPenetrationAngle)
        self.viewModel.setAngleRicochet(ricochetAngle)
        nominalBurst = projectileData['shellDamageBurstHE']
        armorProtectionHE = -abs(int(round(projectileData['armorProtectionHE'])))
        spallLinerProtectionHE = -abs(int(round(projectileData['spallLinerProtectionHE'])))
        distanceLossHE = -abs(int(round(projectileData['distanceLossHE'])))
        randomization = -(nominalBurst - effectiveDamage + armorProtectionHE + spallLinerProtectionHE)
        self.viewModel.setShellDamageBurst(nominalBurst)
        self.viewModel.setShellDamageLossProtectionHe(armorProtectionHE)
        self.viewModel.setShellDamageLossProtectionSpallLiner(spallLinerProtectionHE)
        self.viewModel.setShellDamageLossDistance(distanceLossHE)
        self.viewModel.setImpactMode(impactType)
        if impactType == ImpactMode.LEGACYHE:
            randomization -= distanceLossHE
            self.viewModel.setShellDamageRandomizationFactor(randomization)
        elif impactType == ImpactMode.MODERNHE:
            self.viewModel.setShellDamageBasic(projectileData['averageDamageOfShell'] / 2)
            self.viewModel.setShellDamageRandomizationFactor(randomization)
        self.viewModel.setDeathReason(self.__DEATH_REASONS.get(causeOfDeath, DeathReason.HP))

    def __updateViewModelSettings(self, phase, phaseTimePassed, phaseDuration, isVisible):
        self.viewModel.setPhase(phase)
        self.viewModel.setPhaseTimePassed(phaseTimePassed)
        self.viewModel.setPhaseDuration(phaseDuration)
        self.viewModel.setIsMarkerVisible(isVisible)

    def __initializeModel(self):
        self.viewModel.setPhase(Phase.KILLER)
        self.viewModel.setImpactMode(ImpactMode.PENETRATION)
        self.viewModel.setShellType(ShellType.ARMORPIERCING)
        self.viewModel.setShellIcon(ShellType.ARMORPIERCING.value)
        self.viewModel.setDeathReason(DeathReason.HP)

    def __updateMarkerPosition(self):
        if self.viewModel is not None:
            self.__positionController.add(self.viewModel.base.proxy, self.__markerMatrix)
            self.__showMarker()
        return

    def __getCaliberMarkerPositions(self, markerData):
        simulatedKillerGunInfo = markerData.simulatedKillerGunInfo
        if simulatedKillerGunInfo:
            return simulatedKillerGunInfo
        caliberMarkerMatrix = Math.createTranslationMatrix(markerData.projectileOrigin)
        return (caliberMarkerMatrix, caliberMarkerMatrix)

    def __showMarker(self):
        if not self.viewModel.getIsMarkerVisible():
            self.viewModel.setIsMarkerVisible(True)

    def __hideMarker(self):
        if self.viewModel.getIsMarkerVisible():
            self.viewModel.setIsMarkerVisible(False)

    def __isSimplifiedView(self):
        avatar = BigWorld.player()
        return False if not avatar else avatar.isSimpleDeathCam()
