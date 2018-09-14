# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/minimap.py
from CTFManager import g_ctfManager
from constants import FLAG_STATE, FLAG_TYPES
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap import plugins, settings
from gui.battle_control import minimap_utils
from gui.Scaleform.daapi.view.battle.event_mark1 import common
from gui.battle_control import g_sessionProvider
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_MARK1_VEHICLE_LINKAGE = 'vehicleMarkerMark1UI'

class Mark1MinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(Mark1MinimapComponent, self)._setupPlugins(arenaVisitor)
        if arenaVisitor.hasFlags():
            setup['vehicles'] = Mark1FlagsVehiclesBonusesPlugin
        return setup


class Mark1ArenaVehiclesPlugin(plugins.ArenaVehiclesPlugin):
    __slots__ = ('__playerVehicleID', '__mark1Entries')

    def __init__(self, parent):
        super(Mark1ArenaVehiclesPlugin, self).__init__(parent)
        self.__playerVehicleID = 0
        self.__mark1Entries = set()

    def start(self):
        super(Mark1ArenaVehiclesPlugin, self).start()
        self.__playerVehicleID = self._arenaDP.getPlayerVehicleID()
        g_ctfManager.onFlagSpawning += self.__onFlagSpawning
        g_ctfManager.onFlagSpawnedAtBase += self.__onFlagSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround += self.__onFlagDroppedToGround
        g_ctfManager.onFlagRemoved += self.__onFlagRemoved

    def stop(self):
        g_ctfManager.onFlagSpawning -= self.__onFlagSpawning
        g_ctfManager.onFlagSpawnedAtBase -= self.__onFlagSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround -= self.__onFlagDroppedToGround
        g_ctfManager.onFlagRemoved -= self.__onFlagRemoved
        self.__mark1Entries.clear()
        super(Mark1ArenaVehiclesPlugin, self).stop()

    def _notifyEntryAddedToPool(self, vehicleID, entryID):
        flagID = g_ctfManager.getVehicleCarriedFlagID(self._arenaDP.getPlayerVehicleID())
        state = self.__getEntryState(vehicleID, flagID is not None)
        self.__setState(entryID, state)
        return

    def _addEntryEx(self, uniqueID, symbol, container, matrix=None, active=False):
        vTypeInfoVO = self._arenaDP.getVehicleInfo(uniqueID).vehicleType
        if vTypeInfoVO.isMark1:
            symbol = common.MINIMAP_MARK1_ENTRY
            self.__mark1Entries.add(uniqueID)
        elif symbol == _S_NAME.VEHICLE:
            symbol = _MARK1_VEHICLE_LINKAGE
        return super(Mark1ArenaVehiclesPlugin, self)._addEntryEx(uniqueID, symbol, container, matrix, active)

    def __onFlagSpawning(self, flagID, respawnTime):
        if common.isFlagNeedsUpdate(flagID):
            self.__updateEntries(False)

    def __onFlagSpawnedAtBase(self, flagID, flagTeam, flagPos):
        if common.isFlagNeedsUpdate(flagID):
            self.__updateEntries(False)

    def __onFlagCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        if vehicleID == self.__playerVehicleID:
            self.__updateEntries(True)

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        if common.isFlagNeedsUpdate(flagID):
            self.__updateEntries(False)

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        if loserVehicleID == self.__playerVehicleID:
            self.__updateEntries(False)

    def __onFlagRemoved(self, flagID, flagTeam, vehicleID):
        self.__updateEntries(False)

    def __setState(self, entryID, state):
        if state is not None:
            self._invoke(entryID, 'setState', state)
        return

    def __updateEntries(self, flagBearer):
        for markVehicleID in self.__mark1Entries:
            state = self.__getEntryState(markVehicleID, flagBearer)
            self.__setState(self._entries[markVehicleID].getID(), state)

    def __getEntryState(self, vehicleID, flagBearer):
        vTypeInfoVO = self._arenaDP.getVehicleInfo(vehicleID).vehicleType
        if vTypeInfoVO.isMark1:
            if flagBearer:
                result = common.MINIMAP_ENTRY_STATE_ABSORPTION
            elif common.isRepairKitInGame():
                result = common.MINIMAP_ENTRY_STATE_ALERT
            else:
                battleCtx = g_sessionProvider.getCtx()
                isAlly = battleCtx.isAlly(vehicleID)
                if isAlly:
                    result = common.MINIMAP_ENTRY_STATE_MARK1_ALLY
                else:
                    result = common.MINIMAP_ENTRY_STATE_MARK1_ENEMY
        else:
            result = None
        return result


class Mark1FlagsAndVehiclesPlugin(Mark1ArenaVehiclesPlugin):
    __slots__ = ('__playerTeam', '__isTeamPlayer', '__flagEntries')

    def __init__(self, parentObj):
        super(Mark1FlagsAndVehiclesPlugin, self).__init__(parentObj)
        self.__playerTeam = 0
        self.__isTeamPlayer = False
        self.__flagEntries = {}

    def start(self):
        super(Mark1FlagsAndVehiclesPlugin, self).start()
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
        super(Mark1FlagsAndVehiclesPlugin, self).stop()

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

    def __onFlagSpawning(self, flagID, respawnTime):
        flagPos = self._arenaVisitor.type.getFlagSpawnPoints()[flagID]['position']
        state = self.__getFlagMarkerState(flagID)
        self.__addOrUpdateFlag(flagID, flagPos, state)
        self.__moveToTop(flagID)

    def __onFlagSpawnedAtBase(self, flagID, flagTeam, flagPos):
        state = self.__getFlagMarkerState(flagID, flagTeam)
        self.__addOrUpdateFlag(flagID, flagPos, state)
        self.__moveToTop(flagID)

    def __moveToTop(self, flagID):
        """
        Moves to top layer already existing flag entries
        :param flagID: flag id
        """
        if flagID in self.__flagEntries:
            flagType = g_ctfManager.getFlagType(flagID)
            if flagType == FLAG_TYPES.REPAIR_KIT or flagType == FLAG_TYPES.EXPLOSIVE:
                entryID = self.__flagEntries[flagID]
                self._invoke(entryID, 'moveToTop')

    def __onFlagCapturedByVehicle(self, flagID, _, vehicleID):
        model = self._entries.get(vehicleID, None)
        flagVisible = False
        if model is not None and not model.isInAoI():
            flagVisible = True
        else:
            self.__updateVehicleFlagState(vehicleID, True)
        self.__setFlagVisible(flagID, flagVisible)
        if vehicleID != self._getPlayerVehicleID():
            state = self.__getFlagMarkerState(flagID)
            self.__updateFlagState(flagID, state)
        return

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, _):
        state = self.__getFlagMarkerState(flagID, flagTeam)
        self.__updateVehicleFlagState(loserVehicleID)
        self.__addOrUpdateFlag(flagID, flagPos, state)

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        if common.isFlagNeedsUpdate(flagID):
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
                    state = self.__getFlagMarkerState(flagID)
                    self.__addOrUpdateFlag(flagID, flagPos, state)

        return

    def __updateMarkerFlagPosition(self, flagID, pos):
        item = self.__flagEntries[flagID]
        matrix = minimap_utils.makePositionMatrix(pos)
        self._setMatrix(item, matrix)

    def __addOrUpdateFlag(self, flagID, flagPos, state, isVisible=True):
        if flagID not in self.__flagEntries:
            flagType = g_ctfManager.getFlagType(flagID)
            if flagType == FLAG_TYPES.OTHER:
                cName = _C_NAME.TEAM_POINTS
            else:
                cName = _C_NAME.FLAGS
            self.__addFlagEntryMarker(cName, common.MINIMAP_MARK1_FLAG, flagID, flagPos, isVisible)
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

    def __getFlagMarkerState(self, flagID, flagTeam=0):
        if not flagTeam:
            flagTeam = g_ctfManager.getFlagInfo(flagID)['team']
        flagType = g_ctfManager.getFlagType(flagID)
        return common.getMark1FlagType(flagType, flagTeam == self.__playerTeam)

    def __updateVehicleFlagState(self, vehicleID, isBearer=False):
        if vehicleID != self._getPlayerVehicleID() and vehicleID in self._entries:
            entry = self._entries[vehicleID]
            if isBearer:
                flagType = self.__getFlagTypeByVehicle(vehicleID)
            else:
                flagType = ''
            self._invoke(entry.getID(), 'setFlagBearer', isBearer, flagType)
            if isBearer:
                self._invoke(entry.getID(), 'moveToTop')

    @staticmethod
    def __getFlagTypeByVehicle(vehicleID):
        flagID = g_ctfManager.getVehicleCarriedFlagID(vehicleID)
        result = ''
        if flagID is not None:
            ctx = g_sessionProvider.getCtx()
            flagType = g_ctfManager.getFlagType(flagID)
            result = common.getMark1FlagType(flagType, ctx.isAlly(vehicleID))
        return result


class Mark1FlagsVehiclesBonusesPlugin(Mark1FlagsAndVehiclesPlugin):

    def start(self):
        super(Mark1FlagsVehiclesBonusesPlugin, self).start()
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            bonusCtrl.onBonusBigGunTaken += self.__onBonusBigGunTaken
            bonusCtrl.onBonusMachineGunTaken += self.__onBonusMachineGunTaken
            bonusCtrl.onBonusEnded += self.__onBonusEnded
        return

    def stop(self):
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            bonusCtrl.onBonusBigGunTaken -= self.__onBonusBigGunTaken
            bonusCtrl.onBonusMachineGunTaken -= self.__onBonusMachineGunTaken
            bonusCtrl.onBonusEnded -= self.__onBonusEnded
        super(Mark1FlagsVehiclesBonusesPlugin, self).stop()
        return

    def _notifyVehicleAdded(self, vehicleID):
        super(Mark1FlagsVehiclesBonusesPlugin, self)._notifyVehicleAdded(vehicleID)
        bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
        if bonusCtrl is not None:
            bonus = bonusCtrl.getVehicleBonus(vehicleID)
            isBearer = bonus is not None
            self.__updateBonus(vehicleID, isBearer, common.BONUS_EXTRA_TO_NAME[bonus])
        return

    def __onBonusBigGunTaken(self, vehicleID):
        if vehicleID != self._getPlayerVehicleID():
            self.__updateBonus(vehicleID, True, common.BONUS_NAMES.BIG_GUN)

    def __onBonusMachineGunTaken(self, vehicleID):
        if vehicleID != self._getPlayerVehicleID():
            self.__updateBonus(vehicleID, True, common.BONUS_NAMES.MACHINE_GUN)

    def __onBonusEnded(self, vehicleID):
        if vehicleID != self._getPlayerVehicleID():
            self.__updateBonus(vehicleID, False, '')

    def __updateBonus(self, vehicleID, isBearer, bonus):
        if vehicleID in self._entries:
            entry = self._entries[vehicleID]
            if entry.isActive():
                self._invoke(entry.getID(), 'updateBonusBearerState', isBearer, bonus)
