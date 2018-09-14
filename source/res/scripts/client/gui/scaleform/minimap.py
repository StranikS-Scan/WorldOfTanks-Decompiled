# Embedded file name: scripts/client/gui/Scaleform/Minimap.py
import string
import math
from functools import partial
from weakref import proxy
import BigWorld
import Math
import CommandMapping
import Keys
from CTFManager import g_ctfManager
from battleground.gas_attack import gasAttackManager
from constants import REPAIR_POINT_ACTION, RESOURCE_POINT_STATE, FLAG_STATE, AOI
from gui.battle_control.avatar_getter import getPlayerVehicleID
from gui.battle_control.dyn_squad_functional import IDynSquadEntityClient
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from ids_generators import SequenceIDGenerator
from messenger import MessengerEntry
from AvatarInputHandler import mathUtils
from shared_utils import findFirst
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS, FEEDBACK_EVENT_ID, NEUTRAL_TEAM
from gui.battle_control.arena_info import isLowLevelBattle, hasFlags, hasRepairPoints, hasResourcePoints, getIsMultiteam, hasGasAttack
import FMOD
import SoundGroups
from gui import GUI_SETTINGS, g_repeatKeyHandlers
from helpers.gui_utils import *
from debug_utils import *
from account_helpers.AccountSettings import AccountSettings
from gui.battle_control import vehicle_getter
from battleground.gas_attack import _getDefaultScenario
from time import time
CURSOR_NORMAL = 'cursorNormal'
CURSOR_NORMAL_WITH_DIRECTION = 'cursorNormalWithDirection'
CURSOR_STRATEGIC = 'cursorStrategic'
CAMERA_NORMAL = 'cameraNormal'
CAMERA_VIDEO = 'cameraVideo'
CAMERA_STRATEGIC = 'cameraStrategic'
MARKER = 'marker'
MODE_VIDEO = 'video'
MODE_POSTMORTEM = 'postmortem'
MODE_SNIPER = 'sniper'
MODE_ARCADE = 'arcade'
MODE_STRATEGIC = 'strategic'
MODE_BATTLE_CONSUME = 'mapcase'

def _isStrategic(ctrlMode):
    return ctrlMode in (MODE_STRATEGIC, MODE_BATTLE_CONSUME)


class VehicleLocation():
    AOI = 0
    FAR = 1
    AOI_TO_FAR = 2


class MARKER_TYPE():
    CONSUMABLE = 'fortConsumables'
    FLAG = 'flags'
    RESOURCE_POINT = 'resourcePoints'


class FLAG_TYPE():
    ALLY = 'ally'
    ENEMY = 'enemy'
    NEUTRAL = 'neutral'
    ALLY_CAPTURE = 'allyCapture'
    ENEMY_CAPTURE = 'enemyCapture'
    ALLY_CAPTURE_ANIMATION = 'allyCaptureAnimation'
    COOLDOWN = 'cooldown'


class RESOURCE_POINT_TYPE():
    CONFLICT = 'conflict'
    COOLDOWN = 'cooldown'
    READY = 'ready'
    OWN_MINING = 'ownMining'
    ENEMY_MINING = 'enemyMining'


_CAPTURE_STATE_BY_TEAMS = {True: RESOURCE_POINT_TYPE.OWN_MINING,
 False: RESOURCE_POINT_TYPE.ENEMY_MINING}
_CAPTURE_FROZEN_STATE_BY_TEAMS = {True: RESOURCE_POINT_TYPE.OWN_MINING,
 False: RESOURCE_POINT_TYPE.ENEMY_MINING}

class Minimap(IDynSquadEntityClient):
    __MINIMAP_SIZE = (210, 210)
    __MINIMAP_CELLS = (10, 10)
    __AOI_ESTIMATE = AOI.VEHICLE_CIRCULAR_AOI_RADIUS - 50.0 if AOI.ENABLE_MANUAL_RULES else 450.0
    __AOI_TO_FAR_TIME = 5.0

    def __init__(self, parentUI):
        self.proxy = proxy(self)
        self.__cfg = dict()
        player = BigWorld.player()
        arena = player.arena
        arenaType = arena.arenaType
        self.__playerTeam = player.team
        self.__playerVehicleID = player.playerVehicleID
        self.__isTeamPlayer = self.__playerTeam in arenaType.squadTeamNumbers if getIsMultiteam(arenaType) else True
        self.__cfg['texture'] = arenaType.minimap
        self.__cfg['teamBasePositions'] = arenaType.teamBasePositions
        if isLowLevelBattle() and self.__playerTeam - 1 in arenaType.teamLowLevelSpawnPoints and len(arenaType.teamLowLevelSpawnPoints[self.__playerTeam - 1]):
            self.__cfg['teamSpawnPoints'] = arenaType.teamLowLevelSpawnPoints
        else:
            self.__cfg['teamSpawnPoints'] = arenaType.teamSpawnPoints
        self.__cfg['controlPoints'] = arenaType.controlPoints
        self.__cfg['repairPoints'] = []
        if hasFlags():
            self.__cfg['flagAbsorptionPoints'] = arenaType.flagAbsorptionPoints
            self.__cfg['flagSpawnPoints'] = arenaType.flagSpawnPoints
        if hasRepairPoints():
            self.__cfg['repairPoints'] = arenaType.repairPoints
        self.__points = {'base': {},
         'spawn': {}}
        self.__backMarkers = {}
        self.__entries = {}
        self.__entrieLits = {}
        self.__entrieMarkers = {}
        self.__vehicleIDToFlagUniqueID = {}
        self.__enemyEntries = {}
        self.__main = None
        self.__vehiclesWaitStart = {}
        self.__isStarted = False
        self.__parentUI = parentUI
        self.__ownUI = None
        self.__ownEntry = {}
        self.__aoiToFarCallbacks = {}
        self.__deadCallbacks = {}
        self.__isFirstEnemyNonSPGMarked = False
        self.__isFirstEnemySPGMarkedById = {}
        self.__checkEnemyNonSPGLengthID = None
        self.__resetSPGMarkerTimoutCbckId = None
        self.zIndexManager = MinimapZIndexManager()
        self.__observedVehicleId = -1
        self.__currentMode = None
        self._actualSize = {'width': 0,
         'height': 0}
        self.__normalMarkerScale = None
        self.__markerScale = None
        self.__markerIDGenerator = None
        self.__settingName = 'minimapSize'
        self.__isShowExtendedInfoActive = False
        self.__updateSettings()
        return

    def __del__(self):
        LOG_DEBUG('Minimap deleted')

    def updateSquadmanVeh(self, vID):
        self.__callEntryFlash(vID, 'setEntryName', [PLAYER_GUI_PROPS.squadman.name()])

    def start(self):
        self.__ownUI = GUI.WGMinimapFlash(self.__parentUI.movie)
        self.__ownUI.wg_inputKeyMode = 2
        self.__parentUI.component.addChild(self.__ownUI, 'minimap')
        self.__ownUI.mapSize = Math.Vector2(self.__MINIMAP_SIZE)
        bl, tr = BigWorld.player().arena.arenaType.boundingBox
        self.__ownUI.setArenaBB(bl, tr)
        player = BigWorld.player()
        tex = BigWorld.PyTextureProvider(self.__cfg['texture'])
        if not self.__ownUI.setBackground(tex):
            LOG_ERROR("Failed to set minimap texture: '%s'" % self.__cfg['texture'])
        self.__cameraHandle = None
        self.__cameraMatrix = None
        player.inputHandler.onCameraChanged += self.__resetCamera
        player.inputHandler.onPostmortemVehicleChanged += self.__clearCamera
        self.__parentUI.addExternalCallbacks({'minimap.onClick': self._onMapClicked,
         'minimap.playAttantion': self._playAttention,
         'minimap.setSize': self.onSetSize,
         'minimap.lightPlayer': self.onLightPlayer,
         'minimap.scaleMarkers': self.onScaleMarkers})
        arena = player.arena
        arena.onPositionsUpdated += self.__onFarPosUpdated
        arena.onNewVehicleListReceived += self.__validateEntries
        arena.onVehicleKilled += self.__onVehicleKilled
        arena.onVehicleAdded += self.__onVehicleAdded
        arena.onTeamKiller += self.__onTeamKiller
        ctrl = g_sessionProvider.getEquipmentsCtrl()
        if ctrl:
            ctrl.onEquipmentMarkerShown += self.__onEquipmentMarkerShown
        ctrl = g_sessionProvider.getFeedback()
        if ctrl:
            ctrl.onMinimapVehicleAdded += self.__onMinimapVehicleAdded
            ctrl.onMinimapVehicleRemoved += self.__onMinimapVehicleRemoved
            ctrl.onMinimapFeedbackReceived += self.__onMinimapFeedbackReceived
        addListener = g_eventBus.addListener
        addListener(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)
        addListener(GameEvent.MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__markerIDGenerator = SequenceIDGenerator()
        isFlagBearer = False
        if hasFlags():
            g_ctfManager.onFlagSpawning += self.__onFlagSpawning
            g_ctfManager.onFlagSpawnedAtBase += self.__onFlagSpawnedAtBase
            g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
            g_ctfManager.onFlagDroppedToGround += self.__onFlagDroppedToGround
            g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
            g_ctfManager.onFlagRemoved += self.__onFlagRemoved
            g_ctfManager.onCarriedFlagsPositionUpdated += self.__onCarriedFlagsPositionUpdated
            for flagID, flagInfo in g_ctfManager.getFlags():
                vehicleID = flagInfo['vehicle']
                if vehicleID is None:
                    if flagInfo['state'] == FLAG_STATE.WAITING_FIRST_SPAWN:
                        self.__onFlagSpawning(flagID, flagInfo['respawnTime'])
                    elif flagInfo['state'] in (FLAG_STATE.ON_GROUND, FLAG_STATE.ON_SPAWN):
                        self.__onFlagSpawnedAtBase(flagID, flagInfo['team'], flagInfo['minimapPos'])
                elif vehicleID == self.__playerVehicleID:
                    isFlagBearer = True

            self.__addFlagCaptureMarkers(isFlagBearer)
        if hasRepairPoints():
            g_sessionProvider.getRepairCtrl().onRepairPointStateChanged += self.__onRepairPointStateChanged
        arenaDP = g_sessionProvider.getArenaDP()
        if hasResourcePoints():
            g_ctfManager.onResPointIsFree += self.__onResPointIsFree
            g_ctfManager.onResPointCooldown += self.__onResPointCooldown
            g_ctfManager.onResPointCaptured += self.__onResPointCaptured
            g_ctfManager.onResPointCapturedLocked += self.__onResPointCapturedLocked
            g_ctfManager.onResPointBlocked += self.__onResPointBlocked
            for pointID, point in g_ctfManager.getResourcePoints():
                pointState = point['state']
                if pointState == RESOURCE_POINT_STATE.FREE:
                    state = RESOURCE_POINT_TYPE.READY
                elif pointState == RESOURCE_POINT_STATE.COOLDOWN:
                    state = RESOURCE_POINT_TYPE.COOLDOWN
                elif pointState == RESOURCE_POINT_STATE.CAPTURED:
                    state = RESOURCE_POINT_TYPE.OWN_MINING if arenaDP.isAllyTeam(point['team']) else RESOURCE_POINT_TYPE.ENEMY_MINING
                else:
                    state = RESOURCE_POINT_TYPE.CONFLICT
                self.__addResourcePointMarker(pointID, point['minimapPos'], state)

        if hasGasAttack():
            g_sessionProvider.getGasAttackCtrl().onPreparing += self.__onGasAttackPreparing
            g_sessionProvider.getGasAttackCtrl().onStarted += self.__onGasAttackStarted
            self.__initGasAttackArea()
        self.__marks = {}
        if not g_sessionProvider.getCtx().isPlayerObserver():
            mp = player.getOwnVehicleMatrix()
            self.__ownEntry['handle'] = self.__ownUI.addEntry(mp, self.zIndexManager.getIndexByName('self'))
            entryName = 'normal'
            self.__ownUI.entryInvoke(self.__ownEntry['handle'], ('init', ['player', entryName + 'Flag' if isFlagBearer else entryName]))
            self.__ownEntry['matrix'] = player.getOwnVehicleMatrix()
            self.__ownEntry['location'] = None
            self.__ownEntry['entryName'] = entryName
        self.__resetCamera(MODE_ARCADE)
        self.__isStarted = True
        for vProxy, vInfo, guiProps in self.__vehiclesWaitStart.itervalues():
            self.notifyVehicleStart(vProxy, vInfo, guiProps)

        self.__vehiclesWaitStart.clear()
        self.__mapSizeIndex = self.getStoredMinimapSize()
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged += self.setupMinimapSettings
        self.setupMinimapSettings()
        self.setTeamPoints()
        g_repeatKeyHandlers.add(self.handleRepeatKeyEvent)
        return

    def __showSector(self):
        vehicle = BigWorld.entity(self.__playerVehicleID)
        vTypeDesc = vehicle.typeDescriptor
        yawLimits = vehicle_getter.getYawLimits(vTypeDesc)
        entryName = 'normalWithSector'
        self.__ownUI.entryInvoke(self.__ownEntry['handle'], ('setEntryName', [entryName + 'Flag' if g_ctfManager.isFlagBearer(self.__playerVehicleID) else entryName]))
        self.__ownEntry['entryName'] = entryName
        self.__ownUI.entryInvoke(self.__ownEntry['handle'], ('showSector', [math.degrees(yawLimits[0]), math.degrees(yawLimits[1])]))

    def __hideSector(self):
        self.__ownUI.entryInvoke(self.__ownEntry['handle'], ('hideSector',))

    def onScaleMarkers(self, callbackID, scale, normalScale):
        self.__markerScale = scale
        self.__normalMarkerScale = normalScale
        bases = self.__points['base']
        for team in bases:
            for base in bases[team]:
                self.scaleMarker(bases[team][base].handle, bases[team][base].matrix, self.__markerScale)

        spawns = self.__points['spawn']
        for team in spawns:
            for spawn in spawns[team]:
                self.scaleMarker(spawns[team][spawn].handle, spawns[team][spawn].matrix, self.__markerScale)

        if 'control' in self.__points:
            controls = self.__points['control']
            for point in controls:
                self.scaleMarker(point.handle, point.matrix, self.__markerScale)

        if 'repair' in self.__points:
            repairs = self.__points['repair']
            for point, pointCooldown in repairs.itervalues():
                self.scaleMarker(point.handle, point.matrix, self.__markerScale)
                self.scaleMarker(pointCooldown.handle, pointCooldown.matrix, self.__markerScale)

        if not _isStrategic(self.__currentMode) and self.__cameraHandle is not None and self.__cameraMatrix is not None:
            self.scaleMarker(self.__cameraHandle, self.__cameraMatrix, self.__markerScale)
            vehicle = BigWorld.entity(self.__playerVehicleID)
            if vehicle is not None and vehicle.isAlive() and GUI_SETTINGS.showDirectionLine and self.__showDirectionLine:
                self.__ownUI.entryInvoke(self.__cameraHandle, ('updateLinesScale', [self.__normalMarkerScale]))
        if 'handle' in self.__ownEntry:
            self.scaleMarker(self.__ownEntry['handle'], self.__ownEntry['matrix'], self.__markerScale)
            if self.isSpg() and GUI_SETTINGS.showSectorLines and self.__showSectorLine:
                self.__ownUI.entryInvoke(self.__ownEntry['handle'], ('updateLinesScale', [self.__normalMarkerScale]))
        for id in self.__entries:
            originalMatrix = self.__entries[id]['matrix']
            handle = self.__entries[id]['handle']
            self.scaleMarker(handle, originalMatrix, self.__markerScale)

        for id in self.__entrieLits:
            originalMatrix = self.__entrieLits[id]['matrix']
            handle = self.__entrieLits[id]['handle']
            self.scaleMarker(handle, originalMatrix, self.__markerScale)

        for item in self.__entrieMarkers.itervalues():
            originalMatrix = item['matrix']
            handle = item['handle']
            self.scaleMarker(handle, originalMatrix, self.__markerScale)

        return

    def scaleMarker(self, handle, originalMatrix, scale):
        if handle is not None and originalMatrix is not None:
            scaleMatrix = Math.Matrix()
            scaleMatrix.setScale(Math.Vector3(scale, scale, scale))
            mp = mathUtils.MatrixProviders.product(scaleMatrix, originalMatrix)
            self.__ownUI.entrySetMatrix(handle, mp)
        return

    def getStoredMinimapSize(self):
        return AccountSettings.getSettings(self.__settingName)

    def storeMinimapSize(self):
        AccountSettings.setSettings(self.__settingName, self.__mapSizeIndex)

    def useRespawnSize(self):
        self.storeMinimapSize()
        self.__settingName = 'minimapRespawnSize'
        self.__parentUI.call('minimap.setupSize', [self.getStoredMinimapSize()])

    def useNormalSize(self):
        self.storeMinimapSize()
        self.__settingName = 'minimapSize'
        self.__parentUI.call('minimap.setupSize', [self.getStoredMinimapSize()])

    def getStoredMinimapAlpha(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        return g_settingsCore.getSetting('minimapAlpha')

    def setupMinimapSettings(self, diff = None):
        from account_helpers.settings_core import settings_constants
        if diff is None or self.__settingName in diff:
            self.__parentUI.call('minimap.setupSize', [self.getStoredMinimapSize()])
        if diff is None or settings_constants.GAME.MINIMAP_ALPHA in diff:
            self.__parentUI.call('minimap.setupAlpha', [self.getStoredMinimapAlpha()])
        if diff is None or {settings_constants.GAME.SHOW_VEH_MODELS_ON_MAP, settings_constants.GAME.SHOW_SECTOR_ON_MAP, settings_constants.GAME.SHOW_VECTOR_ON_MAP} & set(diff.keys()):
            self.__updateSettings()
            if diff is None or settings_constants.GAME.SHOW_VEH_MODELS_ON_MAP in diff:
                self.showVehicleNames(self.__permanentNamesShow)
            if diff is None or settings_constants.GAME.SHOW_VECTOR_ON_MAP in diff:
                vehicle = BigWorld.entity(self.__playerVehicleID)
                if GUI_SETTINGS.showDirectionLine and not _isStrategic(self.__currentMode) and vehicle is not None and vehicle.isAlive() and not g_sessionProvider.getCtx().isPlayerObserver():
                    if self.__showDirectionLine:
                        self.__ownUI.entryInvoke(self.__cameraHandle, ('showCameraDirectionLine', ()))
                    else:
                        self.__ownUI.entryInvoke(self.__cameraHandle, ('hideCameraDirectionLine', ()))
            if diff is None or settings_constants.GAME.SHOW_SECTOR_ON_MAP in diff:
                if GUI_SETTINGS.showSectorLines and self.isSpg():
                    if self.__showSectorLine:
                        self.__showSector()
                    else:
                        self.__hideSector()
        return

    def setTeamPoints(self):
        if self.__cfg['teamBasePositions'] or self.__cfg['teamSpawnPoints'] or self.__cfg['controlPoints'] or self.__cfg['repairPoints']:
            for team, teamSpawnPoints in enumerate(self.__cfg['teamSpawnPoints'], 1):
                teamSpawnData = {}
                self.__points['spawn'][team] = teamSpawnData
                for spawn, spawnPoint in enumerate(teamSpawnPoints, 1):
                    pos = (spawnPoint[0], 0, spawnPoint[1])
                    m = Math.Matrix()
                    m.setTranslate(pos)
                    teamSpawnData[spawn] = EntryInfo(self.__ownUI.addEntry(m, self.zIndexManager.getTeamPointIndex()), m)
                    self.__ownUI.entryInvoke(teamSpawnData[spawn].handle, ('init', ['points',
                      'spawn',
                      'blue' if team == self.__playerTeam else 'red',
                      spawn + 1 if len(teamSpawnPoints) > 1 else 1]))

            for team, teamBasePoints in enumerate(self.__cfg['teamBasePositions'], 1):
                teamBaseData = {}
                self.__points['base'][team] = teamBaseData
                for base, basePoint in teamBasePoints.items():
                    pos = (basePoint[0], 0, basePoint[1])
                    m = Math.Matrix()
                    m.setTranslate(pos)
                    teamBaseData[base] = EntryInfo(self.__ownUI.addEntry(m, self.zIndexManager.getTeamPointIndex()), m)
                    self.__ownUI.entryInvoke(teamBaseData[base].handle, ('init', ['points',
                      'base',
                      'blue' if team == self.__playerTeam else 'red',
                      len(teamBaseData) + 1 if len(teamBasePoints) > 1 else 1]))

            if self.__cfg['controlPoints']:
                controlData = []
                self.__points['control'] = controlData
                for index, controlPoint in enumerate(self.__cfg['controlPoints'], 2):
                    pos = (controlPoint[0], 0, controlPoint[1])
                    m = Math.Matrix()
                    m.setTranslate(pos)
                    newPoint = EntryInfo(self.__ownUI.addEntry(m, self.zIndexManager.getTeamPointIndex()), m)
                    controlData.append(newPoint)
                    self.__ownUI.entryInvoke(newPoint.handle, ('init', ['points',
                      'control',
                      'empty',
                      index if len(self.__cfg['controlPoints']) > 1 else 1]))

            if self.__cfg['repairPoints']:
                repairData = {}
                self.__points['repair'] = repairData
                for index, repairPoint in enumerate(self.__cfg['repairPoints']):
                    pos = repairPoint['position']
                    m = Math.Matrix()
                    m.setTranslate(pos)
                    newPoint = EntryInfo(self.__ownUI.addEntry(m, self.zIndexManager.getTeamPointIndex()), m)
                    self.__ownUI.entryInvoke(newPoint.handle, ('init', ['repairPoints',
                      'active',
                      '',
                      0]))
                    newPointCooldown = EntryInfo(self.__ownUI.addEntry(m, self.zIndexManager.getTeamPointIndex()), m)
                    self.__ownUI.entryInvoke(newPointCooldown.handle, ('init', ['repairPoints',
                      'cooldown',
                      '',
                      0]))
                    self.__entrySetActive(newPointCooldown.handle, False)
                    repairData[index] = (newPoint, newPointCooldown)

            self.__parentUI.call('minimap.entryInited', [])

    def updateGasAtackArea(self, radius):
        self.__parentUI.call('minimap.gasAtackUpdate', [radius])

    def initGasAtackArea(self, mapWidth, mapHeight, xPos, yPos, radius, safeZoneRadius):
        self.__parentUI.call('minimap.gasAtackInit', [mapWidth,
         mapHeight,
         xPos,
         yPos,
         radius,
         safeZoneRadius])

    def onSetSize(self, calbackID, index):
        self.__mapSizeIndex = int(index)
        self.__parentUI.call('minimap.setupSize', [self.__mapSizeIndex])

    def onLightPlayer(self, calbackID, vehicleID, visibility):
        self.__callEntryFlash(vehicleID, 'lightPlayer', [visibility])

    def destroy(self):
        if not self.__isStarted:
            self.__vehiclesWaitStart.clear()
            return
        else:
            while len(self.__aoiToFarCallbacks):
                _, callbackID = self.__aoiToFarCallbacks.popitem()
                if callbackID is not None:
                    BigWorld.cancelCallback(callbackID)

            self.__isStarted = False
            self.__entries = {}
            self.__entrieLits = {}
            self.__entrieMarkers = {}
            self.__cameraHandle = None
            self.__cameraMatrix = None
            ctrl = g_sessionProvider.getEquipmentsCtrl()
            if ctrl:
                ctrl.onEquipmentMarkerShown -= self.__onEquipmentMarkerShown
            ctrl = g_sessionProvider.getFeedback()
            if ctrl:
                ctrl.onMinimapVehicleAdded -= self.__onMinimapVehicleAdded
                ctrl.onMinimapVehicleRemoved -= self.__onMinimapVehicleRemoved
                ctrl.onMinimapFeedbackReceived -= self.__onMinimapFeedbackReceived
            removeListener = g_eventBus.removeListener
            removeListener(GameEvent.SHOW_EXTENDED_INFO, self.__handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)
            removeListener(GameEvent.MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)
            self.__markerIDGenerator = None
            if hasFlags():
                g_ctfManager.onFlagSpawning -= self.__onFlagSpawning
                g_ctfManager.onFlagSpawnedAtBase -= self.__onFlagSpawnedAtBase
                g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
                g_ctfManager.onFlagDroppedToGround -= self.__onFlagDroppedToGround
                g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
                g_ctfManager.onFlagRemoved -= self.__onFlagRemoved
                g_ctfManager.onCarriedFlagsPositionUpdated -= self.__onCarriedFlagsPositionUpdated
            if hasRepairPoints():
                g_sessionProvider.getRepairCtrl().onRepairPointStateChanged -= self.__onRepairPointStateChanged
            if hasResourcePoints():
                g_ctfManager.onResPointIsFree -= self.__onResPointIsFree
                g_ctfManager.onResPointCooldown -= self.__onResPointCooldown
                g_ctfManager.onResPointCaptured -= self.__onResPointCaptured
                g_ctfManager.onResPointCapturedLocked -= self.__onResPointCapturedLocked
                g_ctfManager.onResPointBlocked -= self.__onResPointBlocked
            if hasGasAttack():
                g_sessionProvider.getGasAttackCtrl().onPreparing -= self.__onGasAttackPreparing
                g_sessionProvider.getGasAttackCtrl().onStarted -= self.__onGasAttackStarted
            self.__marks = None
            self.__backMarkers.clear()
            setattr(self.__parentUI.component, 'minimap', None)
            from account_helpers.settings_core.SettingsCore import g_settingsCore
            g_settingsCore.onSettingsChanged -= self.setupMinimapSettings
            self.storeMinimapSize()
            self.__parentUI = None
            g_repeatKeyHandlers.remove(self.handleRepeatKeyEvent)
            self.__ownUI = None
            return

    def prerequisites(self):
        return []

    def setVisible(self, visible):
        pass

    def notifyVehicleStop(self, vehicleID):
        vInfo = g_sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        if not self.__isStarted:
            if vehicleID in self.__vehiclesWaitStart:
                self.__vehiclesWaitStart.pop(vehicleID, None)
            return
        elif vehicleID == self.__playerVehicleID:
            return
        elif not vInfo.isAlive():
            return
        else:
            entries = self.__entries
            if vehicleID in entries:
                location = entries[vehicleID]['location']
                if location == VehicleLocation.AOI:
                    ownPos = Math.Matrix(BigWorld.camera().invViewMatrix).translation
                    entryMatitx = entries[vehicleID]['matrix']
                    entryPos = Math.Matrix(entryMatitx).translation
                    if AOI.ENABLE_MANUAL_RULES:
                        inAoI = (ownPos.x - entryPos.x) ** 2 + (ownPos.z - entryPos.z) ** 2 < self.__AOI_ESTIMATE ** 2
                    else:
                        inAoI = bool(abs(ownPos.x - entryPos.x) < self.__AOI_ESTIMATE and abs(ownPos.z - entryPos.z) < self.__AOI_ESTIMATE)
                    guiProps = g_sessionProvider.getCtx().getPlayerGuiProps(vehicleID, vInfo.team)
                    self.__delEntry(vehicleID)
                    self.__delEntryLit(vehicleID)
                    if not inAoI:
                        self.__addEntry(vInfo, guiProps, VehicleLocation.AOI_TO_FAR, False)
                    elif self.__permanentNamesShow or self.__onAltNamesShow:
                        battleCtx = g_sessionProvider.getCtx()
                        if not battleCtx.isObserver(self.__playerVehicleID):
                            if type(entryMatitx) == Math.WGTranslationOnlyMP:
                                self.__addEntryLit(vInfo, guiProps, Math.Matrix(entryMatitx.source), not self.__onAltNamesShow or self.__isShowExtendedInfoActive)
                            else:
                                mp = Math.WGTranslationOnlyMP()
                                mp.source = Math.Matrix(entryMatitx)
                                self.__addEntryLit(vInfo, guiProps, mp, not self.__onAltNamesShow or self.__isShowExtendedInfoActive)
                else:
                    LOG_DEBUG('notifyVehicleOnStop, unknown minimap entry location', location)
            return

    def notifyVehicleStart(self, vProxy, vInfo, guiProps):
        vehicleID = vInfo.vehicleID
        if not self.__isStarted:
            self.__vehiclesWaitStart[vehicleID] = (vProxy, vInfo, guiProps)
            return
        if vehicleID == self.__playerVehicleID:
            return
        if not vProxy.isAlive():
            return
        entries = self.__entries
        doMark = True
        if vehicleID in entries:
            doMark = False
            self.__delEntry(vehicleID)
        self.__delEntryLit(vehicleID)
        self.__delCarriedFlagMarker(vehicleID)
        self.__addEntry(vInfo, guiProps, VehicleLocation.AOI, doMark)

    def _playAttention(self, _):
        if FMOD.enabled:
            SoundGroups.g_instance.playSound2D('/GUI/notifications_FX/minimap_attention')

    def markCell(self, cellIndexes, duration):
        if not self.__isStarted:
            return
        elif cellIndexes < 0:
            return
        else:
            columnCount, rowCount = Minimap.__MINIMAP_CELLS
            column = cellIndexes / columnCount % columnCount
            row = cellIndexes % columnCount
            if cellIndexes in self.__marks:
                BigWorld.cancelCallback(self.__marks[cellIndexes][1])
                self._removeCellMark(cellIndexes)
            arenaDesc = BigWorld.player().arena.arenaType
            bottomLeft, upperRight = arenaDesc.boundingBox
            viewpoint = (upperRight + bottomLeft) * 0.5
            viewpointTranslate = Math.Matrix()
            viewpointTranslate.setTranslate((viewpoint.x, 0.0, viewpoint.y))
            spaceSize = upperRight - bottomLeft
            pos = (column * spaceSize[0] / columnCount - spaceSize[0] * 0.5, 0, -row * spaceSize[1] / rowCount + spaceSize[0] * 0.5)
            m = Math.Matrix()
            m.setTranslate(Math.Matrix(viewpointTranslate).applyPoint(pos))
            player = BigWorld.player()
            if player.isTeleport:
                tmpPointUp = (pos[0], 1000.0, pos[2])
                tmpPointDown = (pos[0], -1000.0, pos[2])
                colRes = BigWorld.collide(player.spaceID, tmpPointUp, tmpPointDown)
                height = colRes[0][1]
                player.base.vehicle_teleport((pos[0], height, pos[2]), 0)
            mark = self.__ownUI.addEntry(m, self.zIndexManager.getIndexByName('cell'))
            self.__ownUI.entryInvoke(mark, ('gotoAndStop', ['cellFlash']))
            self._playAttention(None)
            callbackID = BigWorld.callback(duration, partial(self._removeCellMark, cellIndexes))
            self.__marks[cellIndexes] = (mark, callbackID)
            return

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

    def _onMapClicked(self, _, x, y, bHighlightCellNVehicleSpecific = True):
        localPos = (x - 0.5, y - 0.5)
        mapSize = Minimap.__MINIMAP_SIZE
        player = BigWorld.player()
        if bHighlightCellNVehicleSpecific:
            cellCount = Minimap.__MINIMAP_CELLS
            row = int(cellCount[0] * localPos[0] / mapSize[0])
            column = int(cellCount[1] * localPos[1] / mapSize[1])
            g_sessionProvider.getChatCommands().sendAttentionToCell(row * int(cellCount[1]) + column)
        else:
            arenaDesc = BigWorld.player().arena.arenaType
            bottomLeft, upperRight = arenaDesc.boundingBox
            spaceSize = upperRight - bottomLeft
            viewpoint = (upperRight + bottomLeft) * 0.5
            viewpointTranslate = Math.Matrix()
            viewpointTranslate.setTranslate((viewpoint.x, 0.0, viewpoint.y))
            pos = ((localPos[0] - mapSize[0] * 0.5) / mapSize[0], (localPos[1] - mapSize[1] * 0.5) / mapSize[1])
            worldPos = Math.Matrix(viewpointTranslate).applyPoint((pos[0] * spaceSize[0], 0.0, -pos[1] * spaceSize[1]))
            player.inputHandler.onMinimapClicked(worldPos)

    def __onVehicleAdded(self, vehicleID):
        vInfo = g_sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        if not vInfo.isAlive():
            return
        else:
            location = self.__detectLocation(vehicleID)
            if location is not None:
                guiProps = g_sessionProvider.getCtx().getPlayerGuiProps(vehicleID, vInfo.team)
                self.__addEntry(vInfo, guiProps, location, True)
            return

    def __onTeamKiller(self, id):
        arena = BigWorld.player().arena
        entryVehicle = arena.vehicles[id]
        if BigWorld.player().team == entryVehicle.get('team') and g_sessionProvider.getCtx().isSquadMan(vID=id):
            return
        self.__callEntryFlash(id, 'setEntryName', [PLAYER_GUI_PROPS.teamKiller.name()])

    def __onVehicleRemoved(self, vehicleID):
        if vehicleID in self.__entries:
            self.__delEntry(vehicleID)
        self.__delEntryLit(vehicleID)

    def __onVehicleKilled(self, victimId, *args):
        if victimId in self.__entries:
            entry = self.__delEntry(victimId)
            if GUI_SETTINGS.showMinimapDeath:
                self.__addDeadEntry(entry, victimId)
        self.__delEntryLit(victimId)

    def __onFarPosUpdated(self):
        entries = self.__entries
        arenaDP = g_sessionProvider.getArenaDP()
        getVehicleInfo = arenaDP.getVehicleInfo
        getPlayerGuiProps = arenaDP.getPlayerGuiProps
        arena = BigWorld.player().arena
        for vehicleID, pos in arena.positions.iteritems():
            vInfo = getVehicleInfo(vehicleID)
            if vehicleID in entries:
                entry = entries[vehicleID]
                location = entry['location']
                if location == VehicleLocation.FAR:
                    entry['matrix'].source.setTranslate(pos)
                elif location == VehicleLocation.AOI_TO_FAR:
                    self.__delEntry(vehicleID)
                    self.__delEntryLit(vehicleID)
                    self.__addEntry(vInfo, getPlayerGuiProps(vehicleID, vInfo.team), VehicleLocation.FAR, False)
            elif vInfo.isAlive():
                self.__delEntryLit(vehicleID)
                self.__addEntry(vInfo, getPlayerGuiProps(vehicleID, vInfo.team), VehicleLocation.FAR, True)

        for vehicleID in set(entries).difference(set(arena.positions)):
            location = entries[vehicleID]['location']
            if location in (VehicleLocation.FAR, VehicleLocation.AOI_TO_FAR):
                if self.__permanentNamesShow or self.__onAltNamesShow:
                    if hasattr(entries[vehicleID]['matrix'], 'source'):
                        vInfo = getVehicleInfo(vehicleID)
                        guiProps = getPlayerGuiProps(vehicleID, vInfo.team)
                        self.__addEntryLit(vInfo, guiProps, entries[vehicleID]['matrix'].source, not self.__onAltNamesShow or self.__isShowExtendedInfoActive)
                self.__delEntry(vehicleID)

    def __validateEntries(self):
        entrySet = set(self.__entries.iterkeys())
        vehiclesSet = set(BigWorld.player().arena.vehicles.iterkeys())
        playerOnlySet = {self.__playerVehicleID}
        for id in vehiclesSet.difference(entrySet) - playerOnlySet:
            self.__onVehicleAdded(id)

        for id in entrySet.difference(vehiclesSet) - playerOnlySet:
            self.__onVehicleRemoved(id)

    def __detectLocation(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is not None and vehicle.isStarted:
            return VehicleLocation.AOI
        elif vehicleID in BigWorld.player().arena.positions:
            return VehicleLocation.FAR
        else:
            return
            return

    def __delEntry(self, vehicleID):
        entry = self.__entries.get(vehicleID)
        if entry is None:
            return
        else:
            self.__ownUI.delEntry(entry['handle'])
            if entry.get('location') == VehicleLocation.AOI_TO_FAR:
                callbackId = self.__aoiToFarCallbacks.pop(vehicleID, None)
                if callbackId is not None:
                    BigWorld.cancelCallback(callbackId)
            if vehicleID in self.__enemyEntries:
                self.__enemyEntries.pop(vehicleID)
                if not len(self.__enemyEntries):
                    if self.__checkEnemyNonSPGLengthID:
                        BigWorld.cancelCallback(self.__checkEnemyNonSPGLengthID)
                    self.__checkEnemyNonSPGLengthID = BigWorld.callback(5, self.__checkEnemyNonSPGLength)
            if vehicleID in self.__deadCallbacks:
                callbackId = self.__deadCallbacks.pop(vehicleID)
                BigWorld.cancelCallback(callbackId)
            return self.__entries.pop(vehicleID)

    def __addDeadEntry(self, entry, id):
        """
        adding death animation to minimap (WOTD-5884)
        """
        if id in BigWorld.entities.keys():
            m = self.__getEntryMatrixByLocation(id, entry['location'])
            scaledMatrix = None
            if self.__markerScale is not None:
                scaleMatrix = Math.Matrix()
                scaleMatrix.setScale(Math.Vector3(self.__markerScale, self.__markerScale, self.__markerScale))
                scaledMatrix = mathUtils.MatrixProviders.product(scaleMatrix, m)
            if scaledMatrix is None:
                entry['handle'] = self.__ownUI.addEntry(m, self.zIndexManager.getDeadVehicleIndex(id))
            else:
                entry['handle'] = self.__ownUI.addEntry(scaledMatrix, self.zIndexManager.getVehicleIndex(id))
            self.__entries[id] = entry
            if not GUI_SETTINGS.permanentMinimapDeath:
                self.__deadCallbacks[id] = BigWorld.callback(GUI_SETTINGS.minimapDeathDuration / 1000, partial(self.__delEntry, id))
            self.__callEntryFlash(id, 'setDead', [GUI_SETTINGS.permanentMinimapDeath])
            self.__callEntryFlash(id, 'init', [entry['markerType'],
             entry['entryName'],
             entry['vClass'],
             ''])
            if self.__markerScale is None:
                self.__parentUI.call('minimap.entryInited', [])
        return

    def __checkEnemyNonSPGLength(self):
        self.__checkEnemyNonSPGLengthID = None
        self.__isFirstEnemyNonSPGMarked = not len(self.__enemyEntries) == 0
        return

    def __getEntryMatrixByLocation(self, id, location):
        m = None
        matrix = None
        if location == VehicleLocation.AOI:
            m = Math.WGTranslationOnlyMP()
            matrix = BigWorld.entities[id].matrix
        elif location == VehicleLocation.AOI_TO_FAR:
            m = Math.WGTranslationOnlyMP()
            matrix = Math.Matrix(BigWorld.entities[id].matrix)
        elif location == VehicleLocation.FAR:
            matrix = Math.Matrix()
            pos = BigWorld.player().arena.positions[id]
            matrix.setTranslate(pos)
            m = Math.WGReplayAwaredSmoothTranslationOnlyMP()
        m.source = matrix
        return m

    def addBackEntry(self, id, name, position, type):
        viewpointTranslate = Math.Matrix()
        viewpointTranslate.setTranslate((0.0, 0.0, 0.0))
        m = Math.Matrix()
        m.setTranslate(Math.Matrix(viewpointTranslate).applyPoint(position))
        markerType = 'backgroundMarker'
        marker = dict()
        marker['handle'] = self.__ownUI.addEntry(m, self.zIndexManager.getBackIconIndex(id))
        marker['markerType'] = markerType
        marker['entryName'] = name
        marker['type'] = type
        self.__backMarkers[marker['handle']] = marker
        self.__ownUI.entryInvoke(marker['handle'], ('init', [markerType,
          name,
          '',
          type]))
        if self.__markerScale is None:
            self.__parentUI.call('minimap.entryInited', [])
        return marker['handle']

    def removeBackEntry(self, handle):
        marker = self.__backMarkers.pop(handle, None)
        if marker is not None and self.__ownUI is not None:
            self.__ownUI.delEntry(handle)
        return

    def showVehicleNames(self, value):
        self.__parentUI.call('minimap.setShowVehicleName', [value])

    def __addEntryLit(self, vInfo, guiProps, matrix, visible = True):
        if vInfo.isObserver():
            return
        elif matrix is None:
            return
        else:
            vehicleID = vInfo.vehicleID
            markerType = guiProps.base
            if self.__currentMode == MODE_POSTMORTEM and markerType == 'ally':
                return
            mp = Math.WGReplayAwaredSmoothTranslationOnlyMP()
            mp.source = matrix
            scaledMatrix = None
            if self.__markerScale is not None:
                scaleMatrix = Math.Matrix()
                scaleMatrix.setScale(Math.Vector3(self.__markerScale, self.__markerScale, self.__markerScale))
                scaledMatrix = mathUtils.MatrixProviders.product(scaleMatrix, mp)
            if scaledMatrix is None:
                handle = self.__ownUI.addEntry(mp, self.zIndexManager.getVehicleIndex(vehicleID))
            else:
                handle = self.__ownUI.addEntry(scaledMatrix, self.zIndexManager.getVehicleIndex(vehicleID))
            entry = {'matrix': mp,
             'handle': handle}
            entryName = guiProps.name()
            self.__entrieLits[vehicleID] = entry
            vName = vInfo.vehicleType.shortNameWithPrefix
            self.__ownUI.entryInvoke(entry['handle'], ('init', [markerType,
              entryName,
              'lastLit',
              '',
              vName]))
            if not visible:
                self.__entrySetActive(entry['handle'], visible)
            if self.__markerScale is None:
                self.__parentUI.call('minimap.entryInited', [])
            return

    def __delEntryLit(self, vehicleID):
        entry = self.__entrieLits.pop(vehicleID, None)
        if entry is not None:
            self.__ownUI.delEntry(entry['handle'])
        return

    def __addEntryMarker(self, markerType, marker, uniqueID, zIndex, matrix, isVisible = True, index = None):
        if matrix is None:
            return
        else:
            mp = Math.WGReplayAwaredSmoothTranslationOnlyMP()
            mp.source = matrix
            scaledMatrix = None
            if self.__markerScale is not None:
                scaleMatrix = Math.Matrix()
                scaleMatrix.setScale(Math.Vector3(self.__markerScale, self.__markerScale, self.__markerScale))
                scaledMatrix = mathUtils.MatrixProviders.product(scaleMatrix, mp)
            if scaledMatrix is None:
                handle = self.__ownUI.addEntry(mp, zIndex)
            else:
                handle = self.__ownUI.addEntry(scaledMatrix, zIndex)
            entry = {'matrix': mp,
             'handle': handle}
            self.__entrieMarkers[uniqueID] = entry
            indexNumber = str(index) if index is not None else ''
            self.__ownUI.entryInvoke(entry['handle'], ('init', [markerType,
              marker,
              '',
              indexNumber,
              '']))
            if not isVisible:
                self.__entrySetActive(entry['handle'], False)
            if self.__markerScale is None:
                self.__parentUI.call('minimap.entryInited', [])
            return

    def __delEntryMarker(self, uniqueID):
        entry = self.__entrieMarkers.pop(uniqueID, None)
        if entry is not None:
            self.__ownUI.delEntry(entry['handle'])
        return

    def __addEntry(self, vInfo, guiProps, location, doMark):
        if vInfo.isObserver():
            return
        else:
            entry = {}
            vehicleID = vInfo.vehicleID
            m = self.__getEntryMatrixByLocation(vehicleID, location)
            scaledMatrix = None
            if self.__markerScale is not None:
                scaleMatrix = Math.Matrix()
                scaleMatrix.setScale(Math.Vector3(self.__markerScale, self.__markerScale, self.__markerScale))
                scaledMatrix = mathUtils.MatrixProviders.product(scaleMatrix, m)
            if location == VehicleLocation.AOI_TO_FAR:
                self.__aoiToFarCallbacks[vehicleID] = BigWorld.callback(self.__AOI_TO_FAR_TIME, partial(self.__delEntry, vehicleID))
            entry['location'] = location
            entry['matrix'] = m
            if scaledMatrix is None:
                entry['handle'] = self.__ownUI.addEntry(m, self.zIndexManager.getVehicleIndex(vehicleID))
            else:
                entry['handle'] = self.__ownUI.addEntry(scaledMatrix, self.zIndexManager.getVehicleIndex(vehicleID))
            self.__entries[vehicleID] = entry
            markerType = guiProps.base
            entryName = guiProps.name()
            classTag = vInfo.vehicleType.classTag
            markMarker = ''
            if not guiProps.isFriend:
                if doMark and not g_sessionProvider.getCtx().isPlayerObserver():
                    if classTag == 'SPG':
                        if vehicleID not in self.__isFirstEnemySPGMarkedById:
                            self.__isFirstEnemySPGMarkedById[vehicleID] = False
                        isFirstEnemySPGMarked = self.__isFirstEnemySPGMarkedById[vehicleID]
                        if not isFirstEnemySPGMarked:
                            markMarker = 'enemySPG'
                            self.__isFirstEnemySPGMarkedById[vehicleID] = True
                            self.__resetSPGMarkerTimoutCbckId = BigWorld.callback(5, partial(self.__resetSPGMarkerCallback, vehicleID))
                    elif not self.__isFirstEnemyNonSPGMarked and markMarker == '':
                        if not len(self.__enemyEntries):
                            markMarker = 'firstEnemy'
                            self.__isFirstEnemyNonSPGMarked = True
                    if markMarker != '':
                        BigWorld.player().soundNotifications.play('enemy_sighted_for_team')
                self.__enemyEntries[vehicleID] = entry
            if GUI_SETTINGS.showMinimapSuperHeavy and vInfo.vehicleType.level == 10 and classTag == 'heavyTank':
                classTag = 'super' + classTag
            vName = vInfo.vehicleType.shortNameWithPrefix
            self.__callEntryFlash(vehicleID, 'init', [markerType,
             entryName,
             classTag,
             markMarker,
             vName])
            if g_ctfManager.isFlagBearer(vehicleID):
                self.__callEntryFlash(vehicleID, 'setVehicleClass', classTag + 'Flag')
            entry['markerType'] = markerType
            entry['entryName'] = entryName
            entry['vClass'] = classTag
            if self.__markerScale is None:
                self.__parentUI.call('minimap.entryInited', [])
            return

    def __resetSPGMarkerCallback(self, id):
        self.__isFirstEnemySPGMarkedById[id] = False

    def updateEntries(self):
        self.__parentUI.call('minimap.updatePoints', [])
        for id in self.__entries:
            self.__callEntryFlash(id, 'update')

        for handle in self.__backMarkers:
            self.__ownUI.entryInvoke(handle, ('update', None))

        for entry in self.__entrieMarkers.itervalues():
            handle = entry['handle']
            self.__ownUI.entryInvoke(handle, ('update', None))

        return None

    def __callEntryFlash(self, entryID, methodName, args = None):
        if not self.__isStarted:
            return
        else:
            if args is None:
                args = []
            if entryID in self.__entries:
                self.__ownUI.entryInvoke(self.__entries[entryID]['handle'], (methodName, args))
            elif entryID == BigWorld.player().playerVehicleID:
                if 'handle' in self.__ownEntry:
                    self.__ownUI.entryInvoke(self.__ownEntry['handle'], (methodName, args))
            return

    def __resetVehicleIfObserved(self, id):
        if self.__observedVehicleId > 0 and id == self.__observedVehicleId:
            self.__callEntryFlash(self.__observedVehicleId, 'setPostmortem', [False])
            if self.__observedVehicleId in self.__entries:
                entry = self.__entries[self.__observedVehicleId]
                if 'handle' in entry:
                    mp1 = self.__getEntryMatrixByLocation(self.__observedVehicleId, entry['location'])
                    self.__ownUI.entrySetMatrix(entry['handle'], mp1)
                    entry['matrix'] = mp1
            self.__observedVehicleId = -1

    def __resetCamera(self, mode, vehicleId = None):
        self.__currentMode = mode
        if self.__cameraHandle is not None:
            self.__ownUI.delEntry(self.__cameraHandle)
        if _isStrategic(mode):
            m = Math.WGStrategicAreaViewMP()
            m.source = BigWorld.camera().invViewMatrix
            m.baseScale = (1.0, 1.0)
        elif mode == MODE_ARCADE or mode == MODE_SNIPER:
            m = Math.WGCombinedMP()
            m.translationSrc = BigWorld.player().getOwnVehicleMatrix()
            m.rotationSrc = BigWorld.camera().invViewMatrix
        elif mode == MODE_POSTMORTEM:
            m = Math.WGCombinedMP()
            if vehicleId is not None:
                translationSrc = Math.WGTranslationOnlyMP()
                translationSrc.source = BigWorld.entities[vehicleId].matrix
            else:
                translationSrc = BigWorld.player().getOwnVehicleMatrix()
            m.translationSrc = translationSrc
            m.rotationSrc = BigWorld.camera().invViewMatrix
        elif mode == MODE_VIDEO:
            m = BigWorld.camera().invViewMatrix
        else:
            m = BigWorld.camera().invViewMatrix
        if mode == MODE_VIDEO:
            self.__cameraHandle = self.__ownUI.addEntry(m, self.zIndexManager.getIndexByName(CAMERA_VIDEO))
            self.__cameraMatrix = m
            self.__ownUI.entryInvoke(self.__cameraHandle, ('init', ['player', mode]))
        else:
            self.__cameraHandle = self.__ownUI.addEntry(m, self.zIndexManager.getIndexByName(CAMERA_STRATEGIC if _isStrategic(mode) else CAMERA_NORMAL))
            self.__cameraMatrix = m
            cursorType = CURSOR_NORMAL
            if _isStrategic(mode):
                cursorType = CURSOR_STRATEGIC
            self.__ownUI.entryInvoke(self.__cameraHandle, ('gotoAndStop', [cursorType]))
            vehicle = BigWorld.entity(self.__playerVehicleID)
            if vehicle is not None and vehicle.isAlive() and not g_sessionProvider.getCtx().isPlayerObserver():
                if GUI_SETTINGS.showDirectionLine and self.__showDirectionLine and cursorType == CURSOR_NORMAL:
                    self.__ownUI.entryInvoke(self.__cameraHandle, ('showCameraDirectionLine', ()))
                if GUI_SETTINGS.showSectorLines and self.isSpg() and self.__showSectorLine:
                    self.__showSector()
        if mode in (MODE_POSTMORTEM, MODE_VIDEO):
            self.__resetVehicleIfObserved(self.__observedVehicleId)
            playerMarker = mode
            if vehicleId is not None and vehicleId != BigWorld.player().playerVehicleID:
                self.__observedVehicleId = vehicleId
                self.__callEntryFlash(vehicleId, 'setPostmortem', [True])
                mp = BigWorld.player().getOwnVehicleMatrix()
                if vehicleId in self.__entries:
                    entry = self.__entries[vehicleId]
                    if 'handle' in entry:
                        mp1 = BigWorld.entities[vehicleId].matrix
                        self.__ownUI.entrySetMatrix(entry['handle'], mp1)
                        entry['matrix'] = mp1
            else:
                playerMarker += 'Camera'
                mp = Math.WGCombinedMP()
                mp.translationSrc = BigWorld.player().getOwnVehicleMatrix()
                mp.rotationSrc = BigWorld.camera().invViewMatrix
            if 'handle' in self.__ownEntry:
                self.__ownUI.entrySetMatrix(self.__ownEntry['handle'], mp)
            self.__callEntryFlash(BigWorld.player().playerVehicleID, 'init', ['player', playerMarker])
        if not _isStrategic(mode) and self.__markerScale is not None:
            self.scaleMarker(self.__cameraHandle, self.__cameraMatrix, self.__markerScale)
            vehicle = BigWorld.entity(self.__playerVehicleID)
            if vehicle is not None and vehicle.isAlive() and GUI_SETTINGS.showDirectionLine and self.__showDirectionLine:
                self.__ownUI.entryInvoke(self.__cameraHandle, ('updateLinesScale', [self.__normalMarkerScale]))
        if self.__markerScale is None:
            self.__parentUI.call('minimap.entryInited', [])
        else:
            self.onScaleMarkers(None, self.__markerScale, self.__normalMarkerScale)
        return

    def __clearCamera(self, vehicleId):
        if self.__cameraHandle is not None:
            self.__ownUI.delEntry(self.__cameraHandle)
            self.__cameraHandle = None
            self.__cameraMatrix = None
        return

    def isSpg(self):
        vehicle = BigWorld.entity(self.__playerVehicleID)
        if not vehicle:
            return False
        vTypeDesc = vehicle.typeDescriptor
        return 'SPG' in vTypeDesc.type.tags and vehicle_getter.hasYawLimits(vTypeDesc)

    def handleRepeatKeyEvent(self, event):
        if not MessengerEntry.g_instance.gui.isEditing(event):
            if GUI_SETTINGS.minimapSize:
                from game import convertKeyEvent
                cmdMap = CommandMapping.g_instance
                isDown, key, mods, isRepeat = convertKeyEvent(event)
                if isRepeat and isDown and not BigWorld.isKeyDown(Keys.KEY_RSHIFT) and cmdMap.isFiredList((CommandMapping.CMD_MINIMAP_SIZE_DOWN, CommandMapping.CMD_MINIMAP_SIZE_UP), key):
                    self.handleKey(key)

    def handleKey(self, key):
        if GUI_SETTINGS.minimapSize:
            cmdMap = CommandMapping.g_instance
            if cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_DOWN, key):
                self.__parentUI.call('minimap.sizeDown', [])
            elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_UP, key):
                self.__parentUI.call('minimap.sizeUp', [])
            elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_VISIBLE, key):
                self.__parentUI.call('minimap.visible', [])

    def showActionMarker(self, vehicleID, newState):
        self.__callEntryFlash(vehicleID, 'showAction', [newState])

    def __updateSettings(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        from account_helpers.settings_core import settings_constants
        setting = g_settingsCore.options.getSetting(settings_constants.GAME.SHOW_VEH_MODELS_ON_MAP)
        value = setting.get()
        valueName = setting.VEHICLE_MODELS_TYPES[value]
        self.__permanentNamesShow = valueName == setting.OPTIONS.ALWAYS
        self.__onAltNamesShow = valueName == setting.OPTIONS.ALT
        self.__showDirectionLine = g_settingsCore.getSetting(settings_constants.GAME.SHOW_VECTOR_ON_MAP)
        self.__showSectorLine = g_settingsCore.getSetting(settings_constants.GAME.SHOW_SECTOR_ON_MAP)
        for entry in self.__entrieLits.values():
            self.__entrySetActive(entry['handle'], self.__permanentNamesShow)

    def __onEquipmentMarkerShown(self, item, pos, dir, time):
        markerType = MARKER_TYPE.CONSUMABLE
        marker = item.getMarker()
        mp = Math.Matrix()
        mp.translation = pos
        uniqueID = '%s%s%d' % (markerType, marker, self.__markerIDGenerator.next())
        zIndex = self.zIndexManager.getMarkerIndex(uniqueID)
        if zIndex is not None:
            self.__addEntryMarker(markerType, marker, uniqueID, zIndex, mp)

            def callback():
                self.zIndexManager.clearMarkerIndex(uniqueID)
                self.__delEntryMarker(uniqueID)

            BigWorld.callback(int(time), callback)
        return

    def __handleShowExtendedInfo(self, event):
        if not self.__permanentNamesShow and self.__onAltNamesShow:
            for entry in self.__entrieLits.values():
                self.__entrySetActive(entry['handle'], event.ctx['isDown'])

            self.showVehicleNames(event.ctx['isDown'])
            self.__isShowExtendedInfoActive = event.ctx['isDown']

    def __handleMinimapCmd(self, event):
        self.handleKey(event.ctx['key'])

    def __onFlagSpawning(self, flagID, respawnTime):
        flagType = FLAG_TYPE.COOLDOWN
        flagPos = self.__cfg['flagSpawnPoints'][flagID]['position']
        self.__addFlagMarker(flagID, flagPos, flagType)

    def __onFlagSpawnedAtBase(self, flagID, flagTeam, flagPos):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self.__delFlagMarker(flagID, FLAG_TYPE.COOLDOWN)
        self.__delFlagMarker(flagID, flagType)
        self.__addFlagMarker(flagID, flagPos, flagType)

    def __onFlagCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self.__updateVehicleFlagState(vehicleID, True)
        self.__delFlagMarker(flagID, flagType)
        if vehicleID == self.__playerVehicleID:
            self.__toggleFlagCaptureAnimation(True)

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self.__updateVehicleFlagState(loserVehicleID)
        self.__addFlagMarker(flagID, flagPos, flagType)
        self.__delCarriedFlagMarker(loserVehicleID)
        if loserVehicleID == self.__playerVehicleID:
            self.__toggleFlagCaptureAnimation(False)

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self.__updateVehicleFlagState(vehicleID)
        self.__delFlagMarker(flagID, flagType)
        self.__delCarriedFlagMarker(vehicleID)
        if vehicleID == self.__playerVehicleID:
            self.__toggleFlagCaptureAnimation(False)

    def __onFlagRemoved(self, flagID, flagTeam, vehicleID):
        flagType = self.__getFlagMarkerType(flagID, flagTeam)
        self.__delFlagMarker(flagID, flagType)
        if vehicleID is not None:
            self.__updateVehicleFlagState(vehicleID)
            self.__delCarriedFlagMarker(vehicleID)
            if vehicleID == self.__playerVehicleID:
                self.__toggleFlagCaptureAnimation(False)
        return

    def __onCarriedFlagsPositionUpdated(self, flagIDs):
        for flagID in flagIDs:
            flagInfo = g_ctfManager.getFlagInfo(flagID)
            vehID = flagInfo['vehicle']
            if vehID is not None and vehID != self.__playerVehicleID:
                if vehID not in self.__entries:
                    flagPos = g_ctfManager.getFlagMinimapPos(flagID)
                    battleCtx = g_sessionProvider.getCtx()
                    if battleCtx.isObserver(vehID):
                        marker = FLAG_TYPE.NEUTRAL
                    else:
                        arena = BigWorld.player().arena
                        entryVehicle = arena.vehicles[vehID]
                        entityName = battleCtx.getPlayerGuiProps(vehID, entryVehicle.get('team'))
                        marker = FLAG_TYPE.ALLY if entityName.isFriend else FLAG_TYPE.ENEMY
                    uniqueID = self.__makeFlagUniqueID(flagID, marker)
                    if uniqueID in self.__entrieMarkers:
                        item = self.__entrieMarkers[uniqueID]
                        mp = Math.Matrix()
                        mp.translation = flagPos
                        self.__ownUI.entrySetMatrix(item['handle'], mp)
                        item['matrix'] = mp
                    else:
                        self.__addFlagMarker(flagID, flagPos, marker)
                    self.__vehicleIDToFlagUniqueID[vehID] = uniqueID
                else:
                    self.__delCarriedFlagMarker(vehID)

        return

    def __makeFlagUniqueID(self, flagID, marker):
        markerType = MARKER_TYPE.FLAG
        return '%s%s%d' % (markerType, marker, flagID)

    def __updateVehicleFlagState(self, vehicleID, isBearer = False):
        if vehicleID == self.__playerVehicleID:
            entryName = self.__ownEntry['entryName']
            self.__ownUI.entryInvoke(self.__ownEntry['handle'], ('setEntryName', [entryName + 'Flag' if isBearer else entryName]))
        elif vehicleID in self.__entries:
            entry = self.__entries[vehicleID]
            vClass = entry['vClass']
            self.__callEntryFlash(vehicleID, 'setVehicleClass', vClass + 'Flag' if isBearer else vClass)

    def __addFlagMarker(self, flagID, flagPos, marker, isVisible = True):
        uniqueID = self.__makeFlagUniqueID(flagID, marker)
        mp = Math.Matrix()
        mp.translation = flagPos
        if marker == FLAG_TYPE.ALLY_CAPTURE:
            zIndex = self.zIndexManager.getTeamPointIndex()
        elif marker == FLAG_TYPE.ALLY_CAPTURE_ANIMATION:
            zIndex = self.zIndexManager.getAnimationIndex(uniqueID)
        else:
            zIndex = self.zIndexManager.getFlagIndex(uniqueID)
        if zIndex is not None:
            self.__addEntryMarker(MARKER_TYPE.FLAG, marker, uniqueID, zIndex, mp, isVisible)
        return

    def __delFlagMarker(self, flagID, marker):
        uniqueID = self.__makeFlagUniqueID(flagID, marker)
        if marker == FLAG_TYPE.ALLY_CAPTURE_ANIMATION:
            self.zIndexManager.clearAnimationIndex(uniqueID)
        elif marker != FLAG_TYPE.ALLY_CAPTURE:
            self.zIndexManager.clearFlagIndex(uniqueID)
        self.__delEntryMarker(uniqueID)

    def __delCarriedFlagMarker(self, vehicleID):
        uniqueID = self.__vehicleIDToFlagUniqueID.pop(vehicleID, None)
        if uniqueID is not None:
            self.zIndexManager.clearFlagIndex(uniqueID)
            self.__delEntryMarker(uniqueID)
        return

    def __addFlagCaptureMarkers(self, isCarried = False):
        for pointIndex, point in enumerate(self.__cfg['flagAbsorptionPoints']):
            position = point['position']
            isMyTeam = self.__isTeamPlayer and point['team'] in (NEUTRAL_TEAM, self.__playerTeam)
            marker = FLAG_TYPE.ALLY_CAPTURE if isMyTeam else FLAG_TYPE.ENEMY_CAPTURE
            self.__addFlagMarker(pointIndex, position, marker, not isMyTeam or not isCarried)
            if isMyTeam:
                self.__addFlagMarker(pointIndex, position, FLAG_TYPE.ALLY_CAPTURE_ANIMATION, isCarried)

    def __toggleFlagCaptureAnimation(self, isCarried = False):
        for pointIndex, point in enumerate(self.__cfg['flagAbsorptionPoints']):
            if self.__isTeamPlayer and point['team'] in (NEUTRAL_TEAM, self.__playerTeam):
                captureUniqueID = self.__makeFlagUniqueID(pointIndex, FLAG_TYPE.ALLY_CAPTURE)
                captureEntry = self.__entrieMarkers.get(captureUniqueID)
                self.__entrySetActive(captureEntry['handle'], not isCarried)
                captureAnumationUniqueID = self.__makeFlagUniqueID(pointIndex, FLAG_TYPE.ALLY_CAPTURE_ANIMATION)
                captureAnimationEntry = self.__entrieMarkers.get(captureAnumationUniqueID)
                self.__entrySetActive(captureAnimationEntry['handle'], isCarried)

    def __delFlagCaptureMarkers(self):
        if hasFlags():
            for pointIndex, point in enumerate(self.__cfg['flagAbsorptionPoints']):
                if self.__isTeamPlayer and point['team'] in (NEUTRAL_TEAM, self.__playerTeam):
                    captureUniqueID = self.__makeFlagUniqueID(pointIndex, FLAG_TYPE.ALLY_CAPTURE)
                    self.__delEntryMarker(captureUniqueID)
                    captureAnumationUniqueID = self.__makeFlagUniqueID(pointIndex, FLAG_TYPE.ALLY_CAPTURE_ANIMATION)
                    self.__delEntryMarker(captureAnumationUniqueID)
                else:
                    captureUniqueID = self.__makeFlagUniqueID(pointIndex, FLAG_TYPE.ENEMY_CAPTURE)
                    self.__delEntryMarker(captureUniqueID)

    def __getFlagMarkerType(self, flagID, flagTeam = 0):
        if flagTeam > 0:
            if flagTeam == self.__playerTeam:
                return FLAG_TYPE.ALLY
            return FLAG_TYPE.ENEMY
        return FLAG_TYPE.NEUTRAL

    def __onRepairPointStateChanged(self, repairPointID, action, timeLeft = 0):
        if repairPointID not in self.__points['repair']:
            LOG_ERROR('Got repair point state changed for not available repair point: ', repairPointID, action, timeLeft)
            return
        if action in (REPAIR_POINT_ACTION.START_REPAIR, REPAIR_POINT_ACTION.COMPLETE_REPAIR, REPAIR_POINT_ACTION.BECOME_READY):
            point, pointCooldown = self.__points['repair'][repairPointID]
            pointVisible, pointCooldownVisible = (True, False) if action != REPAIR_POINT_ACTION.COMPLETE_REPAIR else (False, True)
            self.__entrySetActive(point.handle, pointVisible)
            self.__entrySetActive(pointCooldown.handle, pointCooldownVisible)
        elif action == REPAIR_POINT_ACTION.BECOME_DISABLED:
            point, pointCooldown = self.__points['repair'][repairPointID]
            self.__entrySetActive(point.handle, False)
            self.__entrySetActive(pointCooldown.handle, False)

    def __entrySetActive(self, entryHandle, visible):
        self.__ownUI.entrySetActive(entryHandle, visible)
        self.__ownUI.entryInvoke(entryHandle, ('resumeAnimation' if visible else 'stopAnimation',))

    def __onMinimapVehicleAdded(self, vProxy, vInfo, guiProps):
        self.notifyVehicleStart(vProxy, vInfo, guiProps)

    def __onMinimapVehicleRemoved(self, vehicleID):
        self.notifyVehicleStop(vehicleID)

    def __onMinimapFeedbackReceived(self, eventID, entityID, value):
        if eventID == FEEDBACK_EVENT_ID.MINIMAP_MARK_CELL:
            self.markCell(*value)
        elif eventID == FEEDBACK_EVENT_ID.MINIMAP_SHOW_MARKER:
            self.showActionMarker(entityID, value)

    def __makeResourcePointUniqueID(self, pointID):
        markerType = MARKER_TYPE.RESOURCE_POINT
        return '%s%d' % (markerType, pointID)

    def __addResourcePointMarker(self, pointID, pointPos, state):
        uniqueID = self.__makeResourcePointUniqueID(pointID)
        mp = Math.Matrix()
        mp.translation = pointPos
        self.__addEntryMarker(MARKER_TYPE.RESOURCE_POINT, state, uniqueID, self.zIndexManager.getTeamPointIndex(), mp, index=pointID)

    def __delResourcePointMarker(self, pointID):
        uniqueID = self.__makeResourcePointUniqueID(pointID)
        self.__delEntryMarker(uniqueID)

    def __setResourcePointState(self, pointID, state):
        uniqueID = self.__makeResourcePointUniqueID(pointID)
        entry = self.__entrieMarkers[uniqueID]
        self.__ownUI.entryInvoke(entry['handle'], ('setEntryName', [state]))

    def __onResPointIsFree(self, pointID):
        self.__setResourcePointState(pointID, RESOURCE_POINT_TYPE.READY)

    def __onResPointCooldown(self, pointID, serverTime):
        self.__setResourcePointState(pointID, RESOURCE_POINT_TYPE.COOLDOWN)

    def __onResPointCaptured(self, pointID, team):
        state = _CAPTURE_STATE_BY_TEAMS[g_sessionProvider.getArenaDP().isAllyTeam(team)]
        self.__setResourcePointState(pointID, state)

    def __onResPointCapturedLocked(self, pointID, team):
        state = _CAPTURE_FROZEN_STATE_BY_TEAMS[g_sessionProvider.getArenaDP().isAllyTeam(team)]
        self.__setResourcePointState(pointID, state)

    def __onResPointBlocked(self, pointID):
        self.__setResourcePointState(pointID, RESOURCE_POINT_TYPE.CONFLICT)

    def __onGasAttackPreparing(self, state):
        self.__delFlagCaptureMarkers()

    def __onGasAttackStarted(self, state):
        self.__delFlagCaptureMarkers()

    def __initGasAttackArea(self):
        _, settings = _getDefaultScenario()
        bottomLeft, upperRight = BigWorld.player().arena.arenaType.boundingBox
        arenaWidth = upperRight[0] - bottomLeft[0]
        arenaHeight = upperRight[1] - bottomLeft[1]
        shiftX = (upperRight[0] + bottomLeft[0]) / 2
        shiftY = (upperRight[1] + bottomLeft[1]) / 2
        self.initGasAtackArea(arenaWidth, arenaHeight, settings.position[0] - shiftX, settings.position[2] - shiftY, settings.startRadius, settings.endRadius)


class EntryInfo(object):

    def __init__(self, handle, matrix):
        self.__handle = handle
        self.__matrix = matrix

    @property
    def handle(self):
        return self.__handle

    @property
    def matrix(self):
        return self.__matrix


class MinimapZIndexManager(object):
    _BASES_RANGE = (0, 99)
    _BACK_ICONS_RANGE = (100, 124)
    _MARKER_RANGE = (200, 299)
    _DEAD_VEHICLE_RANGE = (300, 349)
    _VEHICLE_RANGE = (350, 399)
    _FLAG_RANGE = (400, 449)
    _ANIMATION_RANGE = (450, 500)
    _FIXED_INDEXES = {CAMERA_NORMAL: 1000,
     'self': 1001,
     CAMERA_STRATEGIC: 1002,
     'cell': 1003,
     CAMERA_VIDEO: 1004}

    def __init__(self):
        self.__indexes = {}
        self.__indexesDead = {}
        self.__lastPointIndex = MinimapZIndexManager._BASES_RANGE[0]
        self.__lastVehIndex = MinimapZIndexManager._VEHICLE_RANGE[0]
        self.__lastDeadVehIndex = MinimapZIndexManager._DEAD_VEHICLE_RANGE[0]
        self.__lastBackIconIndex = MinimapZIndexManager._BACK_ICONS_RANGE[0]
        self.__markers = {}
        self.__flags = {}
        self.__animations = {}

    def getTeamPointIndex(self):
        self.__lastPointIndex += 1
        return self.__lastPointIndex

    def getVehicleIndex(self, id):
        if id not in self.__indexes:
            self.__indexes[id] = self.__lastVehIndex
            self.__lastVehIndex += 1
        return self.__indexes[id]

    def getDeadVehicleIndex(self, id):
        if id not in self.__indexesDead:
            self.__indexesDead[id] = self.__lastDeadVehIndex
            self.__lastDeadVehIndex += 1
        return self.__indexesDead[id]

    def getBackIconIndex(self, id):
        if id not in self.__indexes:
            self.__indexes[id] = self.__lastBackIconIndex
            self.__lastBackIconIndex += 1
        return self.__indexes[id]

    def getMarkerIndex(self, id):
        index = findFirst(lambda idx: idx not in self.__markers.values(), range(*self._MARKER_RANGE))
        if index is not None:
            self.__markers[id] = index
        return index

    def clearMarkerIndex(self, id):
        if id in self.__markers:
            del self.__markers[id]

    def getFlagIndex(self, id):
        index = findFirst(lambda idx: idx not in self.__flags.values(), range(*self._FLAG_RANGE))
        if index is not None:
            self.__flags[id] = index
        return index

    def clearFlagIndex(self, id):
        if id in self.__flags:
            del self.__flags[id]

    def getAnimationIndex(self, id):
        index = findFirst(lambda idx: idx not in self.__animations.values(), range(*self._ANIMATION_RANGE))
        if index is not None:
            self.__animations[id] = index
        return index

    def clearAnimationIndex(self, id):
        if id in self.__animations:
            del self.__animations[id]

    def getIndexByName(self, name):
        return MinimapZIndexManager._FIXED_INDEXES[name]
