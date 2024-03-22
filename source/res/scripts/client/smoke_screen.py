# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/smoke_screen.py
import logging
from helpers.EffectsList import effectsFromSection
from items import vehicles
import BigWorld
import ResMgr
import Math
from Flock import DebugGizmo
ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_SHOW_DEBUG_SMOKE = False
_DEFAULT_SMOKE_INTENSITY = 0.08
_DEFAULT_SMOKE_COLOR = Math.Vector3(200, 200, 200)
_logger = logging.getLogger(__name__)

class _SmokeDebugVisualization(object):

    def __init__(self, position, equipmentID, endTime):
        smokeScreenEquipment = vehicles.g_cache.equipments()[equipmentID]
        self._startRadius = smokeScreenEquipment.startRadius
        self._startHeight = smokeScreenEquipment.startHeight
        self._expansionDuration = smokeScreenEquipment.expansionDuration
        self._expandedRadius = smokeScreenEquipment.expandedRadius
        self._expandedHeight = smokeScreenEquipment.expandedHeight
        self._heightUpFraction = smokeScreenEquipment.heightUpFraction
        self._totalDuration = smokeScreenEquipment.totalDuration
        self.__position = position
        self.__callbackID = None
        self.__endTime = endTime
        self.__debugGizmo = DebugGizmo('objects/misc/bbox/cylinder1_proxy.model')
        self.__startTime = BigWorld.serverTime()
        self.__currentMatrix = Math.Matrix()
        self.__onUpdate()
        return

    def stop(self):
        self.__debugGizmo = None
        return

    def __onUpdate(self):
        if not self.__debugGizmo:
            return
        curTime = BigWorld.serverTime()
        deltaTime = curTime - self.__startTime
        if deltaTime > self._totalDuration:
            return
        expansionRate = (self._expandedRadius - self._startRadius) / self._expansionDuration
        heightExpansionRate = (self._expandedHeight - self._startHeight) / self._expansionDuration
        radius = min(self._startRadius + deltaTime * expansionRate, self._expandedRadius)
        height = min(self._startHeight + deltaTime * heightExpansionRate, self._expandedHeight)
        self.__currentMatrix = self.__mkMatrix(radius, height)
        self.__debugGizmo.setMatrix(self.__currentMatrix)
        if radius <= self._expandedRadius:
            BigWorld.callback(1, self.__onUpdate)

    def __mkMatrix(self, radius, height):
        matrix = Math.Matrix()
        matrix.setRotateYPR((0, 0, 0))
        matrix.translation = self.__position + Math.Vector3(0, -height * (1 - self._heightUpFraction), 0)
        scaleMatrix = Math.Matrix()
        scaleMatrix.setScale((radius, height, radius))
        matrix.preMultiply(scaleMatrix)
        return matrix


class SmokeScreen(object):
    vignetteEnabled = False
    activeVignetteEquipmentID = -1
    renderSettings = BigWorld.WGRenderSettings()

    def __init__(self, smokeId, args):
        self.__args = args
        self.__effectID = -1
        self.__smokeID = smokeId
        self.__debugGizmo = None
        self.__loadSmokeScreen(args[0], args[1], args[4])
        if _SHOW_DEBUG_SMOKE:
            self.__debugGizmo = _SmokeDebugVisualization(args[1], args[0], args[3])
        return

    def stop(self):
        self.__stopSmokeScreen()
        if _SHOW_DEBUG_SMOKE and self.__debugGizmo:
            self.__debugGizmo.stop()
            self.__debugGizmo = None
        return

    def __loadSmokeScreen(self, equipmentID, position, team):
        smokeScreenEquipment = vehicles.g_cache.equipments()[equipmentID]
        player = BigWorld.player()
        if player.isSimulationSceneActive:
            return
        else:
            if team is player.followTeamID:
                effectName = smokeScreenEquipment.smokeEffectNameAlly
            else:
                effectName = smokeScreenEquipment.smokeEffectNameEnemy
            settingsData = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE + '/' + effectName)
            if settingsData is None:
                return
            smokeEffect = effectsFromSection(settingsData)
            player = BigWorld.player()
            if player is None:
                return
            self.__effectID = player.terrainEffects.addNew(position, smokeEffect.effectsList, smokeEffect.keyPoints, None)
            return

    def __stopSmokeScreen(self):
        player = BigWorld.player()
        if player is not None and self.__effectID >= 0:
            player.terrainEffects.stop(self.__effectID)
        return

    @staticmethod
    def enableSmokePostEffect(enabled, smokeInfos=None):
        if enabled:
            if smokeInfos:
                equipmentID = smokeInfos['equipmentID']
                if SmokeScreen.vignetteEnabled and SmokeScreen.activeVignetteEquipmentID == equipmentID:
                    return
                smokeScreenEquipment = vehicles.g_cache.equipments()[equipmentID]
                vignetteColor = smokeScreenEquipment.vignetteColor
                vignetteParams = Math.Vector4(vignetteColor.x, vignetteColor.y, vignetteColor.z, smokeScreenEquipment.vignetteIntensity)
            else:
                _logger.warning('No smoke infos set for smoke posteffect, using default values.')
                vignetteParams = Math.Vector4(_DEFAULT_SMOKE_COLOR.x, _DEFAULT_SMOKE_COLOR.y, _DEFAULT_SMOKE_COLOR.z, _DEFAULT_SMOKE_INTENSITY)
            if SmokeScreen.activeVignetteEquipmentID == -1:
                SmokeScreen.defaultVignetteParams = SmokeScreen.renderSettings.getVignetteSettings()
            SmokeScreen.renderSettings.setVignetteSettings(vignetteParams)
            SmokeScreen.activeVignetteEquipmentID = equipmentID
        else:
            if not SmokeScreen.vignetteEnabled:
                return
            SmokeScreen.renderSettings.setVignetteSettings(SmokeScreen.defaultVignetteParams)
            SmokeScreen.activeVignetteEquipmentID = -1
        SmokeScreen.vignetteEnabled = enabled
