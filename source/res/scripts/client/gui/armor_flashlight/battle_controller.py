# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/armor_flashlight/battle_controller.py
import logging
import typing
import BigWorld
import CGF
import armor_flashlight
from AvatarInputHandler import aih_global_binding, AvatarInputHandler
from AvatarInputHandler.aih_global_binding import BINDING_ID
from AvatarInputHandler.gun_marker_ctrl import computePiercingPowerAtDist
from Math import Vector3
from Vehicle import Vehicle
from account_helpers.settings_core.settings_constants import ArmorFlashlight, GRAPHICS, POST_PROCESSING_QUALITY
from aih_constants import CTRL_MODE_NAME, GUN_MARKER_FLAG, GUN_MARKER_TYPE
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import SHELL_TYPES, SHELL_TYPES_INDICES
from gui.armor_flashlight.config import getConfig, isFeatureEnabled
from gui.armor_flashlight.interfaces import IArmorFlashlightBattleController
from gui.armor_flashlight.utils import getAllMatInfos
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, CROSSHAIR_VIEW_ID
from helpers import dependency, isPlayerAvatar
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from ProjectileMover import EntityCollisionData
    from items.vehicles import VehicleDescriptor
    from aih_constants import GunMarkerState
_logger = logging.getLogger(__name__)
GUN_PIERCING = 'gunPiercing'
SETTINGS_TRIGGER_CHANGES = (ArmorFlashlight.ENABLED,
 ArmorFlashlight.FILL,
 ArmorFlashlight.OPACITY,
 ArmorFlashlight.COLOR_SCHEMA,
 GRAPHICS.COLOR_BLIND,
 ArmorFlashlight.RESOLUTION,
 POST_PROCESSING_QUALITY)
VALID_CTRL_MODES = (CTRL_MODE_NAME.SNIPER, CTRL_MODE_NAME.TWIN_GUN, CTRL_MODE_NAME.DUAL_GUN)

def _inputIsBad(handler):
    return handler is None or not isinstance(handler, AvatarInputHandler) or handler.ctrlModeName not in VALID_CTRL_MODES


def _collisionIsBad(collision, myTeam):
    return collision is None or collision.entity is None or not isinstance(collision.entity, Vehicle) or collision.entity.health <= 0 or collision.entity.publicInfo['team'] == myTeam


class ArmorFlashlightBattleController(IArenaLoadController, IArmorFlashlightBattleController):
    __slots__ = ('_myTeam', '_cachedVehicleData', '_targetTankID', '_isVisible', '_armorFlashlightSingleton')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    gunMarkersFlags = aih_global_binding.bindRO(BINDING_ID.GUN_MARKERS_FLAGS)
    clientMarkerDataProvider = aih_global_binding.bindRO(BINDING_ID.CLIENT_GUN_MARKER_DATA_PROVIDER)
    serverMarkerDataProvider = aih_global_binding.bindRO(BINDING_ID.SERVER_GUN_MARKER_DATA_PROVIDER)
    zoomFactor = aih_global_binding.bindRO(BINDING_ID.ZOOM_FACTOR)

    def __init__(self):
        super(ArmorFlashlightBattleController, self).__init__()
        self._myTeam = None
        self._cachedVehicleData = dict()
        self._targetTankID = None
        self._isVisible = False
        self._armorFlashlightSingleton = None
        return

    def stopControl(self):
        if self._armorFlashlightSingleton is not None:
            self._stopFlashlight()
            self._armorFlashlightSingleton = None
        self._unsubscribeFromBattleSessionEvents()
        self.sessionProvider.onBattleSessionStart -= self._subscribeToBattleSessionEvents
        self.sessionProvider.onBattleSessionStop -= self._unsubscribeFromBattleSessionEvents
        self.settingsCore.onSettingsChanged -= self._onSettingsChanged
        BigWorld.player().arena.onVehicleKilled -= self._onArenaVehicleKilled
        return

    def spaceLoadCompleted(self):
        if not isFeatureEnabled():
            return
        elif not BigWorld.player().hasBonusCap(ARENA_BONUS_TYPE_CAPS.AFL_ENABLED):
            return
        else:
            self._isVisible = self.settingsCore.getSetting(ArmorFlashlight.ENABLED)
            self.sessionProvider.onBattleSessionStop += self._unsubscribeFromBattleSessionEvents
            if not self._subscribeToBattleSessionEvents():
                self.sessionProvider.onBattleSessionStart += self._subscribeToBattleSessionEvents
            self.settingsCore.onSettingsChanged += self._onSettingsChanged
            BigWorld.player().arena.onVehicleKilled += self._onArenaVehicleKilled
            self._armorFlashlightSingleton = CGF.findSingleton(avatar_getter.getSpaceID(), armor_flashlight.ArmorFlashlightSingleton)
            if self._armorFlashlightSingleton is not None:
                self._armorFlashlightSingleton.setVisible(self._isVisible)
            self._myTeam = avatar_getter.getPlayerTeam()
            self._setSettings()
            return

    def getControllerID(self):
        return BATTLE_CTRL_ID.ARMOR_FLASHLIGHT

    def toggle(self):
        if self._armorFlashlightSingleton is None:
            return False
        self._isVisible = not self._isVisible
        self._armorFlashlightSingleton.setVisible(self._isVisible)
        if self._targetTankID is not None:
            self._resolveTargetTank(True)
            return True
        else:
            return False

    def _subscribeToBattleSessionEvents(self, *_, **__):
        crosshair = self.sessionProvider.shared.crosshair
        if crosshair is not None:
            _logger.debug('Subscribed to crosshair events.')
            crosshair.onCrosshairViewChanged += self._onCrosshairViewChanged
            return True
        else:
            return False

    def _unsubscribeFromBattleSessionEvents(self, *_, **__):
        crosshair = self.sessionProvider.shared.crosshair
        if crosshair is not None:
            _logger.debug('Unsubscribed from crosshair events.')
            crosshair.onCrosshairViewChanged -= self._onCrosshairViewChanged
            crosshair.onGunMarkerStateChanged -= self._updateVisibilityState
        return

    def _onCrosshairViewChanged(self, viewID):
        self._hide()
        crosshair = self.sessionProvider.shared.crosshair
        if crosshair is None:
            _logger.error('Crosshair controller is missing.')
            return
        else:
            if viewID == CROSSHAIR_VIEW_ID.SNIPER:
                _logger.debug('Subscribed to crosshair onGunMarkerStateChanged event.')
                crosshair.onGunMarkerStateChanged += self._updateVisibilityState
            else:
                _logger.debug('Unsubscribed from crosshair onGunMarkerStateChanged event.')
                crosshair.onGunMarkerStateChanged -= self._updateVisibilityState
            return

    def _updateVisibilityState(self, markerType, gunMarkerState, *_, **__):
        if self._armorFlashlightSingleton is None:
            return
        elif markerType == GUN_MARKER_TYPE.CLIENT and not self.gunMarkersFlags & GUN_MARKER_FLAG.CLIENT_MODE_ENABLED:
            return
        elif self._myTeam is None or not isPlayerAvatar():
            self._stopFlashlight()
            return
        else:
            player = BigWorld.player()
            collision = gunMarkerState.collData
            if _inputIsBad(player.inputHandler) or _collisionIsBad(collision, self._myTeam):
                self._stopFlashlight()
                return
            elif not self._isVisible:
                return
            self._startFlashlight(collision.entity)
            self._setShootingParams(gunMarkerState.position, gunMarkerState.direction, gunMarkerState.size)
            return

    def _hide(self):
        if self._armorFlashlightSingleton is None:
            return
        else:
            self._stopFlashlight()
            return

    def _setShootingParams(self, hitPoint, direction, gunAimingCircleSize):
        player = BigWorld.player()
        vDesc = player.getVehicleDescriptor()
        shell = vDesc.shot.shell
        config = getConfig()
        dispAngle = player.gunRotator.getCurShotDispersionAngles()[0]
        extraAlphaFactor = (vDesc.gun.shotDispersionAngle / dispAngle) ** config.fadeoffFactorWhenNotAimed if dispAngle > 0.0 else 1.0
        shotPos, _, _ = player.gunRotator.getShotParams(hitPoint, True)
        ppDesc = vDesc.shot.piercingPower
        maxDist = vDesc.shot.maxDistance
        distance = (hitPoint - player.getOwnVehiclePosition()).length
        vehAttrs = self.sessionProvider.shared.feedback.getVehicleAttrs()
        piercingMultiplier = vehAttrs.get(GUN_PIERCING, 1)
        fullPiercingPower = computePiercingPowerAtDist(ppDesc, distance, maxDist, piercingMultiplier)
        shieldPenetration = False
        shellTypeMaxDamage = 0
        if shell.kind == SHELL_TYPES.HOLLOW_CHARGE:
            ricochetAngleCos = shell.type.ricochetAngleCos
            normalizationAngle = 0.0
        elif shell.kind == SHELL_TYPES.HIGH_EXPLOSIVE:
            ricochetAngleCos = 0.0
            normalizationAngle = 0.0
            if shell.type.shieldPenetration is not None:
                shieldPenetration = shell.type.shieldPenetration
            if shell.type.maxDamage is not None:
                shellTypeMaxDamage = shell.type.maxDamage
        else:
            ricochetAngleCos = shell.type.ricochetAngleCos
            normalizationAngle = shell.type.normalizationAngle
        isServerMarker = self.gunMarkersFlags & GUN_MARKER_FLAG.SERVER_MODE_ENABLED
        markerProvider = self.serverMarkerDataProvider if isServerMarker else self.clientMarkerDataProvider
        self._armorFlashlightSingleton.setShotParams(shell.piercingPowerRandomization, vDesc.shot.maxDistance, shell.caliber, SHELL_TYPES_INDICES[shell.kind], ricochetAngleCos, normalizationAngle, self.zoomFactor, distance, markerProvider.positionMatrixProvider, shotPos, direction, fullPiercingPower, extraAlphaFactor, gunAimingCircleSize, shieldPenetration, shellTypeMaxDamage)
        return

    def _stopFlashlight(self):
        if self._targetTankID is not None:
            self._armorFlashlightSingleton.resetTargetTank()
            self._targetTankID = None
        return

    def _startFlashlight(self, vehicle):
        vehID = vehicle.id
        typeDescriptor = vehicle.typeDescriptor
        if vehID not in self._cachedVehicleData or self._cachedVehicleData[vehID] != typeDescriptor.type.compactDescr:
            self._cachedVehicleData[vehID] = typeDescriptor.type.compactDescr
            self._armorFlashlightSingleton.setTankData(vehID, getAllMatInfos(typeDescriptor), vehicle.appearance.collisions, vehicle.entityGameObject)
        appearing = self._targetTankID != vehID
        if appearing:
            self._targetTankID = vehID
        self._resolveTargetTank(appearing)

    def _resolveTargetTank(self, appearing):
        if self._targetTankID is not None and self._isVisible:
            vehicle = BigWorld.entities.get(self._targetTankID)
            if vehicle:
                self._armorFlashlightSingleton.setTargetTank(self._targetTankID, vehicle.appearance.compoundModel, vehicle.entityGameObject, appearing)
        else:
            self._armorFlashlightSingleton.resetTargetTank()
        return

    def _onSettingsChanged(self, diff):
        if any((item in diff for item in SETTINGS_TRIGGER_CHANGES)):
            self._setSettings()

    def _setSettings(self):
        config = getConfig()
        colorSchemaSetting = self.settingsCore.getSetting(ArmorFlashlight.COLOR_SCHEMA)
        isColorBlind = self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND)
        opacitySetting = self.settingsCore.getSetting(ArmorFlashlight.OPACITY)
        patternSetting = self.settingsCore.getSetting(ArmorFlashlight.FILL)
        resolutionSetting = self.settingsCore.getSetting(ArmorFlashlight.RESOLUTION)
        self._armorFlashlightSingleton.setSettings(opacitySetting, config.getSchemaColorFloatsByIndex(colorSchemaSetting, isColorBlind), config.getPatternByIndex(patternSetting), config.textureTilingFactor, config.getDistanceConfigTupleList(config.alphaByDist), config.getDistanceConfigTupleList(config.radiusByDist), config.getDistanceConfigTupleList(config.appearanceDurationByDist), config.noiseIntensityMultiplier, config.getResolutionDownscaleByIndex(resolutionSetting), config.maxSizePercentOfWindow, config.borderSmoothness, config.aimingCircleAdjustment, config.smoothnessInAimingCircleAdjustment)

    def _onArenaVehicleKilled(self, targetID, attackerID, equipmentID, reason, numVehiclesAffected):
        if targetID == self._targetTankID:
            self._stopFlashlight()
