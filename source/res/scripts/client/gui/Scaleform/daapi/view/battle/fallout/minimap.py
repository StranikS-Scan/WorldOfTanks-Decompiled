# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/minimap.py
from CTFManager import g_ctfManager
from constants import FLAG_STATE, RESOURCE_POINT_STATE
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import entries
from gui.Scaleform.daapi.view.battle.shared.minimap import plugins
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.battle_control import minimap_utils
from gui.battle_control.battle_constants import NEUTRAL_TEAM, REPAIR_STATE_ID
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_F_STATES = settings.FLAG_ENTRY_STATE
_R_STATES = settings.RESOURCE_ENTRY_STATE

class FalloutMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(FalloutMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = FalloutGlobalSettingsPlugin
        if arenaVisitor.hasFlags():
            setup['vehicles'] = FlagsAndVehiclesPlugin
            setup['personal'] = FlagsAndPersonalEntriesPlugin
            setup['absorption'] = AbsorptionFlagsPlugin
        if arenaVisitor.hasResourcePoints():
            setup['resources'] = ResourcePointsPlugin
        if arenaVisitor.hasRepairPoints():
            setup['repairs'] = RepairPointsPlugin
        return setup


class FalloutGlobalSettingsPlugin(GlobalSettingsPlugin):
    __slots__ = ('__previousSizeSettings', '__onRespawnVisibilityChanged')

    def __init__(self, parentObj):
        super(FalloutGlobalSettingsPlugin, self).__init__(parentObj)
        self.__previousSizeSettings = None
        return

    def start(self):
        super(FalloutGlobalSettingsPlugin, self).start()
        if GUI_SETTINGS.minimapSize:
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is not None:
                ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibilityChanged
        return

    def stop(self):
        if GUI_SETTINGS.minimapSize:
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is not None:
                ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibilityChanged
        super(FalloutGlobalSettingsPlugin, self).stop()
        return

    def __onRespawnVisibilityChanged(self, isVisible):
        if isVisible:
            self.__previousSizeSettings = self._changeSizeSettings('minimapRespawnSize')
        else:
            self._changeSizeSettings(self.__previousSizeSettings)
            self.__previousSizeSettings = None
        return


class AbsorptionFlagsPlugin(common.EntriesPlugin):
    __slots__ = ('__playerVehicleID', '__playerTeam', '__isTeamPlayer')

    def __init__(self, parentObj):
        super(AbsorptionFlagsPlugin, self).__init__(parentObj)
        self.__playerVehicleID = 0
        self.__playerTeam = 0
        self.__isTeamPlayer = False

    def start(self):
        super(AbsorptionFlagsPlugin, self).start()
        self.__playerVehicleID = self._arenaDP.getPlayerVehicleID()
        self.__playerTeam = self._arenaDP.getNumberOfTeam()
        self.__isTeamPlayer = not self._arenaVisitor.isSoloTeam(self.__playerTeam)
        g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround += self.__onFlagDroppedToGround
        g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
        g_ctfManager.onFlagRemoved += self.__onFlagRemoved
        self.__addAbsorptionFlags(g_ctfManager.getVehicleCarriedFlagID(self.__playerVehicleID) is not None)
        return

    def stop(self):
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround -= self.__onFlagDroppedToGround
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        g_ctfManager.onFlagRemoved -= self.__onFlagRemoved
        super(AbsorptionFlagsPlugin, self).stop()

    def __addAbsorptionFlags(self, isCarried=False):
        for pointIndex, (team, position) in self._arenaVisitor.type.getFlagAbsorptionPointsIterator():
            isMyTeam = self.__isTeamPlayer and team in (NEUTRAL_TEAM, self.__playerTeam)
            symbol = _S_NAME.ALLY_ABSORPTION_FLAG if isMyTeam else _S_NAME.ENEMY_ABSORPTION_FLAG
            self.__addAbsorptionMarker(pointIndex, symbol, position)
            self.__setAbsorptionMarkerAnimated(pointIndex, isMyTeam and isCarried)

    def __addAbsorptionMarker(self, flagID, symbol, flagPos):
        matrix = minimap_utils.makePositionMatrix(flagPos)
        self._addEntryEx(flagID, symbol, _C_NAME.FLAGS, matrix, True)

    def __setAbsorptionMarkerAnimated(self, flagID, animated=True):
        model = self._entries.get(flagID)
        if model is not None:
            self._invoke(model.getID(), 'setAnimated', animated)
        return

    def __toggleAbsorptionFlagAnimation(self, vehicleID, isCarried=False):
        if vehicleID == self.__playerVehicleID:
            for pointIndex, (team, _) in self._arenaVisitor.type.getFlagAbsorptionPointsIterator():
                if self.__isTeamPlayer and team in (NEUTRAL_TEAM, self.__playerTeam):
                    self.__setAbsorptionMarkerAnimated(pointIndex, isCarried)

    def __onFlagCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        self.__toggleAbsorptionFlagAnimation(vehicleID, True)

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        self.__toggleAbsorptionFlagAnimation(loserVehicleID)

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        self.__toggleAbsorptionFlagAnimation(vehicleID)

    def __onFlagRemoved(self, flagID, flagTeam, vehicleID):
        self.__toggleAbsorptionFlagAnimation(vehicleID)


class FlagsAndPersonalEntriesPlugin(plugins.PersonalEntriesPlugin):
    __slots__ = ()

    def start(self):
        super(FlagsAndPersonalEntriesPlugin, self).start()
        g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround += self.__onFlagDroppedToGround
        g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
        g_ctfManager.onFlagRemoved += self.__onFlagRemoved

    def stop(self):
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround -= self.__onFlagDroppedToGround
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        g_ctfManager.onFlagRemoved -= self.__onFlagRemoved
        super(FlagsAndPersonalEntriesPlugin, self).stop()

    def initControlMode(self, mode, available):
        super(FlagsAndPersonalEntriesPlugin, self).initControlMode(mode, available)
        playerVehID = self._getPlayerVehicleID()
        if g_ctfManager.getVehicleCarriedFlagID(playerVehID) is not None:
            self.__updateVehicleFlagState(playerVehID, True)
        return

    def __updateVehicleFlagState(self, vehicleID, isBearer=False):
        if vehicleID == self._getPlayerVehicleID():
            animationID = self._getAnimationID()
            if animationID:
                self._invoke(animationID, 'setFlagBearer', isBearer)

    def __onFlagCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        self.__updateVehicleFlagState(vehicleID, True)

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        self.__updateVehicleFlagState(loserVehicleID)

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        self.__updateVehicleFlagState(vehicleID)

    def __onFlagRemoved(self, flagID, flagTeam, vehicleID):
        self.__updateVehicleFlagState(vehicleID)


class FlagsAndVehiclesPlugin(plugins.ArenaVehiclesPlugin):
    __slots__ = ('__playerTeam', '__isTeamPlayer', '__flagEntries')

    def __init__(self, parentObj):
        super(FlagsAndVehiclesPlugin, self).__init__(parentObj)
        self.__playerTeam = 0
        self.__isTeamPlayer = False
        self.__flagEntries = {}

    def start(self):
        super(FlagsAndVehiclesPlugin, self).start()
        self.__playerTeam = self._arenaDP.getNumberOfTeam()
        self.__isTeamPlayer = not self._arenaVisitor.isSoloTeam(self.__playerTeam)
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

        return

    def stop(self):
        g_ctfManager.onFlagSpawning -= self.__onFlagSpawning
        g_ctfManager.onFlagSpawnedAtBase -= self.__onFlagSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagDroppedToGround -= self.__onFlagDroppedToGround
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        g_ctfManager.onFlagRemoved -= self.__onFlagRemoved
        g_ctfManager.onCarriedFlagsPositionUpdated -= self.__onCarriedFlagsPositionUpdated
        super(FlagsAndVehiclesPlugin, self).stop()

    def _notifyVehicleAdded(self, vehicleID):
        flagID = g_ctfManager.getVehicleCarriedFlagID(vehicleID)
        if flagID is not None:
            self.__updateVehicleFlagState(vehicleID, True)
            self.__setFlagVisible(flagID, False)
        return

    def _notifyVehicleRemoved(self, vehicleID):
        flagID = g_ctfManager.getVehicleCarriedFlagID(vehicleID)
        if flagID is not None:
            self.__setFlagVisible(flagID, True)
            self.__updateVehicleFlagState(vehicleID, False)
            if flagID in self.__flagEntries:
                flagPos = g_ctfManager.getFlagMinimapPos(flagID)
                self.__updateMarkerFlagPosition(flagID, flagPos)
        return

    def __onFlagSpawning(self, flagID, _):
        flagPos = self._arenaVisitor.type.getFlagSpawnPoints()[flagID]['position']
        self.__addOrUpdateFlag(flagID, flagPos, _F_STATES.COOLDOWN)

    def __onFlagSpawnedAtBase(self, flagID, flagTeam, flagPos):
        state = self.__getFlagMarkerState(flagTeam)
        self.__addOrUpdateFlag(flagID, flagPos, state)

    def __onFlagCapturedByVehicle(self, flagID, _, vehicleID):
        model = self._entries.get(vehicleID, None)
        flagVisible = False
        if model is not None and not model.isInAoI():
            flagVisible = True
        else:
            self.__updateVehicleFlagState(vehicleID, True)
        self.__setFlagVisible(flagID, flagVisible)
        if vehicleID != self._getPlayerVehicleID():
            state = self.__getFlagMarkerStateByVehicle(vehicleID)
            self.__updateFlagState(flagID, state)
        return

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, _):
        state = self.__getFlagMarkerState(flagTeam)
        self.__updateVehicleFlagState(loserVehicleID)
        self.__addOrUpdateFlag(flagID, flagPos, state)

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        self.__updateVehicleFlagState(vehicleID)
        self.__setFlagVisible(flagID, False)

    def __onFlagRemoved(self, flagID, _, vehicleID):
        self.__setFlagVisible(flagID, False)
        if vehicleID is not None:
            self.__updateVehicleFlagState(vehicleID)
        return

    def __onCarriedFlagsPositionUpdated(self, flagIDs):
        for flagID in flagIDs:
            flagInfo = g_ctfManager.getFlagInfo(flagID)
            vehID = flagInfo['vehicle']
            if vehID is not None and vehID != self._getPlayerVehicleID():
                flagPos = g_ctfManager.getFlagMinimapPos(flagID)
                if flagID in self.__flagEntries:
                    self.__updateMarkerFlagPosition(flagID, flagPos)
                else:
                    state = self.__getFlagMarkerStateByVehicle(vehID)
                    self.__addOrUpdateFlag(flagID, flagPos, state)

        return

    def __updateMarkerFlagPosition(self, flagID, pos):
        item = self.__flagEntries[flagID]
        matrix = minimap_utils.makePositionMatrix(pos)
        self._setMatrix(item, matrix)

    def __addOrUpdateFlag(self, flagID, flagPos, state, isVisible=True):
        if flagID not in self.__flagEntries:
            self.__addFlagEntryMarker(_C_NAME.FLAGS, _S_NAME.FLAG_ENTRY, flagID, flagPos, isVisible)
            self.__updateFlagState(flagID, state)
        else:
            self.__updateFlagState(flagID, state)
            self.__setFlagVisible(flagID, isVisible)
            self.__updateMarkerFlagPosition(flagID, flagPos)

    def __updateFlagState(self, flagID, state):
        if flagID in self.__flagEntries:
            entry = self.__flagEntries[flagID]
            self._invoke(entry, 'setState', state)

    def __addFlagEntryMarker(self, container, symbol, flagID, markerPos, isVisible=True):
        matrix = minimap_utils.makePositionMatrix(markerPos)
        entry = self._addEntry(symbol, container, matrix, isVisible)
        if entry is not None:
            self.__flagEntries[flagID] = entry
        return

    def __setFlagVisible(self, flagID, isVisible=True):
        entry = self.__flagEntries.get(flagID, None)
        if entry is not None:
            self._setActive(entry, isVisible)
        return

    def __getFlagMarkerState(self, flagTeam=0):
        if flagTeam:
            if flagTeam == self.__playerTeam:
                return _F_STATES.ALLY
            return _F_STATES.ENEMY
        return _F_STATES.NEUTRAL

    def __getFlagMarkerStateByVehicle(self, vehicleID):
        battleCtx = self.sessionProvider.getCtx()
        if battleCtx.isObserver(vehicleID):
            state = _F_STATES.NEUTRAL
        else:
            vehicle_team = self._arenaDP.getVehicleInfo(vehicleID).team
            state = _F_STATES.ENEMY if self._arenaDP.isEnemyTeam(vehicle_team) else _F_STATES.ALLY
        return state

    def __updateVehicleFlagState(self, vehicleID, isBearer=False):
        if vehicleID != self._getPlayerVehicleID() and vehicleID in self._entries:
            entry = self._entries[vehicleID]
            self._invoke(entry.getID(), 'setFlagBearer', isBearer)


class ResourcePointsPlugin(common.EntriesPlugin):
    __slots__ = ()

    def start(self):
        super(ResourcePointsPlugin, self).start()
        g_ctfManager.onResPointIsFree += self.__onResPointIsFree
        g_ctfManager.onResPointCooldown += self.__onResPointCooldown
        g_ctfManager.onResPointCaptured += self.__onResPointCaptured
        g_ctfManager.onResPointCapturedLocked += self.__onResPointCapturedLocked
        g_ctfManager.onResPointBlocked += self.__onResPointBlocked
        for pointID, point in g_ctfManager.getResourcePoints():
            pointState = point['state']
            if pointState == RESOURCE_POINT_STATE.FREE:
                state = _R_STATES.READY
            elif pointState == RESOURCE_POINT_STATE.COOLDOWN:
                state = _R_STATES.COOLDOWN
            elif pointState == RESOURCE_POINT_STATE.CAPTURED:
                state = _R_STATES.OWN_MINING if self._arenaDP.isAllyTeam(point['team']) else _R_STATES.ENEMY_MINING
            else:
                state = _R_STATES.CONFLICT
            self.__addResourcePointMarker(pointID, point['minimapPos'], state)

    def stop(self):
        g_ctfManager.onResPointIsFree -= self.__onResPointIsFree
        g_ctfManager.onResPointCooldown -= self.__onResPointCooldown
        g_ctfManager.onResPointCaptured -= self.__onResPointCaptured
        g_ctfManager.onResPointCapturedLocked -= self.__onResPointCapturedLocked
        g_ctfManager.onResPointBlocked -= self.__onResPointBlocked
        super(ResourcePointsPlugin, self).stop()

    def __setResourcePointState(self, pointID, state):
        if pointID in self._entries:
            entryModel = self._entries[pointID]
            self._invoke(entryModel.getID(), 'setState', state)

    def __onResPointIsFree(self, pointID):
        self.__setResourcePointState(pointID, _R_STATES.READY)

    def __onResPointCooldown(self, pointID, _):
        self.__setResourcePointState(pointID, _R_STATES.COOLDOWN)

    def __onResPointCaptured(self, pointID, team):
        state = settings.CAPTURE_STATE_BY_TEAMS[self._arenaDP.isAllyTeam(team)]
        self.__setResourcePointState(pointID, state)

    def __onResPointCapturedLocked(self, pointID, team):
        state = settings.CAPTURE_FROZEN_STATE_BY_TEAMS[self._arenaDP.isAllyTeam(team)]
        self.__setResourcePointState(pointID, state)

    def __onResPointBlocked(self, pointID):
        self.__setResourcePointState(pointID, _R_STATES.CONFLICT)

    def __addResourcePointMarker(self, pointID, pointPos, state):
        matrix = minimap_utils.makePositionMatrix(pointPos)
        self._addEntryEx(pointID, _S_NAME.RESOURCE_POINT, _C_NAME.TEAM_POINTS, matrix, True)
        self.__setResourcePointState(pointID, state)


class RepairPointEntry(entries.MinimapEntry):
    __slots__ = ('_isInCooldown',)

    def __init__(self, entryID, active, matrix=None):
        super(RepairPointEntry, self).__init__(entryID, active, matrix)
        self._isInCooldown = True

    def setCooldown(self, isInCooldown):
        if self._isInCooldown != isInCooldown:
            self._isInCooldown = isInCooldown
            return True
        return False

    def clear(self):
        self._isInCooldown = False
        super(RepairPointEntry, self).clear()


class RepairPointsPlugin(common.EntriesPlugin):
    __slots__ = ()

    def __init__(self, parent):
        super(RepairPointsPlugin, self).__init__(parent, clazz=RepairPointEntry)

    def start(self):
        super(RepairPointsPlugin, self).start()
        self.__addRepairPoints()
        ctrl = self.sessionProvider.dynamic.repair
        if ctrl is not None:
            ctrl.onStateCreated += self.__onRepairPointStateCreated
        return

    def stop(self):
        ctrl = self.sessionProvider.dynamic.repair
        if ctrl is not None:
            ctrl.onStateCreated -= self.__onRepairPointStateCreated
        super(RepairPointsPlugin, self).stop()
        return

    def __addRepairPoints(self):
        playerTeam = self._arenaDP.getNumberOfTeam()
        for index, (team, position) in self._arenaVisitor.type.getRepairPointIterator():
            if team in (NEUTRAL_TEAM, playerTeam):
                symbol = _S_NAME.ALLY_REPAIR_POINT
            else:
                symbol = _S_NAME.ENEMY_REPAIR_POINT
            self.__addRepairEntryMarker(symbol, index, position)
            self.__setRepairPointCooldown(index, False)

    def __onRepairPointStateCreated(self, pointIndex, stateID):
        self.__setRepairPointCooldown(pointIndex, stateID in (REPAIR_STATE_ID.COOLDOWN, REPAIR_STATE_ID.DISABLED))

    def __addRepairEntryMarker(self, symbol, pointID, markerPos):
        matrix = minimap_utils.makePositionMatrix(markerPos)
        self._addEntryEx(pointID, symbol, _C_NAME.TEAM_POINTS, matrix, True)

    def __setRepairPointCooldown(self, pointID, isCooldown=True):
        if pointID in self._entries:
            model = self._entries[pointID]
            if model.setCooldown(isCooldown):
                self._invoke(model.getID(), 'setCooldown', isCooldown)
