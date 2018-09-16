# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SectorBase.py
import BigWorld
from Math import Vector4, Vector3, Vector2, Matrix
import ResMgr
import SoundGroups
from FlagModel import FlagSettings, FlagModel

class _SectorBaseSettingsCache(object):

    def __init__(self, settings):
        self.initSettings(settings)

    def initSettings(self, settings):
        self.flagModelName = settings.readString('flagModelName', '')
        self.flagStaffModelName = settings.readString('flagstaffModelName', '')
        self.radiusModel = settings.readString('radiusModel', '')
        self.flagAnim = settings.readString('flagAnim', '')
        self.flagStaffFlagHP = settings.readString('flagstaffFlagHP', '')
        self.baseAttachedSoundEventName = settings.readString('wwsound', '')
        self.flagBackgroundTex = settings.readString('flagBackgroundTex', '')
        self.flagEmblemTex = settings.readString('flagEmblemTex', '')
        self.flagEmblemTexCoords = settings.readVector4('flagEmblemTexCoords', Vector4())
        self.flagScale = settings.readVector3('flagScale', Vector3())


ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_g_sectorBaseSettings = None

class SectorBase(BigWorld.Entity):
    _OVER_TERRAIN_HEIGHT = 0.5
    _PLAYER_TEAM_PARAMS = {}

    def __init__(self):
        global _g_sectorBaseSettings
        super(SectorBase, self).__init__(self)
        self.__flagModel = FlagModel()
        self.__terrainSelectedArea = None
        self.capturePercentage = 0
        self.__isCapturedOnStart = False
        self.__baseCaptureSoundObject = None
        self._baseCaptureSirenSoundIsPlaying = False
        if _g_sectorBaseSettings is None:
            settingsData = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE + '/sectorBase')
            _g_sectorBaseSettings = _SectorBaseSettingsCache(settingsData)
            SectorBase._PLAYER_TEAM_PARAMS = {True: (4278255360L, True),
             False: (4294901760L, False)}
        return

    def prerequisites(self):
        self.capturePercentage = float(self.pointsPercentage) / 100
        self.__isCapturedOnStart = self.isCaptured
        sectorBaseComponent = BigWorld.player().arena.componentSystem.sectorBaseComponent
        if sectorBaseComponent is not None:
            sectorBaseComponent.addSectorBase(self)
        rv = [_g_sectorBaseSettings.flagModelName, _g_sectorBaseSettings.flagStaffModelName, _g_sectorBaseSettings.radiusModel]
        mProv = Matrix()
        mProv.translation = self.position
        self.__baseCaptureSoundObject = SoundGroups.g_instance.WWgetSoundObject('base_' + str(self.baseID), mProv)
        self.__baseCaptureSoundObject.play(_g_sectorBaseSettings.baseAttachedSoundEventName)
        return rv

    def onEnterWorld(self, prereqs):
        self.capturePercentage = float(self.pointsPercentage) / 100
        if self.__isCapturedOnStart != self.isCaptured:
            self.set_isCaptured(self.__isCapturedOnStart)
        teamParams = self.__getTeamParams()
        flagSettings = FlagSettings(prereqs[_g_sectorBaseSettings.flagStaffModelName], prereqs[_g_sectorBaseSettings.flagModelName], _g_sectorBaseSettings.flagStaffFlagHP, _g_sectorBaseSettings.flagAnim, _g_sectorBaseSettings.flagBackgroundTex, _g_sectorBaseSettings.flagEmblemTex, _g_sectorBaseSettings.flagEmblemTexCoords, _g_sectorBaseSettings.flagScale)
        self.__flagModel.setupFlag(self.position, flagSettings, teamParams[0])
        self.__terrainSelectedArea = BigWorld.PyTerrainSelectedArea()
        self.__terrainSelectedArea.setup(_g_sectorBaseSettings.radiusModel, Vector2(self.radius * 2.0, self.radius * 2.0), self._OVER_TERRAIN_HEIGHT, teamParams[0])
        self.__flagModel.model.root.attach(self.__terrainSelectedArea)
        self.model = self.__flagModel.model
        self.__flagModel.startFlagAnimation()

    def onLeaveWorld(self):
        sectorBaseComponent = BigWorld.player().arena.componentSystem.sectorBaseComponent
        if sectorBaseComponent is not None:
            sectorBaseComponent.removeSectorBase(self)
        self.__prereqs = None
        self.__baseCaptureSoundObject.stopAll()
        self._baseCaptureSirenSoundIsPlaying = False
        self.__baseCaptureSoundObject = None
        self.__flagModel = None
        self.model = None
        return

    def isPlayerTeam(self):
        return self.team == BigWorld.player().team and not self.isCaptured or self.team != BigWorld.player().team and self.isCaptured

    def active(self):
        return self.isActive and not self.isCaptured

    def set_invadersCount(self, oldValue):
        sectorBaseComponent = BigWorld.player().arena.componentSystem.sectorBaseComponent
        if sectorBaseComponent is not None:
            sectorBaseComponent.sectorBasePointsUpdated(self)
        return

    def set_pointsPercentage(self, oldValue):
        sectorBaseComponent = BigWorld.player().arena.componentSystem.sectorBaseComponent
        self.capturePercentage = float(self.pointsPercentage) / 100
        if sectorBaseComponent is not None:
            sectorBaseComponent.sectorBasePointsUpdated(self)
        return

    def set_capturingStopped(self, oldValue):
        sectorBaseComponent = BigWorld.player().arena.componentSystem.sectorBaseComponent
        if sectorBaseComponent is not None:
            sectorBaseComponent.sectorBasePointsUpdated(self)
        return

    def set_isActive(self, oldValue):
        sectorBaseComponent = BigWorld.player().arena.componentSystem.sectorBaseComponent
        if sectorBaseComponent is not None:
            sectorBaseComponent.sectorBaseActiveStateChanged(self)
        return

    def set_isCaptured(self, oldValue):
        sectorBaseComponent = BigWorld.player().arena.componentSystem.sectorBaseComponent
        if sectorBaseComponent is not None:
            sectorBaseComponent.sectorBaseCaptured(self)
            if self.__flagModel:
                teamParams = self.__getTeamParams()
                self.__flagModel.changeFlagColor(teamParams[0])
                if self.__terrainSelectedArea is not None:
                    self.__terrainSelectedArea.setColor(teamParams[0])
        return

    def set_expectedCaptureTime(self, oldValue):
        sectorBaseComponent = BigWorld.player().arena.componentSystem.sectorBaseComponent
        self.expectedCaptureTime = self.expectedCaptureTime
        if sectorBaseComponent is not None:
            sectorBaseComponent.sectorBasePointsUpdated(self)
        return

    def __getTeamParams(self):
        return self._PLAYER_TEAM_PARAMS[self.isPlayerTeam()]
