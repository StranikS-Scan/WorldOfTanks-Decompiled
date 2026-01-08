# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/team_bases_panel.py
from gui.Scaleform.daapi.view.battle.classic.team_bases_panel import TeamBasesPanel, TeamBaseSettingItem, buildTeamBaseSettingItem
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from epic_constants import SECTORS
from helpers import i18n
_EPIC_SETTINGS_TO_TEAM = {0: (2,
     'red',
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_EPIC_ALLY_BASE_CAPTURED_BY_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_EPIC_ALLY_BASE_CAPTURED_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURE_BLOCKED)),
 3: (1,
     'green',
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_EPIC_ENEMY_BASE_CAPTURED_BY_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_EPIC_ENEMY_BASE_CAPTURED_NOTIFICATION),
     i18n.makeString(I18N_INGAME_GUI.PLAYER_MESSAGES_BASE_CAPTURE_BLOCKED))}

def _getEpicSettingItem(clientID, ownTeam, arenaTypeID):
    return buildTeamBaseSettingItem(clientID, ownTeam, arenaTypeID, _EPIC_SETTINGS_TO_TEAM, EpicTeamBaseSettingItem)


class EpicTeamBaseSettingItem(TeamBaseSettingItem):
    __slots__ = ('_sectorLetter',)

    def __init__(self, weight, color, capturing, captured, blocked):
        super(EpicTeamBaseSettingItem, self).__init__(weight, color, capturing, captured, blocked)
        self._sectorLetter = ''

    def setup(self, arenaTypeID, baseID, team):
        super(EpicTeamBaseSettingItem, self).setup(arenaTypeID, baseID, team)
        idx = max(0, min(self._baseID - 1, len(SECTORS) - 1))
        self._sectorLetter = SECTORS[idx]

    def getCapturingString(self, points):
        return self._capturing % (self._subTypeBaseID, self._sectorLetter, points)

    def getCapturedString(self):
        return self._captured % (self._subTypeBaseID, self._sectorLetter)


class EpicTeamBasesPanel(TeamBasesPanel):

    def makeSettingItem(self, clientID, playerTeam):
        return _getEpicSettingItem(clientID, playerTeam, self.sessionProvider.arenaVisitor.type.getID())
