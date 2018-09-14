# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/ColorSchemeManager.py
import BigWorld
import Math
from gui.battle_control import g_sessionProvider
from gui.Scaleform.framework.entities.abstract.ColorSchemeManagerMeta import ColorSchemeManagerMeta
from gui.doc_loaders import GuiColorsLoader

class ColorSchemeManager(ColorSchemeManagerMeta):

    def __init__(self):
        super(ColorSchemeManager, self).__init__()
        self.colors = GuiColorsLoader.load()

    def getColorGroup(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        return 'color_blind' if g_settingsCore.getSetting('isColorBlind') else 'default'

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

    def update(self):
        self.as_updateS()

    def _populate(self):
        super(ColorSchemeManager, self)._populate()
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged += self.__onAccountSettingsChange

    def _dispose(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.__onAccountSettingsChange
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


class BattleColorSchemeManager(ColorSchemeManager):

    def update(self):
        super(BattleColorSchemeManager, self).update()
        self.__set3DFlagsColors()

    def _populate(self):
        super(BattleColorSchemeManager, self)._populate()
        self.__set3DFlagsColors()
        self.__set3DFlagsEmblem()

    def __set3DFlagsColors(self):
        arenaDP = g_sessionProvider.getArenaDP()
        teamsOnArena = arenaDP.getTeamsOnArena()
        group = self.getColorGroup()
        allyColor = self.colors.getSubScheme('flag_team_green', group)['rgba']
        enemyColor = self.colors.getSubScheme('flag_team_red', group)['rgba']
        for teamIdx in teamsOnArena:
            color = allyColor if arenaDP.isAllyTeam(teamIdx) else enemyColor
            BigWorld.wg_setFlagColor(teamIdx, color / 255)

    def __set3DFlagsEmblem(self):
        arenaDP = g_sessionProvider.getArenaDP()
        teamsOnArena = arenaDP.getTeamsOnArena()
        for teamIdx in [0] + teamsOnArena:
            BigWorld.wg_setFlagEmblem(teamIdx, 'system/maps/wg_emblem.dds', Math.Vector4(0.0, 0.1, 0.5, 0.9))
