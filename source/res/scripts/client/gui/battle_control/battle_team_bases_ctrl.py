# Embedded file name: scripts/client/gui/battle_control/battle_team_bases_ctrl.py
from collections import defaultdict
import weakref
import BattleReplay
import BigWorld
import SoundGroups
from constants import TEAMS_IN_ARENA
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.battle_control import arena_info
from gui.battle_control.arena_info.interfaces import ITeamsBasesController
from gui.shared.utils.functions import getArenaSubTypeName
import FMOD
if FMOD.enabled:
    _BASE_CAPTURE_SOUND_NAME_ENEMY = '/GUI/notifications_FX/base_capture_2'
    _BASE_CAPTURE_SOUND_NAME_ALLY = '/GUI/notifications_FX/base_capture_1'
_AVAILABLE_TEAMS_NUMBERS = range(1, TEAMS_IN_ARENA.MAX_TEAMS + 1)
_UPDATE_POINTS_DELAY = 1.0
_ENEMY_OFFSET_DISABLED_BY_GAMEPLAY = ('assault', 'assault2', 'domination')

class ITeamBasesPanel(object):

    def setOffsetForEnemyPoints(self):
        raise NotImplementedError

    def addCapturingTeamBase(self, clientID, playerTeam, points, rate, capturingStopped):
        raise NotImplementedError

    def addCapturedTeamBase(self, clientID, playerTeam):
        raise NotImplementedError

    def updateTeamBasePoints(self, clientID, points, rate):
        raise NotImplementedError

    def stopTeamBaseCapturing(self, clientID, points):
        raise NotImplementedError

    def setTeamBaseCaptured(self, clientID, playerTeam):
        raise NotImplementedError

    def removeTeamBase(self, clientID):
        raise NotImplementedError

    def removeTeamsBases(self):
        raise NotImplementedError


class BattleTeamsBasesController(ITeamsBasesController):
    __slots__ = ('__ui', '__battleCtx', '__clientIDs', '__points', '__sounds', '__callbackIDs', '__snap', '__captured')

    def __init__(self):
        super(BattleTeamsBasesController, self).__init__()
        self.__ui = None
        self.__battleCtx = None
        self.__clientIDs = set()
        self.__points = {}
        self.__captured = set()
        self.__sounds = {}
        self.__callbackIDs = {}
        self.__snap = defaultdict(tuple)
        return

    def setBattleCtx(self, battleCtx):
        self.__battleCtx = battleCtx

    def setUI(self, ui):
        if not ui:
            return
        self.__ui = weakref.proxy(ui)
        typeID = arena_info.getArenaTypeID()
        if typeID and getArenaSubTypeName(typeID) not in _ENEMY_OFFSET_DISABLED_BY_GAMEPLAY:
            self.__ui.setOffsetForEnemyPoints()
        playerTeam = self.__battleCtx.getArenaDP().getNumberOfTeam()
        for clientID, (points, stopped) in self.__points.iteritems():
            if clientID in self.__captured:
                self.__ui.addCapturedTeamBase(clientID, playerTeam)
            elif points:
                self.__ui.addCapturingTeamBase(clientID, playerTeam, points, self._getProgressRate(), stopped)

    def clearUI(self):
        self.__ui = None
        return

    def clear(self):
        self.__clearUpdateCallbacks()
        self.__stopCaptureSounds()
        self.__ui = None
        self.__clientIDs.clear()
        self.__points.clear()
        self.__sounds.clear()
        self.__snap.clear()
        return

    def getTeamBasePoints(self, clientID):
        points = 0
        if clientID in self.__points:
            points, _ = self.__points[clientID]
        return points

    def isTeamBaseCaptured(self, clientID):
        return clientID in self.__captured

    def invalidateTeamBasePoints(self, baseTeam, baseID, points, capturingStopped):
        if baseTeam not in _AVAILABLE_TEAMS_NUMBERS:
            return
        clientID = arena_info.makeClientTeamBaseID(baseTeam, baseID)
        arenaDP = self.__battleCtx.getArenaDP()
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemyBase = arenaDP.isEnemyTeam(baseTeam)
        self.__points[clientID] = (points, capturingStopped)
        if not points:
            if clientID in self.__clientIDs:
                self.__clearUpdateCallback(clientID)
                self.__clientIDs.remove(clientID)
                if self.__ui:
                    self.__ui.removeTeamBase(clientID)
                if not self.__hasBaseID(baseTeam) or isEnemyBase:
                    self.__stopCaptureSound(baseTeam)
        else:
            if clientID in self.__clientIDs:
                if capturingStopped and self.__ui:
                    self.__ui.stopTeamBaseCapturing(clientID, points)
            else:
                self.__clientIDs.add(clientID)
                if self.__ui:
                    self.__ui.addCapturingTeamBase(clientID, playerTeam, points, self._getProgressRate(), capturingStopped)
                self.__addUpdateCallback(clientID)
            if not capturingStopped:
                self.__playCaptureSound(playerTeam, baseTeam)
            elif not self.__hasBaseID(baseTeam, exclude=clientID) or isEnemyBase:
                self.__stopCaptureSound(baseTeam)

    def invalidateTeamBaseCaptured(self, baseTeam, baseID):
        if baseTeam not in _AVAILABLE_TEAMS_NUMBERS:
            return
        clientID = arena_info.makeClientTeamBaseID(baseTeam, baseID)
        playerTeam = self.__battleCtx.getArenaDP().getNumberOfTeam()
        self.__captured.add(clientID)
        if clientID in self.__clientIDs:
            if self.__ui:
                self.__ui.setTeamBaseCaptured(clientID, playerTeam)
        else:
            self.__clientIDs.add(clientID)
            if self.__ui:
                self.__ui.addCapturedTeamBase(clientID, playerTeam)
        self.__stopCaptureSound(baseTeam)

    def removeTeamsBases(self):
        if self.__ui:
            self.__ui.removeTeamsBases()
        self.__stopCaptureSounds()

    def _getProgressRate(self):
        return 1

    def __hasBaseID(self, team, exclude = -1):
        return len(filter(lambda i: i & team != 0 and i != exclude, self.__clientIDs)) > 0

    def __playCaptureSound(self, playerTeam, baseTeam):
        if baseTeam not in self.__sounds:
            if playerTeam ^ baseTeam:
                soundID = _BASE_CAPTURE_SOUND_NAME_ENEMY
            else:
                soundID = _BASE_CAPTURE_SOUND_NAME_ALLY
            try:
                sound = SoundGroups.g_instance.getSound2D(soundID)
                sound.play()
                self.__sounds[baseTeam] = sound
            except Exception:
                LOG_CURRENT_EXCEPTION()

    def __stopCaptureSound(self, team):
        sound = self.__sounds.pop(team, None)
        if sound:
            try:
                sound.stop()
            except Exception:
                LOG_CURRENT_EXCEPTION()

        return

    def __stopCaptureSounds(self):
        for team in self.__sounds.keys():
            self.__stopCaptureSound(team)

    def __updatePoints(self, clientID):
        if clientID not in self.__clientIDs:
            return
        points, _ = self.__points[clientID]
        rate = self._getProgressRate()
        if self.__ui and self.__snap[clientID] != (points, rate):
            self.__snap[clientID] = (points, rate)
            self.__ui.updateTeamBasePoints(clientID, points, rate)

    def __tickToUpdatePoints(self, clientID):
        self.__callbackIDs.pop(clientID, None)
        self.__updatePoints(clientID)
        self.__addUpdateCallback(clientID)
        return

    def __addUpdateCallback(self, clientID):
        self.__callbackIDs[clientID] = BigWorld.callback(_UPDATE_POINTS_DELAY, lambda : self.__tickToUpdatePoints(clientID))

    def __clearUpdateCallback(self, clientID):
        callbackID = self.__callbackIDs.pop(clientID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        self.__snap.pop(clientID, None)
        return

    def __clearUpdateCallbacks(self):
        for _, callbackID in self.__callbackIDs.items():
            BigWorld.cancelCallback(callbackID)

        self.__callbackIDs.clear()


class BattleTeamsBasesPlayer(BattleTeamsBasesController):

    def _getProgressRate(self):
        rate = BattleReplay.g_replayCtrl.playbackSpeed
        if rate is None:
            rate = super(BattleTeamsBasesPlayer, self)._getProgressRate()
        return rate


def createTeamsBasesCtrl(isReplayPlaying):
    if isReplayPlaying:
        ctrl = BattleTeamsBasesPlayer()
    else:
        ctrl = BattleTeamsBasesController()
    return ctrl
