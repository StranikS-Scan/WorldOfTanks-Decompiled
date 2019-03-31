# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/MinimapLobby.py
# Compiled at: 2011-09-08 15:19:19
import Math, GUI, BigWorld
import ArenaType
from gui.Scaleform.utils.functions import getArenaSubTypeID

class MinimapLobby(object):

    def __init__(self, parentUI):
        self.__parentUI = parentUI
        self.arenaType = None
        self.__cfg = dict()
        return

    def start(self):
        self.__parentUI.addExternalCallbacks({'minimap.onChange': self.onChange})

    def destroy(self):
        self.__parentUI.removeExternalCallbacks('minimap.onChange')
        self.__parentUI = None
        return

    def onChange(self, callbackID, arenaTypeID):
        self.setArena(arenaTypeID)

    def setArena(self, arenaTypeID):
        arenaTypeID = int(arenaTypeID)
        arenaType = ArenaType.g_cache.get(arenaTypeID)
        arenaSubTypeId = getArenaSubTypeID(arenaTypeID)
        minimapConfig = arenaType.gameplayTypes.get(arenaSubTypeId, {})
        self.__cfg['texture'] = '../../gui/maps/icons/map/%s.tga' % arenaType.typeName
        self.__cfg['textureClean'] = '../../gui/maps/icons/map/%s_clean.tga' % arenaType.typeName
        self.__cfg['size'] = arenaType.boundingBox
        self.__cfg['teamBasePositions'] = minimapConfig.get('teamBasePositions', tuple())
        self.__cfg['teamSpawnPoints'] = minimapConfig.get('teamSpawnPoints', tuple())
        self.__cfg['controlPoint'] = minimapConfig.get('controlPoint', tuple())
        self.build()

    def build(self):
        self.__parentUI.call('minimap.clear', list())
        bottomLeft, upperRight = self.__cfg['size']
        if self.__cfg['teamBasePositions'] or self.__cfg['teamSpawnPoints'] or self.__cfg['controlPoint'] != tuple():
            self.__parentUI.call('minimap.changeMap', [self.__cfg['textureClean']])
            mapWidth, mapHeight = (upperRight - bottomLeft) / 300
            viewpoint = (upperRight + bottomLeft) * 0.5
            viewpointTranslate = Math.Matrix()
            viewpointTranslate.setTranslate((viewpoint.x, 0.0, viewpoint.y))
            for team, teamBasePoints in enumerate(self.__cfg['teamSpawnPoints'], 1):
                for spawn, spawnPoint in enumerate(teamBasePoints, 1):
                    pos = (spawnPoint[0], 0, spawnPoint[1])
                    m = Math.Matrix(viewpointTranslate).applyPoint(pos)
                    self.__parentUI.call('minimap.addPoint', [m[0] / mapWidth,
                     m[2] / mapHeight,
                     'spawn',
                     'blue' if team == 1 else 'red',
                     spawn])

            for team, teamBasePoints in enumerate(self.__cfg['teamBasePositions'], 1):
                for baseNumber, basePoint in enumerate(teamBasePoints.values(), 2):
                    pos = (basePoint[0], 0, basePoint[1])
                    m = Math.Matrix(viewpointTranslate).applyPoint(pos)
                    self.__parentUI.call('minimap.addPoint', [m[0] / mapWidth,
                     m[2] / mapHeight,
                     'base',
                     'blue' if team == 1 else 'red',
                     baseNumber if len(teamBasePoints) > 1 else 1])

            if self.__cfg['controlPoint'] != tuple():
                pos = (self.__cfg['controlPoint'][0], 0, self.__cfg['controlPoint'][1])
                m = Math.Matrix(viewpointTranslate).applyPoint(pos)
                self.__parentUI.call('minimap.addPoint', [m[0] / mapWidth,
                 m[2] / mapHeight,
                 'control',
                 'empty',
                 1])
        else:
            self.__parentUI.call('minimap.changeMap', [self.__cfg['texture']])
