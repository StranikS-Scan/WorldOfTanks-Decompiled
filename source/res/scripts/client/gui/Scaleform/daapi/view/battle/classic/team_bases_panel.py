# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/team_bases_panel.py
from constants import ARENA_GUI_TYPE
from gui.Scaleform.daapi.view.meta.TeamBasesPanelMeta import TeamBasesPanelMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from gui.battle_control.controllers import team_bases_ctrl
from gui.shared.utils.functions import getBattleSubTypeBaseNumber
from gui.shared.utils.functions import isControlPointExists
from helpers import dependency
from helpers import i18n, time_utils
from skeletons.gui.battle_session import IBattleSessionProvider
_MAX_INVADERS_COUNT = 3

class TeamBaseSettingItem(object):
    __slots__ = ('_weight', '_color', '_capturing', '_captured', '_blocked', '_arenaTypeID', '_team', '_baseID', '_subTypeBaseID')

    def __init__(self, weight, color, capturing, captured, blocked):
        super(TeamBaseSettingItem, self).__init__()
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
        return self._capturing % (self._subTypeBaseID, points)

    def getBlockedString(self):
        return self._blocked

    def getCapturedString(self):
        return self._captured % self._subTypeBaseID

    def getBattleSubTypeBaseNumber(self):
        return getBattleSubTypeBaseNumber(self._arenaTypeID, self._team, self._baseID)


_SETTINGS_TO_TEAM = {0: (2,
     'red',
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_ALLY_BASE_CAPTURED_BY_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_ALLY_BASE_CAPTURED_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURE_BLOCKED)),
 3: (1,
     'green',
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_ENEMY_BASE_CAPTURED_BY_NOTIFICATION),
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
_DEFAULT_SETTINGS = (0, 'green', '%s %s', '%s %s', '%s %s')

def buildTeamBaseSettingItem(clientID, ownTeam, arenaTypeID, teamSettingsMap, teamItemCls):
    baseTeam, baseID = team_bases_ctrl.parseClientTeamBaseID(clientID)
    key = baseTeam ^ ownTeam
    if isControlPointExists(arenaTypeID):
        settingsMap = _SETTINGS_TO_CONTROL_POINT
        itemCls = TeamBaseSettingItem
    else:
        settingsMap = teamSettingsMap
        itemCls = teamItemCls
    itemSettings = settingsMap.get(key, _DEFAULT_SETTINGS)
    item = itemCls(*itemSettings)
    item.setup(arenaTypeID, baseID, baseTeam)
    return item


def _getSettingItem(clientID, ownTeam, arenaTypeID):
    return buildTeamBaseSettingItem(clientID, ownTeam, arenaTypeID, _SETTINGS_TO_TEAM, TeamBaseSettingItem)


class TeamBasesPanel(TeamBasesPanelMeta, team_bases_ctrl.ITeamBasesListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TeamBasesPanel, self).__init__()
        self.__basesDict = {}

    def setOffsetForEnemyPoints(self):
        self.as_setOffsetForEnemyPointsS()

    def addCapturingTeamBase(self, clientID, playerTeam, points, _, timeLeft, invadersCnt, capturingStopped, extraInvader=False):
        item = self.makeSettingItem(clientID, playerTeam)
        title = item.getCapturingString(points)
        self.as_addS(clientID, item.getWeight(), item.getColor(), title, points, time_utils.getTimeLeftFormat(timeLeft), self.__getInvadersCountStr(invadersCnt), extraInvader)
        self.__basesDict[clientID] = item
        if capturingStopped:
            if invadersCnt > 0:
                self.blockTeamBaseCapturing(clientID, points)
            else:
                self.stopTeamBaseCapturing(clientID, points)

    def addCapturedTeamBase(self, clientID, playerTeam, timeLeft, invadersCnt, extraInvader=False):
        item = self.makeSettingItem(clientID, playerTeam)
        title = item.getCapturedString()
        self.as_addS(clientID, item.getWeight(), item.getColor(), title, 100, time_utils.getTimeLeftFormat(timeLeft), self.__getInvadersCountStr(invadersCnt), extraInvader)
        self.__basesDict[clientID] = item

    def updateTeamBasePoints(self, clientID, points, rate, timeLeft, invadersCnt, extraInvader=False):
        item = self.__basesDict.get(clientID, None)
        if not item:
            return
        else:
            capturingString = item.getCapturingString(points)
            self.as_updateCaptureDataS(clientID, points, rate, time_utils.getTimeLeftFormat(timeLeft), self.__getInvadersCountStr(invadersCnt), capturingString, extraInvader, item.getColor())
            return

    def blockTeamBaseCapturing(self, clientID, points):
        item = self.__basesDict.get(clientID, None)
        if not item:
            return
        else:
            color = 'gray' if self.sessionProvider.arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.EPIC_RANGE else item.getColor()
            self.as_updateCaptureDataS(clientID, points, 0, '-:-', -1, item.getBlockedString(), False, color)
            return

    def stopTeamBaseCapturing(self, clientID, points):
        if clientID not in self.__basesDict:
            return
        self.as_stopCaptureS(clientID, points)

    def setTeamBaseCaptured(self, clientID, playerTeam):
        if clientID in self.__basesDict:
            item = self.__basesDict[clientID]
        else:
            item = self.makeSettingItem(clientID, playerTeam)
        self.as_setCapturedS(clientID, item.getCapturedString())

    def removeTeamBase(self, clientID):
        if clientID in self.__basesDict:
            self.__basesDict.pop(clientID)
            self.as_removeS(clientID)

    def removeTeamsBases(self):
        self.__basesDict.clear()
        self.as_clearS()

    def makeSettingItem(self, clientID, playerTeam):
        return _getSettingItem(clientID, playerTeam, self.sessionProvider.arenaVisitor.type.getID())

    @staticmethod
    def __getInvadersCountStr(count):
        return count if count < _MAX_INVADERS_COUNT else _MAX_INVADERS_COUNT
