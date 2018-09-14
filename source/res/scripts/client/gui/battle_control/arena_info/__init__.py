# Embedded file name: scripts/client/gui/battle_control/arena_info/__init__.py
import BigWorld
import constants

def getClientArena():
    return getattr(BigWorld.player(), 'arena', None)


def getArenaTypeID():
    return getattr(BigWorld.player(), 'arenaTypeID', 0)


def isPlayerTeamKillSuspected():
    return bool(getattr(BigWorld.player(), 'tkillIsSuspected', 0))


def getArenaGuiType():
    return getattr(getClientArena(), 'guiType', constants.ARENA_GUI_TYPE.UNKNOWN)


def getArenaGuiTypeLabel():
    arenaGuiType = getArenaGuiType()
    if arenaGuiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
        label = constants.ARENA_GUI_TYPE_LABEL.LABELS[getArenaGuiType()]
    else:
        label = ''
    return label


def isLowLevelBattle():
    arena, battleLevel = getClientArena(), None
    if arena is not None:
        battleLevel = arena.extraData.get('battleLevel')
    return 0 < battleLevel < 4


def isEventBattle():
    return getArenaGuiType() == constants.ARENA_GUI_TYPE.EVENT_BATTLES


class IArenaController(object):

    def destroy(self):
        pass

    def setBattleCtx(self, battleCtx):
        raise NotImplementedError, 'Routine "setBattleCtx" must be implemented'

    def invalidateArenaInfo(self):
        pass

    def invalidateVehiclesInfo(self, arenaDP):
        pass

    def invalidateStats(self, arenaDP):
        pass

    def addVehicleInfo(self, vo, arenaDP):
        pass

    def invalidateVehicleInfo(self, flags, vo, arenaDP):
        pass

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        pass

    def invalidateVehicleStats(self, flags, vo, arenaDP):
        pass

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        pass

    def invalidateUsersTags(self):
        pass

    def invalidateUserTags(self, user):
        pass

    def spaceLoadStarted(self):
        pass

    def spaceLoadCompleted(self):
        pass

    def updateSpaceLoadProgress(self, progress):
        pass

    def arenaLoadCompleted(self):
        pass

    def updateRespawnVehicles(self, vehsList):
        pass

    def updateRespawnCooldowns(self, cooldowns):
        pass

    def updateRespawnInfo(self, respawnInfo):
        pass

    def updateRespawnRessurectedInfo(self, respawnInfo):
        pass

    def invalidateVehicleInteractiveStats(self):
        pass
