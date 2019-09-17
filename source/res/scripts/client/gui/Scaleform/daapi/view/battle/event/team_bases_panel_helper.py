# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/team_bases_panel_helper.py
from gui.shared.utils.functions import isControlPointExists, getBattleSubTypeBaseNumber
from gui.battle_control.controllers import team_bases_ctrl
from gui.Scaleform.locale.FESTIVAL import FESTIVAL
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from helpers import i18n

class _TeamBaseSettingItem(object):
    __slots__ = ('_weight', '_color', '_capturing', '_captured', 'captured', '_blocked', '_arenaTypeID', '_team', '_baseID', '_subTypeBaseID')

    def __init__(self, weight, color, capturing, captured, blocked):
        super(_TeamBaseSettingItem, self).__init__()
        self._weight = weight
        self._color = color
        self._capturing = capturing
        self._captured = captured
        self._blocked = blocked
        self._arenaTypeID = 0
        self._team = 0
        self._baseID = 0
        self._subTypeBaseID = 0

    def setup(self, arenaTypeID, baseID, team):
        self._arenaTypeID = arenaTypeID
        self._baseID = baseID
        self._team = team
        self._subTypeBaseID = getBattleSubTypeBaseNumber(self._arenaTypeID, self._team, self._baseID)

    def getWeight(self):
        return self._weight

    def getColor(self):
        return self._color

    def getCapturingString(self, points):
        return self._capturing % points

    def getBlockedString(self):
        return self._blocked

    def getCapturedString(self):
        return self._captured % self._subTypeBaseID

    def getBattleSubTypeBaseNumber(self):
        return getBattleSubTypeBaseNumber(self._arenaTypeID, self._team, self._baseID)


_SETTINGS_TO_TEAM = {0: (2,
     'red',
     i18n.makeString(FESTIVAL.FESTIVAL_PROGRESS_BAR_ENEMY_CAPTURE),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_ALLY_BASE_CAPTURED_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURE_BLOCKED)),
 3: (1,
     'green',
     i18n.makeString(FESTIVAL.FESTIVAL_PROGRESS_BAR_ALLY_CAPTURE),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_ENEMY_BASE_CAPTURED_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURE_BLOCKED))}
_SETTINGS_TO_CONTROL_POINT = {0: (4,
     'red',
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURED_BY_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURED_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURE_BLOCKED)),
 3: (3,
     'green',
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURED_BY_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURED_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURE_BLOCKED))}

def getFestivalSettingItem(clientID, ownTeam, arenaTypeID):
    baseTeam, baseID = team_bases_ctrl.parseClientTeamBaseID(clientID)
    itemSettings = (0, 'green', '%s %s', '%s %s', '%s %s')
    key = baseTeam ^ ownTeam
    if isControlPointExists(arenaTypeID):
        if key in _SETTINGS_TO_CONTROL_POINT:
            itemSettings = _SETTINGS_TO_CONTROL_POINT[key]
    elif key in _SETTINGS_TO_TEAM:
        itemSettings = _SETTINGS_TO_TEAM[key]
    item = _TeamBaseSettingItem(*itemSettings)
    item.setup(arenaTypeID, baseID, baseTeam)
    return item
