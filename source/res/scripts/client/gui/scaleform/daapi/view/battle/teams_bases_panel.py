# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/teams_bases_panel.py
from debug_utils import LOG_DEBUG
from gui.battle_control import arena_info
from gui.battle_control.battle_team_bases_ctrl import ITeamBasesPanel
from gui.shared.utils.functions import isControlPointExists, getBattleSubTypeBaseNumder
from helpers import i18n

class _TeamBaseSettingItem(object):
    __slots__ = ('_weight', '_color', '_capturing', '_captured', '_arenaTypeID', '_team', '_baseID')

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


_SETTINGS_TO_TEAM = {0: _TeamBaseSettingItem(2, 'red', i18n.makeString('#ingame_gui:player_messages/ally_base_captured_by_notification'), i18n.makeString('#ingame_gui:player_messages/ally_base_captured_notification')),
 3: _TeamBaseSettingItem(1, 'green', i18n.makeString('#ingame_gui:player_messages/enemy_base_captured_by_notification'), i18n.makeString('#ingame_gui:player_messages/enemy_base_captured_notification'))}
_SETTINGS_TO_CONTROL_POINT = {0: _TeamBaseSettingItem(4, 'red', i18n.makeString('#ingame_gui:player_messages/base_captured_by_notification'), i18n.makeString('#ingame_gui:player_messages/base_captured_by_notification')),
 3: _TeamBaseSettingItem(3, 'green', i18n.makeString('#ingame_gui:player_messages/base_captured_by_notification'), i18n.makeString('#ingame_gui:player_messages/base_captured_by_notification'))}

def getSettingItem(clientID, ownTeam, avatar = None):
    arenaTypeID = arena_info.getArenaTypeID(avatar)
    baseTeam, baseID = arena_info.parseClientTeamBaseID(clientID)
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


class TeamBasesPanel(ITeamBasesPanel):

    def __init__(self, parentUI):
        self.__ui = parentUI

    def __del__(self):
        LOG_DEBUG('TeamBasesPanel is deleted')

    def destroy(self):
        self.__ui = None
        return

    def setOffsetForEnemyPoints(self):
        self.__callFlash('init', [True])

    def addCapturingTeamBase(self, clientID, playerTeam, points, rate, capturingStopped):
        item = getSettingItem(clientID, playerTeam)
        self.__callFlash('add', [clientID,
         item.getWeight(),
         item.getColor(),
         item.getCapturingString(),
         points,
         rate])
        if capturingStopped:
            self.__callFlash('stop', [clientID, points])

    def addCapturedTeamBase(self, clientID, playerTeam):
        item = getSettingItem(clientID, playerTeam)
        self.__callFlash('add', [clientID,
         item.getColor(),
         item.getWeight(),
         item.getCapturedString(),
         100])

    def updateTeamBasePoints(self, clientID, points, rate):
        self.__callFlash('updatePoints', [clientID, points, rate])

    def stopTeamBaseCapturing(self, clientID, points):
        self.__callFlash('stop', [clientID, points])

    def setTeamBaseCaptured(self, clientID, playerTeam):
        item = getSettingItem(clientID, playerTeam)
        self.__callFlash('setCaptured', [clientID, item.getCapturedString()])

    def removeTeamBase(self, clientID):
        self.__callFlash('remove', [clientID])

    def removeTeamsBases(self):
        self.__callFlash('clear', [])

    def __callFlash(self, funcName, args):
        self.__ui.call('battle.teamBasesPanel.{0:>s}'.format(funcName), args)
