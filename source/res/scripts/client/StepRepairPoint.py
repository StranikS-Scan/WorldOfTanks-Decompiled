# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StepRepairPoint.py
import BigWorld
from Math import Vector2
from Math import Matrix
import ResMgr
from debug_utils import LOG_WARNING
import SoundGroups

class _StepRepairPointSettingsCache(object):

    def __init__(self, settings):
        self.initSettings(settings)

    def initSettings(self, settings):
        self.flagModel = settings.readString('flagModelName', '')
        self.radiusModel = settings.readString('radiusModel', '')
        self.flagAnim = settings.readString('flagAnim', '')
        self.attachedSoundEventName = settings.readString('wwsound', '')


ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_g_stepRepairPointSettings = None

class StepRepairPoint(BigWorld.Entity):
    _COLOR = 4294967295L
    _OVER_TERRAIN_HEIGHT = 0.5

    def __init__(self):
        global _g_stepRepairPointSettings
        if _g_stepRepairPointSettings is None:
            settingsData = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE + '/stepRepairPoint')
            _g_stepRepairPointSettings = _StepRepairPointSettingsCache(settingsData)
        self.__stepRepairPointSoundObject = None
        self.__terrainSelectedArea = None
        return

    def prerequisites(self):
        stepRepairPointComponent = BigWorld.player().arena.componentSystem.stepRepairPointComponent
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.addStepRepairPoint(self)
        rv = [_g_stepRepairPointSettings.flagModel, _g_stepRepairPointSettings.radiusModel]
        mProv = Matrix()
        mProv.translation = self.position
        self.__stepRepairPointSoundObject = SoundGroups.g_instance.WWgetSoundObject('stepRepairPoint_' + str(self), mProv)
        self.__stepRepairPointSoundObject.play(_g_stepRepairPointSettings.attachedSoundEventName)
        return rv

    def onEnterWorld(self, prereqs):
        self.model = prereqs[_g_stepRepairPointSettings.flagModel]
        self.model.position = self.position
        if _g_stepRepairPointSettings.flagAnim is not None:
            try:
                animAction = self.model.action(_g_stepRepairPointSettings.flagAnim)
                animAction()
            except Exception:
                LOG_WARNING('Unable to start "%s" animation action for model "%s"' % (_g_stepRepairPointSettings.flagAnim, _g_stepRepairPointSettings.flagModel))

        self.__terrainSelectedArea = BigWorld.PyTerrainSelectedArea()
        self.__terrainSelectedArea.setup(_g_stepRepairPointSettings.radiusModel, Vector2(self.radius * 2.0, self.radius * 2.0), self._OVER_TERRAIN_HEIGHT, self._COLOR)
        self.model.root.attach(self.__terrainSelectedArea)
        return

    def onLeaveWorld(self):
        stepRepairPointComponent = BigWorld.player().arena.componentSystem.stepRepairPointComponent
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.removeStepRepairPoint(self)
        self.__stepRepairPointSoundObject.stopAll()
        self.__stepRepairPointSoundObject = None
        return

    def isActiveForPlayerTeam(self):
        return self.team == 0 or self.team == BigWorld.player().team

    def set_team(self, oldValue):
        stepRepairPointComponent = BigWorld.player().arena.componentSystem.stepRepairPointComponent
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.stepRepairPointActiveStateChanged(self)
        return
