# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/smoke_screen.py
from helpers.EffectsList import effectsFromSection
from items import vehicles
import BigWorld
import ResMgr
import Math
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from Flock import DebugGizmo
ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_SHOW_DEBUG_SMOKE = False
_SMOKE_VIGNETTE_PARAMS = Math.Vector4(0.08, 200, 0, 0)

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
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    vignetteEnabled = False

    def __init__(self, smokeId, args):
        self.__args = args
        self.__effectID = -1
        self.__smokeID = smokeId
        self.__debugGizmo = None
        ctrl = self.guiSessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__loadSmokeScreen(args[0], args[1])
        if _SHOW_DEBUG_SMOKE:
            self.__debugGizmo = _SmokeDebugVisualization(args[1], args[0], args[3])
        return

    def stop(self):
        ctrl = self.guiSessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        self.__stopSmokeScreen()
        if _SHOW_DEBUG_SMOKE and self.__debugGizmo:
            self.__debugGizmo.stop()
            self.__debugGizmo = None
        return

    def __loadSmokeScreen(self, equipmentID, position):
        smokeScreenEquipment = vehicles.g_cache.equipments()[equipmentID]
        settingsData = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE + '/' + smokeScreenEquipment.smokeEffectName)
        if settingsData is None:
            return
        else:
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

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SMOKE:
            SmokeScreen.enableSmokePostEffect(bool(value))

    @staticmethod
    def enableSmokePostEffect(enabled):
        if enabled == SmokeScreen.vignetteEnabled:
            return
        SmokeScreen.vignetteEnabled = enabled
        if enabled:
            SmokeScreen.defaultVignetteParams = BigWorld.getVignettSettings()
            BigWorld.setVignettSettings(_SMOKE_VIGNETTE_PARAMS)
        else:
            BigWorld.setVignettSettings(SmokeScreen.defaultVignetteParams)
