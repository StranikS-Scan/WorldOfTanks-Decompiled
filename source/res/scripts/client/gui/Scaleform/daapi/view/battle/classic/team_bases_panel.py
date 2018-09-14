# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/team_bases_panel.py
from gui.Scaleform.daapi.view.meta.TeamBasesPanelMeta import TeamBasesPanelMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from gui.battle_control import g_sessionProvider
from gui.battle_control.controllers import team_bases_ctrl
from gui.shared.utils.functions import getBattleSubTypeBaseNumder
from gui.shared.utils.functions import isControlPointExists
from helpers import i18n, time_utils
_MAX_INVADERS_COUNT = 3

class _TeamBaseSettingItem(object):
    __slots__ = ('_weight', '_color', '_capturing', '_captured', 'captured', '_arenaTypeID', '_team', '_baseID')

    def __init__(self, weight, color, capturing, captured):
        super(_TeamBaseSettingItem, self).__init__()
        self._weight = weight
        self._color = color
        self._capturing = capturing
        self._captured = captured
        self._arenaTypeID = 0
        self._team = 0
        self._baseID = 0

    def setup(self, arenaTypeID, baseID, team):
        self._arenaTypeID = arenaTypeID
        self._baseID = baseID
        self._team = team

    def getWeight(self):
        return self._weight

    def getColor(self):
        return self._color

    def getCapturingString(self):
        return self._capturing % getBattleSubTypeBaseNumder(self._arenaTypeID, self._team, self._baseID)

    def getCapturedString(self):
        return self._captured % getBattleSubTypeBaseNumder(self._arenaTypeID, self._team, self._baseID)


_SETTINGS_TO_TEAM = {0: _TeamBaseSettingItem(2, 'red', i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_ALLY_BASE_CAPTURED_BY_NOTIFICATION), i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_ALLY_BASE_CAPTURED_NOTIFICATION)),
 3: _TeamBaseSettingItem(1, 'green', i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_ENEMY_BASE_CAPTURED_BY_NOTIFICATION), i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_ENEMY_BASE_CAPTURED_NOTIFICATION))}
_SETTINGS_TO_CONTROL_POINT = {0: _TeamBaseSettingItem(4, 'red', i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURED_BY_NOTIFICATION), i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURED_BY_NOTIFICATION)),
 3: _TeamBaseSettingItem(3, 'green', i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURED_BY_NOTIFICATION), i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURED_BY_NOTIFICATION))}

def _getSettingItem(clientID, ownTeam, arenaTypeID):
    baseTeam, baseID = team_bases_ctrl.parseClientTeamBaseID(clientID)
    item = None
    key = baseTeam ^ ownTeam
    if isControlPointExists(arenaTypeID):
        if key in _SETTINGS_TO_CONTROL_POINT:
            item = _SETTINGS_TO_CONTROL_POINT[key]
    elif key in _SETTINGS_TO_TEAM:
        item = _SETTINGS_TO_TEAM[key]
    if item is None:
        item = _TeamBaseSettingItem(0, 'green', '%s', '%s')
    item.setup(arenaTypeID, baseID, baseTeam)
    return item


class TeamBasesPanel(TeamBasesPanelMeta, team_bases_ctrl.ITeamBasesPanel):

    def __init__(self):
        super(TeamBasesPanel, self).__init__()

    def setOffsetForEnemyPoints(self):
        self.as_setOffsetForEnemyPointsS()

    def addCapturingTeamBase(self, clientID, playerTeam, points, _, timeLeft, invadersCnt, capturingStopped):
        item = _getSettingItem(clientID, playerTeam, g_sessionProvider.arenaVisitor.type.getID())
        self.as_addS(clientID, item.getWeight(), item.getColor(), item.getCapturingString(), points, time_utils.getTimeLeftFormat(timeLeft), self.__getInvadersCountStr(invadersCnt))
        if capturingStopped:
            self.stopTeamBaseCapturing(clientID, points)

    def addCapturedTeamBase(self, clientID, playerTeam, timeLeft, invadersCnt):
        item = _getSettingItem(clientID, playerTeam, g_sessionProvider.arenaVisitor.type.getID())
        self.as_addS(clientID, item.getWeight(), item.getColor(), item.getCapturingString(), 100, time_utils.getTimeLeftFormat(timeLeft), self.__getInvadersCountStr(invadersCnt))

    def updateTeamBasePoints(self, clientID, points, rate, timeLeft, invadersCnt):
        self.as_updateCaptureDataS(clientID, points, rate, time_utils.getTimeLeftFormat(timeLeft), self.__getInvadersCountStr(invadersCnt))

    def stopTeamBaseCapturing(self, clientID, points):
        self.as_stopCaptureS(clientID, points)

    def setTeamBaseCaptured(self, clientID, playerTeam):
        item = _getSettingItem(clientID, playerTeam, g_sessionProvider.arenaVisitor.type.getID())
        self.as_setCapturedS(clientID, item.getCapturedString())

    def removeTeamBase(self, clientID):
        self.as_removeS(clientID)

    def removeTeamsBases(self):
        self.as_clearS()

    @staticmethod
    def __getInvadersCountStr(count):
        if count < _MAX_INVADERS_COUNT:
            return str(count)
        else:
            return str(_MAX_INVADERS_COUNT)
