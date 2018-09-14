# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/MinimapLobby.py
import Math
import ArenaType
from gui.Scaleform.daapi.view.meta.MinimapLobbyMeta import MinimapLobbyMeta

class MinimapLobby(MinimapLobbyMeta):
    MINIMAP_SIZE = 300

    def __init__(self):
        super(MinimapLobby, self).__init__()
        self.__playerTeam = 1
        self.__arenaTypeID = None
        self.__cfg = dict()
        return

    def _populate(self):
        super(MinimapLobby, self)._populate()
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged += self.onSettingsChanging

    def _dispose(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.onSettingsChanging
        super(MinimapLobby, self)._dispose()

    def onSettingsChanging(self, diff):
        if 'isColorBlind' in diff:
            self.as_updatePointsS()

    def setMap(self, arenaID):
        self.setArena(arenaID)

    def swapTeams(self, team):
        doBuild = False
        if not team:
            team = 1
        if team is not self.__playerTeam:
            self.__playerTeam = team
            doBuild = True
        if doBuild and self.__arenaTypeID is not None:
            self.build()
        return

    def setArena(self, arenaTypeID):
        self.__arenaTypeID = int(arenaTypeID)
        arenaType = ArenaType.g_cache[self.__arenaTypeID]
        self.__cfg['texture'] = '../../gui/maps/icons/map/%s.png' % arenaType.geometryName
        self.__cfg['size'] = arenaType.boundingBox
        self.__cfg['teamBasePositions'] = arenaType.teamBasePositions
        self.__cfg['teamSpawnPoints'] = arenaType.teamSpawnPoints
        self.__cfg['controlPoints'] = arenaType.controlPoints
        self.build()

    def build(self):
        self.as_clearS()
        self.as_changeMapS(self.__cfg['texture'])
        bottomLeft, upperRight = self.__cfg['size']
        mapWidth, mapHeight = (upperRight - bottomLeft) / self.MINIMAP_SIZE
        viewpoint = (upperRight + bottomLeft) * 0.5
        for team, teamSpawnPoints in enumerate(self.__cfg['teamSpawnPoints'], 1):
            for spawn, spawnPoint in enumerate(teamSpawnPoints, 1):
                pos = (spawnPoint[0], 0, spawnPoint[1])
                m = Math.Matrix().setTranslate(pos)
                self.as_addPointS(pos[0] / mapWidth - viewpoint.x * 0.5, pos[2] / mapHeight - viewpoint.y * 0.5, 'spawn', 'blue' if team == self.__playerTeam else 'red', spawn + 1 if len(teamSpawnPoints) > 1 else 1)

        for team, teamBasePoints in enumerate(self.__cfg['teamBasePositions'], 1):
            for baseNumber, basePoint in enumerate(teamBasePoints.values(), 2):
                pos = (basePoint[0], 0, basePoint[1])
                m = Math.Matrix().setTranslate(pos)
                self.as_addPointS(pos[0] / mapWidth - viewpoint.x * 0.5, pos[2] / mapHeight - viewpoint.y * 0.5, 'base', 'blue' if team == self.__playerTeam else 'red', baseNumber if len(teamBasePoints) > 1 else 1)

        if self.__cfg['controlPoints']:
            for index, controlPoint in enumerate(self.__cfg['controlPoints'], 2):
                pos = (controlPoint[0], 0, controlPoint[1])
                m = Math.Matrix().setTranslate(pos)
                self.as_addPointS(pos[0] / mapWidth - viewpoint.x * 0.5, pos[2] / mapHeight - viewpoint.y * 0.5, 'control', 'empty', index if len(self.__cfg['controlPoints']) > 1 else 1)
