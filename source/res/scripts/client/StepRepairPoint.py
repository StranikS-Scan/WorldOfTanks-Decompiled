# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StepRepairPoint.py
import BigWorld
import AnimationSequence
from Math import Vector2
from Math import Matrix
import ResMgr
import SoundGroups
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS

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
        self.__animator = None
        return

    @property
    def __isEnabled(self):
        return ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arena.bonusType, ARENA_BONUS_TYPE_CAPS.STEP_REPAIR_MECHANIC)

    def prerequisites(self):
        stepRepairPointComponent = getattr(BigWorld.player().arena.componentSystem, 'stepRepairPointComponent', None)
        rv = []
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.addStepRepairPoint(self)
        if self.__isEnabled:
            assembler = BigWorld.CompoundAssembler(_g_stepRepairPointSettings.flagModel, self.spaceID)
            assembler.addRootPart(_g_stepRepairPointSettings.flagModel, 'root')
            rv = [assembler, _g_stepRepairPointSettings.radiusModel]
            if _g_stepRepairPointSettings.flagAnim is not None:
                loader = AnimationSequence.Loader(_g_stepRepairPointSettings.flagAnim, self.spaceID)
                rv.append(loader)
            mProv = Matrix()
            mProv.translation = self.position
            self.__stepRepairPointSoundObject = SoundGroups.g_instance.WWgetSoundObject('stepRepairPoint_' + str(self), mProv)
            self.__stepRepairPointSoundObject.play(_g_stepRepairPointSettings.attachedSoundEventName)
        return rv

    def onEnterWorld(self, prereqs):
        if not prereqs:
            return
        else:
            self.model = prereqs[_g_stepRepairPointSettings.flagModel]
            self.model.position = self.position
            if _g_stepRepairPointSettings.flagAnim is not None:
                self.__animator = prereqs[_g_stepRepairPointSettings.flagAnim]
                self.__animator.bindTo(AnimationSequence.CompoundWrapperContainer(self.model))
                self.__animator.start()
            self.__terrainSelectedArea = BigWorld.PyTerrainSelectedArea()
            self.__terrainSelectedArea.setup(_g_stepRepairPointSettings.radiusModel, Vector2(self.radius * 2.0, self.radius * 2.0), self._OVER_TERRAIN_HEIGHT, self._COLOR)
            self.model.root.attach(self.__terrainSelectedArea)
            return

    def onLeaveWorld(self):
        stepRepairPointComponent = getattr(BigWorld.player().arena.componentSystem, 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.removeStepRepairPoint(self)
        if self.__stepRepairPointSoundObject is not None:
            self.__stepRepairPointSoundObject.stopAll()
            self.__stepRepairPointSoundObject = None
        self.__animator = None
        return

    def isActiveForPlayerTeam(self):
        return self.team == 0 or self.team == BigWorld.player().team

    def set_team(self, oldValue):
        stepRepairPointComponent = getattr(BigWorld.player().arena.componentSystem, 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.stepRepairPointActiveStateChanged(self)
        return
