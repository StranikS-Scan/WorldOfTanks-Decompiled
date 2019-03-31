# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Minimap.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld, Math, ResMgr
from gui.BattleContext import g_battleContext, PLAYER_ENTITY_NAME
from gui.Scaleform.utils.sound import Sound
from gui.Scaleform import FEATURES
from functools import partial
from weakref import proxy
from helpers.gui_utils import *
from debug_utils import *
import string, CommandMapping
from items.vehicles import VEHICLE_CLASS_TAGS
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.utils.functions import getArenaSubTypeID

class VehicleLocation():
    AOI = 0
    FAR = 1
    AOI_TO_FAR = 2


class Minimap(object):
    __MINIMAP_SIZE = (210, 210)
    __MINIMAP_CELLS = (10, 10)
    __AOI_ESTIMATE = 450.0
    __AOI_TO_FAR_TIME = 5.0

    def __init__(self, parentUI):
        self.proxy = proxy(self)
        self.__cfg = dict()
        player = BigWorld.player()
        arena = player.arena
        arenaSubTypeId = getArenaSubTypeID(player.arenaTypeID)
        minimapConfig = arena.typeDescriptor.gameplayTypes.get(arenaSubTypeId, {})
        self.__cfg['texture'] = minimapConfig.get('minimap', BigWorld.player().arena.typeDescriptor.defaultMinimap)
        self.__cfg['teamBasePositions'] = minimapConfig.get('teamBasePositions', tuple())
        self.__cfg['teamSpawnPoints'] = minimapConfig.get('teamSpawnPoints', tuple())
        self.__cfg['controlPoint'] = minimapConfig.get('controlPoint', tuple())
        self.__points = {'base': {},
         'spawn': {}}
        self.__entries = {}
        self.__main = None
        self.__vehiclesWaitStart = []
        self.__isStarted = False
        self.__parentUI = parentUI
        self.__ownUI = None
        self.__ownEntry = dict()
        self.__aoiToFarCallbacks = dict()
        self.__enemyEntries = {}
        self.__sndAttention = Sound('/GUI/notifications_FX/minimap_attention')
        self.__isFirstEnemyMarked = False
        self.__checkEnemyLengthID = None
        self.zIndexManager = MinimapZIndexManager()
        return

    def __del__(self):
        LOG_DEBUG('Minimap deleted')

    def start(self):
        self.__ownUI = GUI.WGMinimapFlash(self.__parentUI.movie)
        self.__ownUI.wg_inputKeyMode = 2
        self.__parentUI.component.addChild(self.__ownUI, 'minimap')
        self.__ownUI.mapSize = Math.Vector2(self.__MINIMAP_SIZE)
        bl, tr = BigWorld.player().arena.typeDescriptor.boundingBox
        self.__ownUI.setArenaBB(bl, tr)
        tex = BigWorld.PyTextureProvider(self.__cfg['texture'])
        self.__ownUI.setBackground(tex)
        self.__cameraHandle = None
        self.__resetCamera('arcade')
        BigWorld.player().inputHandler.onCameraChanged += self.__resetCamera
        self.__parentUI.addExternalCallbacks({'minimap.onClick': self._onMapClicked,
         'minimap.playAttantion': self._playAttention,
         'minimap.setSize': self.onSetSize})
        player = BigWorld.player()
        self.__playerTeam = player.team
        self.__playerVehicleID = player.playerVehicleID
        arena = player.arena
        arena.onPositionsUpdated += self.__onFarPosUpdated
        arena.onNewVehicleListReceived += self.__validateEntries
        arena.onVehicleKilled += self.__onVehicleKilled
        arena.onVehicleAdded += self.__onVehicleAdded
        arena.onTeamKiller += self.__onTeamKiller
        self.__marks = {}
        mp = Math.WGCombinedMP()
        mp.translationSrc = BigWorld.player().getOwnVehicleMatrix()
        mp.rotationSrc = BigWorld.camera().invViewMatrix
        self.__ownEntry['handle'] = self.__ownUI.addEntry(mp, self.zIndexManager.getIndexByName('self'))
        self.__ownEntry['matrix'] = player.getOwnVehicleMatrix()
        self.__ownEntry['location'] = None
        self.__isStarted = True
        for id in self.__vehiclesWaitStart:
            self.notifyVehicleStart(id)

        self.__vehiclesWaitStart = []
        AccountSettings.onSettingsChanging += self.setupMinimapSettings
        self.setupMinimapSettings()
        self.setTeamPoints()
        return

    def setupMinimapSettings(self, name=None):
        if name == 'minimapSize' or name is None:
            self.__parentUI.call('minimap.setupSize', [AccountSettings.getSettings('minimapSize')])
        if name == 'minimapAlpha' or name is None:
            self.__parentUI.call('minimap.setupAlpha', [AccountSettings.getSettings('minimapAlpha')])
        return

    def setTeamPoints(self):
        if self.__cfg['teamBasePositions'] or self.__cfg['teamSpawnPoints'] or self.__cfg['controlPoint'] != tuple():
            arenaDesc = BigWorld.player().arena.typeDescriptor
            bottomLeft, upperRight = arenaDesc.boundingBox
            viewpoint = (upperRight + bottomLeft) * 0.5
            viewpointTranslate = Math.Matrix()
            viewpointTranslate.setTranslate((viewpoint.x, 0.0, viewpoint.y))
            for team, teamSpawnPoints in enumerate(self.__cfg['teamSpawnPoints'], 1):
                self.__points['spawn'][team] = {}
                for spawn, spawnPoint in enumerate(teamSpawnPoints, 1):
                    pos = (spawnPoint[0], 0, spawnPoint[1])
                    m = Math.Matrix()
                    m.setTranslate(Math.Matrix(viewpointTranslate).applyPoint(pos))
                    self.__points['spawn'][team][spawn] = self.__ownUI.addEntry(m, self.zIndexManager.getTeamPointIndex())
                    self.__ownUI.entryInvoke(self.__points['spawn'][team][spawn], ('init', ['points',
                      'spawn',
                      'blue' if team == 1 else 'red',
                      spawn]))

            for team, teamBasePoints in enumerate(self.__cfg['teamBasePositions'], 1):
                self.__points['base'][team] = {}
                for base, basePoint in teamBasePoints.items():
                    pos = (basePoint[0], 0, basePoint[1])
                    m = Math.Matrix()
                    m.setTranslate(Math.Matrix(viewpointTranslate).applyPoint(pos))
                    self.__points['base'][team][base] = self.__ownUI.addEntry(m, self.zIndexManager.getTeamPointIndex())
                    self.__ownUI.entryInvoke(self.__points['base'][team][base], ('init', ['points',
                      'base',
                      'blue' if team == 1 else 'red',
                      len(self.__points['base'][team]) + 1 if len(teamBasePoints) > 1 else 1]))

            if self.__cfg['controlPoint'] != tuple():
                pos = (self.__cfg['controlPoint'][0], 0, self.__cfg['controlPoint'][1])
                m = Math.Matrix()
                m.setTranslate(Math.Matrix(viewpointTranslate).applyPoint(pos))
                self.__points['control'] = self.__ownUI.addEntry(m, self.zIndexManager.getTeamPointIndex())
                self.__ownUI.entryInvoke(self.__points['control'], ('init', ['points',
                  'control',
                  'empty',
                  1]))

    def onSetSize(self, calbackID, index):
        AccountSettings.setSettings('minimapSize', int(index))

    def destroy(self):
        if not self.__isStarted:
            self.__vehiclesWaitStart = []
            return
        else:
            while 1:
                if len(self.__aoiToFarCallbacks):
                    _, callbackID = self.__aoiToFarCallbacks.popitem()
                    callbackID is not None and BigWorld.cancelCallback(callbackID)

            self.__isStarted = False
            self.__entries = None
            self.__cameraHandle = None
            self.__marks = None
            setattr(self.__parentUI.component, 'minimap', None)
            AccountSettings.onSettingsChanging -= self.setupMinimapSettings
            self.__parentUI = None
            return

    def prerequisites(self):
        return []

    def setVisible(self, visible):
        pass

    def notifyVehicleStop(self, vehicleId):
        if not self.__isStarted:
            if vehicleId in self.__vehiclesWaitStart:
                self.__vehiclesWaitStart.remove(vehicleId)
            return
        elif vehicleId == self.__playerVehicleID:
            return
        else:
            info = BigWorld.player().arena.vehicles.get(vehicleId)
            if info is None or not info['isAlive']:
                return
            entries = self.__entries
            if vehicleId in entries:
                location = entries[vehicleId]['location']
                if location == VehicleLocation.AOI:
                    ownPos = Math.Matrix(BigWorld.camera().invViewMatrix).translation
                    entryPos = Math.Matrix(entries[vehicleId]['matrix']).translation
                    inAoI = bool(abs(ownPos.x - entryPos.x) < self.__AOI_ESTIMATE and abs(ownPos.z - entryPos.z) < self.__AOI_ESTIMATE)
                    self.__delEntry(vehicleId)
                    if not inAoI:
                        self.__addEntry(vehicleId, VehicleLocation.AOI_TO_FAR)
                else:
                    LOG_DEBUG('notifyVehicleOnStop, unknown minimap entry location', location)
            return

    def notifyVehicleStart(self, vehicleId):
        if not self.__isStarted:
            self.__vehiclesWaitStart.append(vehicleId)
            return
        elif vehicleId == self.__playerVehicleID:
            return
        else:
            info = BigWorld.player().arena.vehicles.get(vehicleId)
            if info is None or not info['isAlive']:
                return
            entries = self.__entries
            if vehicleId in entries:
                self.__delEntry(vehicleId)
            self.__addEntry(vehicleId, VehicleLocation.AOI)
            return

    def _playAttention(self, _):
        self.__sndAttention.play()

    def markCell(self, cellIndexes, duration):
        if not self.__isStarted:
            return
        if cellIndexes < 0:
            return
        columnCount, rowCount = Minimap.__MINIMAP_CELLS
        column = cellIndexes / columnCount % columnCount
        row = cellIndexes % columnCount
        if self.__marks.has_key(cellIndexes):
            BigWorld.cancelCallback(self.__marks[cellIndexes][1])
            self._removeCellMark(cellIndexes)
        arenaDesc = BigWorld.player().arena.typeDescriptor
        bottomLeft, upperRight = arenaDesc.boundingBox
        viewpoint = (upperRight + bottomLeft) * 0.5
        viewpointTranslate = Math.Matrix()
        viewpointTranslate.setTranslate((viewpoint.x, 0.0, viewpoint.y))
        spaceSize = upperRight - bottomLeft
        pos = (column * spaceSize[0] / columnCount - spaceSize[0] * 0.5, 0, -row * spaceSize[1] / rowCount + spaceSize[0] * 0.5)
        m = Math.Matrix()
        m.setTranslate(Math.Matrix(viewpointTranslate).applyPoint(pos))
        mark = self.__ownUI.addEntry(m, self.zIndexManager.getIndexByName('cell'))
        self.__ownUI.entryInvoke(mark, ('gotoAndStop', ['cellFlash']))
        callbackID = BigWorld.callback(duration, partial(self._removeCellMark, cellIndexes))
        self.__marks[cellIndexes] = (mark, callbackID)

    def getCellName(self, cellIndexes):
        columnCount, rowCount = Minimap.__MINIMAP_CELLS
        column = cellIndexes / columnCount % columnCount
        row = cellIndexes % columnCount
        if row < 8:
            name = string.ascii_uppercase[row]
        else:
            name = string.ascii_uppercase[row + 1]
        name += str((column + 1) % 10)
        return name

    def _removeCellMark(self, cellIndexes):
        if self.__isStarted:
            mark = self.__marks[cellIndexes][0]
            del self.__marks[cellIndexes]
            self.__ownUI.delEntry(mark)

    def _onMapClicked(self, _, x, y, bHighlightCellNVehicleSpecific=True):
        localPos = (x, y)
        mapSize = Minimap.__MINIMAP_SIZE
        player = BigWorld.player()
        if bHighlightCellNVehicleSpecific:
            cellCount = Minimap.__MINIMAP_CELLS
            row = int(cellCount[0] * localPos[0] / mapSize[0])
            column = int(cellCount[1] * localPos[1] / mapSize[1])
            player.onMinimapCellClicked(row * int(cellCount[1]) + column)
        elif 'SPG' in player.vehicleTypeDescriptor.type.tags:
            arenaDesc = BigWorld.player().arena.typeDescriptor
            bottomLeft, upperRight = arenaDesc.boundingBox
            spaceSize = upperRight - bottomLeft
            viewpoint = (upperRight + bottomLeft) * 0.5
            viewpointTranslate = Math.Matrix()
            viewpointTranslate.setTranslate((viewpoint.x, 0.0, viewpoint.y))
            pos = ((localPos[0] - mapSize[0] * 0.5) / mapSize[0], (localPos[1] - mapSize[1] * 0.5) / mapSize[1])
            worldPos = Math.Matrix(viewpointTranslate).applyPoint((pos[0] * spaceSize[0], 0.0, -pos[1] * spaceSize[1]))
            player.inputHandler.onMinimapClicked(worldPos)

    def __onVehicleAdded(self, id):
        arena = BigWorld.player().arena
        if not arena.vehicles[id]['isAlive']:
            return
        else:
            location = self.__detectLocation(id)
            if location is not None:
                self.__addEntry(id, location)
            return

    def __onTeamKiller(self, id):
        self.__callEntryFlash(id, 'setEntryName', [PLAYER_ENTITY_NAME.teamKiller.name()])

    def __onVehicleRemoved(self, id):
        if self.__entries.has_key(id):
            self.__delEntry(id)

    def __onVehicleKilled(self, victimId, killerID, reason):
        if self.__entries.has_key(victimId):
            self.__delEntry(victimId)

    def __onFarPosUpdated(self):
        entries = self.__entries
        arena = BigWorld.player().arena
        vehicles = arena.vehicles
        for id, pos in arena.positions.iteritems():
            entry = entries.get(id)
            if entry is not None:
                location = entry['location']
                if location == VehicleLocation.FAR:
                    entry['matrix'].setTranslate(pos)
                elif location == VehicleLocation.AOI_TO_FAR:
                    self.__delEntry(id)
                    self.__addEntry(id, VehicleLocation.FAR)
            elif vehicles[id]['isAlive']:
                self.__addEntry(id, VehicleLocation.FAR)

        for id in set(entries).difference(set(arena.positions)):
            location = entries[id]['location']
            if location == VehicleLocation.FAR:
                self.__delEntry(id)
            elif location == VehicleLocation.AOI_TO_FAR:
                self.__delEntry(id)

        return

    def __validateEntries(self):
        entrySet = set(self.__entries.iterkeys())
        vehiclesSet = set(BigWorld.player().arena.vehicles.iterkeys())
        playerOnlySet = set((self.__playerVehicleID,))
        for id in vehiclesSet.difference(entrySet) - playerOnlySet:
            self.__onVehicleAdded(id)

        for id in entrySet.difference(vehiclesSet) - playerOnlySet:
            self.__onVehicleRemoved(id)

    def __detectLocation(self, id):
        vehicle = BigWorld.entities.get(id)
        if vehicle is not None and vehicle.isStarted:
            return VehicleLocation.AOI
        elif BigWorld.player().arena.positions.has_key(id):
            return VehicleLocation.FAR
        else:
            return
            return

    def __delEntry(self, id, inCallback=False):
        entry = self.__entries.get(id)
        if entry is None:
            return
        else:
            self.__ownUI.delEntry(entry['handle'])
            if entry.get('location') == VehicleLocation.AOI_TO_FAR:
                callbackId = self.__aoiToFarCallbacks.pop(id, None)
                if callbackId is not None:
                    BigWorld.cancelCallback(callbackId)
            self.__entries.pop(id)
            if id in self.__enemyEntries:
                self.__enemyEntries.pop(id)
                if not len(self.__enemyEntries):
                    if self.__checkEnemyLengthID:
                        BigWorld.cancelCallback(self.__checkEnemyLengthID)
                    self.__checkEnemyLengthID = BigWorld.callback(5, self.__checkEnemyLength)
            return

    def __checkEnemyLength(self):
        self.__checkEnemyLengthID = None
        self.__isFirstEnemyMarked = not len(self.__enemyEntries) == 0
        return

    def __addEntry(self, id, location):
        arena = BigWorld.player().arena
        entry = dict()
        matrix = None
        if location == VehicleLocation.AOI:
            matrix = BigWorld.entities[id].matrix
        elif location == VehicleLocation.AOI_TO_FAR:
            matrix = Math.Matrix(BigWorld.entities[id].matrix)
        elif location == VehicleLocation.FAR:
            matrix = Math.Matrix()
            pos = arena.positions[id]
            matrix.setTranslate(pos)
        m = Math.WGTranslationOnlyMP()
        m.source = matrix
        if location == VehicleLocation.AOI_TO_FAR:
            self.__aoiToFarCallbacks[id] = BigWorld.callback(self.__AOI_TO_FAR_TIME, partial(self.__delEntry, id))
        entry['location'] = location
        entry['matrix'] = matrix
        entry['handle'] = self.__ownUI.addEntry(m, self.zIndexManager.getVehicleIndex(id))
        self.__entries[id] = entry
        entryVehicle = arena.vehicles[id]
        entityName = g_battleContext.getPlayerEntityName(id, entryVehicle)
        markerType = entityName.base
        entryName = entityName.name()
        markMarker = ''
        if not entityName.isFriend:
            if not self.__isFirstEnemyMarked and not len(self.__enemyEntries):
                self.__isFirstEnemyMarked = True
                markMarker = 'firstEnemy'
            self.__enemyEntries[id] = entry
        if entryVehicle['vehicleType'] is not None:
            tags = set(entryVehicle['vehicleType'].type.tags & VEHICLE_CLASS_TAGS)
        else:
            LOG_ERROR('Try to show minimap marker without vehicle info.')
            return
        vClass = tags.pop() if len(tags) > 0 else ''
        self.__callEntryFlash(id, 'init', [markerType,
         entryName,
         vClass,
         markMarker])
        return

    def updateEntries(self):
        for id in self.__entries:
            self.__callEntryFlash(id, 'update')

    def __callEntryFlash(self, id, methodName, args=None):
        if not self.__isStarted:
            return
        else:
            if args is None:
                args = []
            if self.__entries.has_key(id):
                self.__ownUI.entryInvoke(self.__entries[id]['handle'], (methodName, args))
            elif id == BigWorld.player().playerVehicleID:
                if self.__ownEntry.has_key('handle'):
                    self.__ownUI.entryInvoke(self.__ownEntry['handle'], (methodName, args))
            return

    def __resetCamera(self, mode, vehicleId=None):
        if self.__cameraHandle is not None:
            self.__ownUI.delEntry(self.__cameraHandle)
        if mode == 'strategic':
            m = Math.WGTranslationOnlyMP()
            m.source = BigWorld.camera().invViewMatrix
        elif mode == 'arcade' or mode == 'sniper':
            m = Math.WGCombinedMP()
            m.translationSrc = BigWorld.player().getOwnVehicleMatrix()
            m.rotationSrc = BigWorld.camera().invViewMatrix
        elif mode == 'postmortem':
            m = Math.WGCombinedMP()
            if vehicleId is not None:
                translationSrc = Math.WGTranslationOnlyMP()
                translationSrc.source = BigWorld.entities[vehicleId].matrix
            else:
                translationSrc = BigWorld.player().getOwnVehicleMatrix()
            m.translationSrc = translationSrc
            m.rotationSrc = BigWorld.camera().invViewMatrix
        else:
            m = BigWorld.camera().invViewMatrix
        self.__cameraHandle = self.__ownUI.addEntry(m, self.zIndexManager.getIndexByName('cameraStrategic' if mode == 'strategic' else 'cameraNormal'))
        self.__ownUI.entryInvoke(self.__cameraHandle, ('gotoAndStop', ['cursorStrategic' if mode == 'strategic' else 'cursorNormal']))
        playerMarker = 'normal'
        if mode == 'strategic':
            playerMarker = 'strategic'
        if mode == 'postmortem':
            if vehicleId is not None and vehicleId != BigWorld.player().playerVehicleID:
                playerMarker = 'strategic'
            elif self.__ownEntry.has_key('handle'):
                mp = Math.WGCombinedMP()
                mp.translationSrc = BigWorld.player().getOwnVehicleMatrix()
                mp.rotationSrc = BigWorld.camera().invViewMatrix
                self.__ownUI.entrySetMatrix(self.__ownEntry['handle'], mp)
        self.__callEntryFlash(BigWorld.player().playerVehicleID, 'init', ['player', playerMarker])
        return

    def handleKey(self, key):
        if FEATURES.MINIMAP_SIZE:
            cmdMap = CommandMapping.g_instance
            if cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_DOWN, key):
                self.__parentUI.call('minimap.sizeDown', [])
            elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_UP, key):
                self.__parentUI.call('minimap.sizeUp', [])
            elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_VISIBLE, key):
                self.__parentUI.call('minimap.visible', [])

    def showActionMarker(self, vehicleID, newState):
        self.__callEntryFlash(vehicleID, 'showAction', [newState])


class MinimapZIndexManager(object):
    _VEHICLE_RANGE = (50, 99)
    _FIXED_INDEXES = {'cameraNormal': 40,
     'self': 100,
     'cameraStrategic': 101,
     'cell': 102}

    def __init__(self):
        self.__indexes = {}
        self.__lastPointIndex = 0
        self.__lastVehIndex = MinimapZIndexManager._VEHICLE_RANGE[0]

    def getTeamPointIndex(self):
        self.__lastPointIndex += 1
        return self.__lastPointIndex

    def getVehicleIndex(self, id):
        if not self.__indexes.has_key(id):
            self.__indexes[id] = self.__lastVehIndex
            self.__lastVehIndex += 1
        return self.__indexes[id]

    def getIndexByName(self, name):
        return MinimapZIndexManager._FIXED_INDEXES[name]
