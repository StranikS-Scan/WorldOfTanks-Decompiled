# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/ColorSchemeManager.py
import BigWorld
from gui.Scaleform.framework.entities.abstract.ColorSchemeManagerMeta import ColorSchemeManagerMeta
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.doc_loaders import GuiColorsLoader
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider

class ColorSchemeManager(ColorSchemeManagerMeta):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(ColorSchemeManager, self).__init__()
        self.colors = GuiColorsLoader.load()

    def getColorGroup(self):
        return 'color_blind' if self.settingsCore.getSetting('isColorBlind') else 'default'

    def getRGBA(self, schemeName):
        return self.colors.getSubScheme(schemeName, self.getColorGroup())['rgba']

    def getColorScheme(self, schemeName):
        scheme = self.colors.getSubScheme(schemeName, self.getColorGroup())
        transform = scheme['transform']
        return {'aliasColor': scheme['alias_color'],
         'rgb': self._packRGB(scheme['rgba']),
         'adjust': {'offset': scheme['adjust']['offset'].tuple()},
         'transform': {'mult': transform['mult'].tuple(),
                       'offset': transform['offset'].tuple()}}

    def getIsColorBlind(self):
        return self.settingsCore.getSetting('isColorBlind')

    def update(self):
        self.as_updateS()

    def _populate(self):
        super(ColorSchemeManager, self)._populate()
        self.settingsCore.onSettingsChanged += self.__onAccountSettingsChange

    def _dispose(self):
        self.settingsCore.onSettingsChanged -= self.__onAccountSettingsChange
        super(ColorSchemeManager, self)._dispose()

    @classmethod
    def _packRGB(cls, rgba):
        return (int(rgba[0]) << 16) + (int(rgba[1]) << 8) + (int(rgba[2]) << 0)

    @classmethod
    def _makeRGB(cls, subScheme):
        return cls._packRGB(subScheme.get('rgb', (0, 0, 0, 0)))

    @classmethod
    def _makeAdjustTuple(cls, subScheme):
        return subScheme['adjust']['offset']

    def __onAccountSettingsChange(self, diff):
        if 'isColorBlind' in diff:
            self.update()


class BattleColorSchemeManager(ColorSchemeManager, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def update(self):
        super(BattleColorSchemeManager, self).update()
        self.__set3DFlagsColors()

    def invalidateArenaInfo(self):
        self.__set3DFlagsColors()

    def _populate(self):
        super(BattleColorSchemeManager, self)._populate()
        self.__set3DFlagsEmblem()
        from PlayerEvents import g_playerEvents
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        self.sessionProvider.addArenaCtrl(self)

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        from PlayerEvents import g_playerEvents
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        super(BattleColorSchemeManager, self)._dispose()

    def __set3DFlagsColors(self):
        arenaDP = self.sessionProvider.getArenaDP()
        teamsOnArena = arenaDP.getTeamsOnArena()
        group = self.getColorGroup()
        allyColor = self.colors.getSubScheme('flag_team_green', group)['rgba']
        enemyColor = self.colors.getSubScheme('flag_team_red', group)['rgba']
        for teamIdx in teamsOnArena:
            color = allyColor if arenaDP.isAllyTeam(teamIdx) else enemyColor
            BigWorld.wg_setFlagColor(teamIdx, color / 255)

    def __set3DFlagsEmblem(self):
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP is None:
            return
        else:
            teamsOnArena = arenaDP.getTeamsOnArena()
            for teamIdx in [0] + teamsOnArena:
                BigWorld.wg_setFlagEmblem(teamIdx, BigWorld.wg_defaultFlagEmblemPath, BigWorld.wg_defaultFlagEmblemCoords)

            return

    def __onTeamChanged(self, teamID):
        self.__set3DFlagsColors()
