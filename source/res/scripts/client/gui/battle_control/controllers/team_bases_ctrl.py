# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/team_bases_ctrl.py
from collections import defaultdict
import BattleReplay
import BigWorld
import SoundGroups
from constants import TEAMS_IN_ARENA
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.battle_control.arena_info.interfaces import ITeamsBasesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
from PlayerEvents import g_playerEvents
_BASE_CAPTURE_SOUND_NAME_ENEMY = 'base_capture_2'
_BASE_CAPTURE_SOUND_NAME_ALLY = 'base_capture_1'
_AVAILABLE_TEAMS_NUMBERS = range(1, TEAMS_IN_ARENA.MAX_TEAMS + 1)
_UPDATE_POINTS_DELAY = 1.0
_ENEMY_OFFSET_DISABLED_BY_GAMEPLAY = ('assault', 'assault2', 'domination')

def makeClientTeamBaseID(team, baseID):
    """Makes unique ID to team base as first 6 bits of team number
    (0..63 ids available), the other bits on baseID.
    :param team: number of team.
    :param baseID:  number containing unique ID of base.
    :return: number containing client ID.
    """
    if baseID is None:
        baseID = 0
    return (int(baseID) << 6) + team


def parseClientTeamBaseID(clientID):
    """Parses clientID for team base.
    :param clientID: number containing client ID.
    :return: tuple(team, baseID)
    """
    team = clientID & 63
    return (team, clientID >> 6)


class ITeamBasesPanel(object):
    """
    View component that shows the team bases points.
    """

    def setOffsetForEnemyPoints(self):
        raise NotImplementedError

    def addCapturingTeamBase(self, clientID, playerTeam, points, rate, timeLeft, invadersCnt, capturingStopped):
        raise NotImplementedError

    def addCapturedTeamBase(self, clientID, playerTeam, timeLeft, invadersCnt):
        raise NotImplementedError

    def updateTeamBasePoints(self, clientID, points, rate, timeLeft, invadersCnt):
        raise NotImplementedError

    def stopTeamBaseCapturing(self, clientID, points):
        raise NotImplementedError

    def setTeamBaseCaptured(self, clientID, playerTeam):
        raise NotImplementedError

    def removeTeamBase(self, clientID):
        raise NotImplementedError

    def removeTeamsBases(self):
        raise NotImplementedError


class BattleTeamsBasesController(ITeamsBasesController, IViewComponentsController):
    """
    Controller adds, updates indicators in UI. It plays sounds when some base is
    capturing.
    """
    __slots__ = ('__ui', '__battleCtx', '__arenaVisitor', '__clientIDs', '__points', '__sounds', '__callbackIDs', '__snap', '__captured')

    def __init__(self):
        super(BattleTeamsBasesController, self).__init__()
        self.__ui = None
        self.__battleCtx = None
        self.__arenaVisitor = None
        self.__clientIDs = set()
        self.__points = {}
        self.__captured = set()
        self.__sounds = {}
        self.__callbackIDs = {}
        self.__snap = defaultdict(tuple)
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.TEAM_BASES

    def startControl(self, battleCtx, arenaVisitor):
        """Starts to control
        :param battleCtx: instance of BattleContext.
        :param arenaVisitor: instance of _ClientArenaVisitor.
        """
        self.__battleCtx = battleCtx
        self.__arenaVisitor = arenaVisitor
        g_playerEvents.onTeamChanged += self.__onTeamChanged

    def stopControl(self):
        """Stops to control"""
        while self.__clientIDs:
            clientID = self.__clientIDs.pop()
            if self.__ui is not None:
                self.__ui.removeTeamBase(clientID)

        self.__battleCtx = None
        self.__arenaVisitor = None
        self.__clearUpdateCallbacks()
        self.__stopCaptureSounds()
        self.__ui = None
        self.__clientIDs.clear()
        self.__points.clear()
        self.__sounds.clear()
        self.__snap.clear()
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        return

    def setViewComponents(self, panel):
        """
        Sets view component.
        :param panel: instance of view component.
        """
        if not panel:
            return
        self.__ui = panel
        name = self.__arenaVisitor.type.getGamePlayName()
        if name and name not in _ENEMY_OFFSET_DISABLED_BY_GAMEPLAY:
            self.__ui.setOffsetForEnemyPoints()
        playerTeam = self.__battleCtx.getArenaDP().getNumberOfTeam()
        for clientID, (points, timeLeft, invadersCnt, stopped) in self.__points.iteritems():
            if clientID in self.__captured:
                self.__ui.addCapturedTeamBase(clientID, playerTeam, timeLeft, invadersCnt)
            if points:
                self.__ui.addCapturingTeamBase(clientID, playerTeam, points, self._getProgressRate(), timeLeft, invadersCnt, stopped)

    def clearViewComponents(self):
        """
        Clears reference to view component.
        """
        self.__ui = None
        return

    def getTeamBasePoints(self, clientID):
        """
        Gets capture points for specified team base.
        :param clientID: integer containing generated ID by makeClientTeamBaseID.
        :return: integer containing value of points.
        """
        points = 0
        if clientID in self.__points:
            points, _, _, _ = self.__points[clientID]
        return points

    def isTeamBaseCaptured(self, clientID):
        """
        Is base captured.
        :param clientID: integer containing generated ID by makeClientTeamBaseID.
        :return: bool.
        """
        return clientID in self.__captured

    def invalidateTeamBasePoints(self, baseTeam, baseID, points, timeLeft, invadersCnt, capturingStopped):
        """
        Adds/Updates indicator for base that is capturing in UI.
        :param baseTeam: number of base's team.
        :param baseID: integer containing unique ID of base.
        :param points: integer containing value of points (0 ... 100).
        :param timeLeft: time left until base will be captured
        :param invadersCnt: count of invaders
        :param capturingStopped: is capture stopped.
        :return:
        """
        if baseTeam not in _AVAILABLE_TEAMS_NUMBERS:
            return
        clientID = makeClientTeamBaseID(baseTeam, baseID)
        arenaDP = self.__battleCtx.getArenaDP()
        playerTeam = arenaDP.getNumberOfTeam()
        isEnemyBase = arenaDP.isEnemyTeam(baseTeam)
        self.__points[clientID] = (points,
         timeLeft,
         invadersCnt,
         capturingStopped)
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
                    self.__ui.addCapturingTeamBase(clientID, playerTeam, points, self._getProgressRate(), timeLeft, invadersCnt, capturingStopped)
                self.__addUpdateCallback(clientID)
            if not capturingStopped:
                self.__playCaptureSound(playerTeam, baseTeam)
            elif not self.__hasBaseID(baseTeam, exclude=clientID) or isEnemyBase:
                self.__stopCaptureSound(baseTeam)

    def invalidateTeamBaseCaptured(self, baseTeam, baseID):
        """
        Adds/Updates indicator for base that is captured in UI.
        :param baseTeam: number of base's team.
        :param baseID: integer containing unique ID of base.
        """
        if baseTeam not in _AVAILABLE_TEAMS_NUMBERS:
            return
        clientID = makeClientTeamBaseID(baseTeam, baseID)
        playerTeam = self.__battleCtx.getArenaDP().getNumberOfTeam()
        self.__captured.add(clientID)
        if clientID in self.__clientIDs:
            if self.__ui:
                self.__ui.setTeamBaseCaptured(clientID, playerTeam)
        else:
            self.__clientIDs.add(clientID)
            timeLeft = invadersCnt = 0
            if clientID in self.__points:
                _, timeLeft, invadersCnt, _ = self.__points[clientID]
            if self.__ui:
                self.__ui.addCapturedTeamBase(clientID, playerTeam, timeLeft, invadersCnt)
        self.__stopCaptureSound(baseTeam)

    def removeTeamsBases(self):
        """
        Removes all teams base from UI, stop plays sounds.
        """
        if not BattleReplay.isPlaying() and self.__ui:
            self.__ui.removeTeamsBases()
        self.__stopCaptureSounds()

    def __onTeamChanged(self, teamID):
        """
        Remove the UI, so that it can be re-added next go-round in the correct color
        """
        for clientID in self.__clientIDs:
            self.__clearUpdateCallback(clientID)
            self.__stopCaptureSound(clientID)
            if not BattleReplay.isPlaying() and self.__ui:
                self.__ui.removeTeamBase(clientID)

        self.__clientIDs.clear()

    def _getProgressRate(self):
        pass

    def __hasBaseID(self, team, exclude=-1):
        return len(filter(lambda i: i & team != 0 and i != exclude, self.__clientIDs)) > 0

    def __playCaptureSound(self, playerTeam, baseTeam):
        if baseTeam not in self.__sounds:
            if playerTeam ^ baseTeam:
                soundID = _BASE_CAPTURE_SOUND_NAME_ENEMY
            else:
                soundID = _BASE_CAPTURE_SOUND_NAME_ALLY
            try:
                sound = self.__sounds.get(baseTeam, None)
                if sound is not None:
                    sound.stop()
                sound = SoundGroups.g_instance.getSound2D(soundID)
                sound.play()
                self.__sounds[baseTeam] = sound
            except Exception:
                LOG_CURRENT_EXCEPTION()

        return

    def __stopCaptureSound(self, team):
        sound = self.__sounds.pop(team, None)
        if sound is not None:
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
        points, timeLeft, invadersCnt, _ = self.__points[clientID]
        rate = self._getProgressRate()
        if self.__ui and self.__snap[clientID] != (points, rate, timeLeft):
            self.__snap[clientID] = (points, rate, timeLeft)
            self.__ui.updateTeamBasePoints(clientID, points, rate, timeLeft, invadersCnt)

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
    """
    There is controller in replays.
    """

    def _getProgressRate(self):
        rate = BattleReplay.g_replayCtrl.playbackSpeed
        if rate is None:
            rate = super(BattleTeamsBasesPlayer, self)._getProgressRate()
        return rate


def createTeamsBasesCtrl(setup):
    if setup.isReplayPlaying:
        ctrl = BattleTeamsBasesPlayer()
    else:
        ctrl = BattleTeamsBasesController()
    return ctrl
