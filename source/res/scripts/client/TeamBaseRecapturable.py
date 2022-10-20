# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TeamBaseRecapturable.py
from enum import IntEnum
import BigWorld
import ResMgr
from helpers import dependency
from Math import Vector4, Vector3, Vector2, Matrix
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from account_helpers.settings_core.settings_constants import GRAPHICS
import AnimationSequence

class _TeamBaseRecapturableSettingsCache(object):

    def __init__(self, settings=None):
        self.inited = False
        if settings is not None:
            self.initSettings(settings)
            self.inited = True
        return

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
        self.flagNodeAliasName = settings.readString('flagNodeAliasName', '')


ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_settings = _TeamBaseRecapturableSettingsCache()

class _TeamIds(IntEnum):
    NEUTRAL = 0
    PLAYER = 1
    ENEMY = 2


class ITeamBasesRecapturableListener(object):

    def onBaseCreated(self, teamBase):
        pass

    def onBaseCaptured(self, baseId, newTeam):
        pass

    def onBaseProgress(self, baseId, team, points, invadersCount, timeLeft):
        pass

    def onBaseCaptureStart(self, baseId, team, isPlayerTeam, invadersCount, timeLeft):
        pass

    def onBaseCaptureStop(self, baseId):
        pass

    def onBaseTeamChanged(self, baseId, prevTeam, newTeam):
        pass

    def onBaseInvadersTeamChanged(self, baseId, invadersTeam):
        pass


class TeamBaseRecapturable(BigWorld.Entity):
    _OVER_TERRAIN_HEIGHT = 0.5
    _TEAM_PARAMS = {}
    __settingsCore = dependency.descriptor(ISettingsCore)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        global _settings
        super(TeamBaseRecapturable, self).__init__(self)
        self.__rootModel = None
        self.__flagModel = None
        self.__raduisEmptyModel = None
        self.__flagFashion = None
        self.__terrainSelectedArea = None
        self.__initUpdateCB = None
        if not _settings.inited:
            settingsData = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE + '/teamBaseRecapturable')
            _settings = _TeamBaseRecapturableSettingsCache(settingsData)
            TeamBaseRecapturable._TEAM_PARAMS = {_TeamIds.NEUTRAL: (4294967295L, 4294967295L, True),
             _TeamIds.ENEMY: (4294851840L, 4290484735L, False),
             _TeamIds.PLAYER: (4289396480L, 4289396480L, True)}
        self._captureInProgress = False
        self._listeners = set()
        return

    def prerequisites(self):
        self.__rootModel = BigWorld.Model(_settings.flagStaffModelName)
        assembler = BigWorld.CompoundAssembler(_settings.flagModelName, self.spaceID)
        assembler.addRootPart(_settings.flagModelName, 'root')
        return [assembler, AnimationSequence.Loader(_settings.flagAnim, self.spaceID)]

    def onEnterWorld(self, prereqs):
        self.__rootModel.position = self.position
        flagStaffFlagHP = self.__rootModel.node(_settings.flagStaffFlagHP)
        matrix = Matrix()
        matrix.translation = self.position + flagStaffFlagHP.initialLocalMatrix.translation
        scaleMatrix = Matrix()
        scaleMatrix.setScale(_settings.flagScale)
        matrix.preMultiply(scaleMatrix)
        self.__flagModel = prereqs[_settings.flagModelName]
        self.__flagModel.matrix.preMultiply(matrix)
        BigWorld.addModel(self.__rootModel, self.spaceID)
        BigWorld.addModel(self.__flagModel, self.spaceID)
        self.__animator = prereqs[_settings.flagAnim]
        self.__animator.bindTo(AnimationSequence.CompoundWrapperContainer(self.__flagModel))
        self.__animator.start()
        teamParams = self.__getTeamParams()
        color = teamParams[0]
        self.__terrainSelectedArea = BigWorld.PyTerrainSelectedArea()
        self.__terrainSelectedArea.setup(_settings.radiusModel, Vector2(self.radius * 2.0, self.radius * 2.0), self._OVER_TERRAIN_HEIGHT, color)
        self.__raduisEmptyModel = BigWorld.Model('')
        self.__raduisEmptyModel.position = self.__rootModel.position
        self.__raduisEmptyModel.node('').attach(self.__terrainSelectedArea)
        BigWorld.addModel(self.__raduisEmptyModel, self.spaceID)
        self.__flagFashion = BigWorld.WGFlagAlphaFadeFashion()
        self.__flagFashion.setFlagBackgroundTexture(_settings.flagBackgroundTex)
        self.__flagFashion.setColor(color)
        self.__flagModel.setupFashions([self.__flagFashion])
        if self.teamBaseController:
            self.teamBaseController.onCreated(self)
        self.__settingsCore.onSettingsChanged += self._onSettingChanged
        for listener in self._listeners:
            listener.onBaseCreated(self)

        if self.invadersCount > 0:
            self.__initUpdateCB = BigWorld.callback(0, self._onInitWithInvaders)

    def onLeaveWorld(self):
        if self.__rootModel:
            BigWorld.delModel(self.__rootModel)
            self.__rootModel = None
        if self.__flagModel:
            BigWorld.delModel(self.__flagModel)
            self.__flagModel = None
        if self.__raduisEmptyModel:
            BigWorld.delModel(self.__raduisEmptyModel)
            self.__raduisEmptyModel = None
        self.__flagFashion = None
        self.__prereqs = None
        self._listeners = set()
        self.__settingsCore.onSettingsChanged -= self._onSettingChanged
        if self.teamBaseController:
            self.teamBaseController.onLeaveWorld(self.baseID)
        if self.__initUpdateCB is not None:
            BigWorld.cancelCallback(self.__initUpdateCB)
            self.__initUpdateCB = None
        return

    def registerListener(self, listener):
        self._listeners.add(listener)

    def unregisterListener(self, listener):
        self._listeners.discard(listener)

    def __getTeamParams(self):
        params = self._TEAM_PARAMS[self._getTeamId()]
        return (params[self.__settingsCore.getSetting(GRAPHICS.COLOR_BLIND)], params[2])

    def _getTeamId(self):
        if self.team == 0:
            return _TeamIds.NEUTRAL
        return _TeamIds.PLAYER if self.team == BigWorld.player().team else _TeamIds.ENEMY

    def set_captureTimeLeft(self, captureTimeLeft):
        self._updateProgress()

    def set_invadersTeam(self, invadersTeam):
        for listener in self._listeners:
            listener.onBaseInvadersTeamChanged(self.baseID, self.invadersTeam)

    def set_team(self, team):
        self._updateBaseColor()
        if not self._captureInProgress:
            for listener in self._listeners:
                listener.onBaseTeamChanged(self.baseID, team, self.team)

    def onCaptured(self):
        self._captureInProgress = True
        for listener in self._listeners:
            listener.onBaseCaptured(self.baseID, self.team)

    def onCaptureStart(self, team):
        self._doCaptureStart()

    def onCaptureStop(self):
        self._captureInProgress = False
        for listener in self._listeners:
            listener.onBaseCaptureStop(self.baseID)

    @property
    def teamBaseController(self):
        return self.__sessionProvider.dynamic.teamBaseRecapturable

    def _onSettingChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            self._updateBaseColor()

    def _updateBaseColor(self):
        teamParams = self.__getTeamParams()
        color = teamParams[0]
        if self.__flagFashion:
            self.__flagFashion.setColor(color)
        if self.__terrainSelectedArea is not None:
            self.__terrainSelectedArea.setColor(color)
        return

    def _onInitWithInvaders(self):
        self._doCaptureStart()
        if self.__initUpdateCB:
            BigWorld.cancelCallback(self.__initUpdateCB)
            self.__initUpdateCB = None
        self._updateProgress()
        return

    def _updateProgress(self):
        if self._captureInProgress:
            for listener in self._listeners:
                listener.onBaseProgress(self.baseID, self.team, self.points, self.invadersCount, self.captureTimeLeft)

    def _doCaptureStart(self):
        self._captureInProgress = True
        isPlayerTeam = self.team == BigWorld.player().team
        for listener in self._listeners:
            listener.onBaseCaptureStart(self.baseID, self.team, isPlayerTeam, self.invadersCount, self.captureTimeLeft)
