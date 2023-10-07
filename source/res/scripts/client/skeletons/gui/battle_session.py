# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/battle_session.py
import typing
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.interfaces import IAppearanceCacheController, IPointsOfInterestController, IComp7PrebattleSetupController, IComp7VOIPController, IMapZonesController, IProgressionController, IRadarController, ISpawnController, IArenaVehiclesController, IVehicleCountController, IOverrideSettingsController
    from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentsController

class ISharedControllersLocator(object):
    __slots__ = ()

    @property
    def ammo(self):
        raise NotImplementedError

    @property
    def equipments(self):
        raise NotImplementedError

    @property
    def optionalDevices(self):
        raise NotImplementedError

    @property
    def prebattleSetups(self):
        raise NotImplementedError

    @property
    def vehicleState(self):
        raise NotImplementedError

    @property
    def hitDirection(self):
        raise NotImplementedError

    @property
    def arenaLoad(self):
        raise NotImplementedError

    @property
    def arenaPeriod(self):
        raise NotImplementedError

    @property
    def feedback(self):
        raise NotImplementedError

    @property
    def chatCommands(self):
        raise NotImplementedError

    @property
    def messages(self):
        raise NotImplementedError

    @property
    def drrScale(self):
        raise NotImplementedError

    @property
    def privateStats(self):
        raise NotImplementedError

    @property
    def crosshair(self):
        raise NotImplementedError

    @property
    def personalEfficiencyCtrl(self):
        raise NotImplementedError

    @property
    def anonymizerFakesCtrl(self):
        raise NotImplementedError

    @property
    def viewPoints(self):
        raise NotImplementedError

    @property
    def questProgress(self):
        raise NotImplementedError

    @property
    def calloutCtrl(self):
        raise NotImplementedError

    @property
    def areaMarker(self):
        return NotImplementedError

    @property
    def arenaBorder(self):
        raise NotImplementedError

    @property
    def deathzones(self):
        raise NotImplementedError

    @property
    def ingameHelp(self):
        raise NotImplementedError

    @property
    def mapZones(self):
        raise NotImplementedError

    @property
    def aimingSounds(self):
        raise NotImplementedError


class IDynamicControllersLocator(object):
    __slots__ = ()

    @property
    def debug(self):
        raise NotImplementedError

    @property
    def teamBases(self):
        raise NotImplementedError

    @property
    def repair(self):
        raise NotImplementedError

    @property
    def progressTimer(self):
        raise NotImplementedError

    @property
    def maps(self):
        raise NotImplementedError

    @property
    def spectator(self):
        raise NotImplementedError

    @property
    def missions(self):
        raise NotImplementedError

    @property
    def respawn(self):
        raise NotImplementedError

    @property
    def dynSquads(self):
        raise NotImplementedError

    @property
    def battleField(self):
        raise NotImplementedError

    @property
    def progression(self):
        raise NotImplementedError

    @property
    def radar(self):
        raise NotImplementedError

    @property
    def spawn(self):
        raise NotImplementedError

    @property
    def deathScreen(self):
        raise NotImplementedError

    @property
    def vehicleCount(self):
        raise NotImplementedError

    @property
    def battleHints(self):
        raise NotImplementedError

    @property
    def dogTags(self):
        raise NotImplementedError

    @property
    def battleNotifier(self):
        raise NotImplementedError

    @property
    def soundPlayers(self):
        raise NotImplementedError

    @property
    def gameNotifications(self):
        raise NotImplementedError

    @property
    def appearanceCache(self):
        raise NotImplementedError

    @property
    def pointsOfInterest(self):
        raise NotImplementedError

    @property
    def comp7PrebattleSetup(self):
        raise NotImplementedError

    @property
    def comp7VOIPController(self):
        raise NotImplementedError

    @property
    def overrideSettingsController(self):
        raise NotImplementedError

    @property
    def teamBaseRecapturable(self):
        raise NotImplementedError


class ISquadInvitationsHandler(object):
    __slots__ = ()

    def clear(self):
        raise NotImplementedError

    def send(self, uid):
        raise NotImplementedError

    def accept(self, uid):
        raise NotImplementedError

    def reject(self, uid):
        raise NotImplementedError


class IClientArenaVisitor(object):
    __slots__ = ()

    def clear(self):
        raise NotImplementedError

    @property
    def gui(self):
        raise NotImplementedError

    @property
    def bonus(self):
        raise NotImplementedError

    @property
    def type(self):
        raise NotImplementedError

    @property
    def extra(self):
        raise NotImplementedError

    @property
    def vehicles(self):
        raise NotImplementedError

    @property
    def modifiers(self):
        raise NotImplementedError

    def getComponentSystem(self):
        raise NotImplementedError

    def isArenaInWaiting(self):
        raise NotImplementedError

    def hasRage(self):
        raise NotImplementedError

    def hasRespawns(self):
        raise NotImplementedError

    def hasHealthBar(self):
        raise NotImplementedError

    def hasPlayerGroups(self):
        raise NotImplementedError

    def isSoloTeam(self, team):
        raise NotImplementedError

    def getArenaIconKey(self):
        raise NotImplementedError

    def getArenaIcon(self, iconKey):
        raise NotImplementedError

    def getTeamSpawnPoints(self, team):
        raise NotImplementedError

    def getTeamSpawnPointsIterator(self, team):
        raise NotImplementedError

    def getVisibilityMinRadius(self):
        raise NotImplementedError

    def getVehicleCircularAoiRadius(self):
        raise NotImplementedError

    def getArenaSubscription(self):
        raise NotImplementedError

    def getRoundLength(self):
        raise NotImplementedError

    def isBattleEndWarningEnabled(self):
        raise NotImplementedError

    def getArenaUniqueID(self):
        raise NotImplementedError

    def getArenaGuiType(self):
        raise NotImplementedError

    def getArenaBonusType(self):
        raise NotImplementedError

    def getArenaType(self):
        raise NotImplementedError

    def getArenaPeriod(self):
        raise NotImplementedError

    def getArenaPeriodEndTime(self):
        raise NotImplementedError

    def getArenaPeriodLength(self):
        raise NotImplementedError

    def getArenaPeriodAdditionalInfo(self):
        raise NotImplementedError

    def getArenaPositions(self):
        raise NotImplementedError

    def getArenaExtraData(self):
        raise NotImplementedError

    def getArenaModifiers(self):
        raise NotImplementedError

    def getArenaVehicles(self):
        raise NotImplementedError

    def getArenaStatistics(self):
        raise NotImplementedError

    def isArenaFogOfWarEnabled(self):
        raise NotImplementedError

    def hasGameEndMessage(self):
        raise NotImplementedError

    def hasDogTag(self):
        raise NotImplementedError

    def hasDynSquads(self):
        raise NotImplementedError

    def hasBattleNotifier(self):
        raise NotImplementedError

    def hasPointsOfInterest(self):
        raise NotImplementedError


class IBattleClientCache(object):

    def getRecord(self, recordClass):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError


class IArenaDataProvider(object):
    __slots__ = ()

    def clearInfo(self):
        raise NotImplementedError

    def clearStats(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def defaultInfo(self):
        raise NotImplementedError

    def buildVehiclesData(self, vehicles):
        raise NotImplementedError

    def buildStatsData(self, stats):
        raise NotImplementedError

    def addVehicleInfo(self, vehicleID, vInfo):
        raise NotImplementedError

    def updateVehicleInfo(self, vID, vInfo):
        raise NotImplementedError

    def updateVehicleStatus(self, vID, vInfo):
        raise NotImplementedError

    def updatePlayerStatus(self, vID, vInfo):
        raise NotImplementedError

    def updateVehicleStats(self, vID, vStats):
        raise NotImplementedError

    def updateVehicleInteractiveStats(self, iStats):
        raise NotImplementedError

    def updateGameModeSpecificStats(self, vehicleID, isStatic, stats):
        raise NotImplementedError

    def updateInvitationStatus(self, avatarSessionID, include, exclude=0):
        raise NotImplementedError

    def updateChatCommandState(self, vID, chatCommandState):
        raise NotImplementedError

    def isRequiredDataExists(self):
        raise NotImplementedError

    def getTeamsOnArena(self):
        raise NotImplementedError

    def getAllyTeams(self):
        raise NotImplementedError

    def getEnemyTeams(self):
        raise NotImplementedError

    def isEnemyTeam(self, team):
        raise NotImplementedError

    def isAllyTeam(self, team):
        raise NotImplementedError

    def isMultipleTeams(self):
        raise NotImplementedError

    def getMultiTeamsType(self):
        raise NotImplementedError

    def getMultiTeamsIndexes(self):
        raise NotImplementedError

    def getTeamIDsIterator(self):
        raise NotImplementedError

    def getNumberOfTeam(self, enemy=False):
        raise NotImplementedError

    def getPersonalDescription(self):
        raise NotImplementedError

    def getPlayerVehicleID(self, forceUpdate=False):
        raise NotImplementedError

    def getVehicleInfo(self, vID=None):
        raise NotImplementedError

    def getVehicleStats(self, vID=None):
        raise NotImplementedError

    def getVehiclesCountInPrebattle(self, team, prebattleID):
        raise NotImplementedError

    def getSquadSizes(self):
        raise NotImplementedError

    def getPlayerGuiProps(self, vID, team):
        raise NotImplementedError

    def isSquadMan(self, vID, prebattleID=None):
        raise NotImplementedError

    def isTeamKiller(self, vID):
        raise NotImplementedError

    def isObserver(self, vID):
        raise NotImplementedError

    def isPlayerObserver(self):
        raise NotImplementedError

    def getVehIDByAccDBID(self, accDBID):
        raise NotImplementedError

    def getVehIDBySessionID(self, avatarSessionID):
        raise NotImplementedError

    def getSessionIDByVehID(self, vehID):
        raise NotImplementedError

    def getVehiclesInfoIterator(self):
        raise NotImplementedError

    def getVehiclesStatsIterator(self):
        raise NotImplementedError

    def getVehiclesItemsGenerator(self):
        raise NotImplementedError

    def getActiveVehiclesGenerator(self):
        raise NotImplementedError

    def getAlliesVehiclesNumber(self):
        raise NotImplementedError

    def getEnemiesVehiclesNumber(self):
        raise NotImplementedError

    def isAlly(self, attackerID):
        raise NotImplementedError


class IBattleContext(object):

    def start(self, arenaDP):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def getArenaDP(self):
        raise NotImplementedError

    def getVehIDBySessionID(self, accID):
        raise NotImplementedError

    def getSessionIDByVehID(self, vehID):
        raise NotImplementedError

    def setPlayerFullNameFormatter(self, formatter):
        raise NotImplementedError

    def getVehicleInfo(self, vID=None, avatarSessionID=None):
        raise NotImplementedError

    def getPlayerName(self, vID=None, avatarSessionID=None):
        raise NotImplementedError

    def resetPlayerFullNameFormatter(self):
        raise NotImplementedError

    def createPlayerFullNameFormatter(self, showVehShortName=True, showClan=True, showRegion=True):
        raise NotImplementedError

    def getPlayerFullNameParts(self, vID=None, avatarSessionID=None, pName=None, showVehShortName=True, showClan=True, showRegion=True):
        raise NotImplementedError

    def getPlayerFullName(self, vID=None, avatarSessionID=None, pName=None, showVehShortName=True, showClan=True, showRegion=True):
        raise NotImplementedError

    def isSquadMan(self, vID=None, avatarSessionID=None, prebattleID=None):
        raise NotImplementedError

    def isTeamKiller(self, vID=None, avatarSessionID=None):
        raise NotImplementedError

    def isObserver(self, vID):
        raise NotImplementedError

    def isPlayerObserver(self):
        raise NotImplementedError

    def isInTeam(self, teamIdx, vID=None, avatarSessionID=None):
        raise NotImplementedError

    def isAlly(self, vID=None, avatarSessionID=None):
        raise NotImplementedError

    def isEnemy(self, vID=None, avatarSessionID=None):
        raise NotImplementedError

    def isCurrentPlayer(self, vID):
        raise NotImplementedError

    def getPlayerGuiProps(self, vID, team):
        raise NotImplementedError

    def getArenaTypeName(self, isInBattle=True):
        raise NotImplementedError

    def getArenaDescriptionString(self, isInBattle=True):
        raise NotImplementedError

    def getArenaWinString(self, isInBattle=True):
        raise NotImplementedError

    def getArenaFrameLabel(self):
        raise NotImplementedError

    def getBattleTypeIconPathBig(self):
        raise NotImplementedError

    def getBattleTypeIconPathSmall(self):
        raise NotImplementedError

    def getGuiEventType(self):
        raise NotImplementedError

    def isInvitationEnabled(self):
        raise NotImplementedError

    def hasSquadRestrictions(self):
        raise NotImplementedError

    def getSelectedQuestIDs(self):
        raise NotImplementedError

    def getSelectedQuestInfo(self):
        raise NotImplementedError

    def getTeamName(self, enemy=False):
        raise NotImplementedError

    def getArenaSmallIcon(self):
        raise NotImplementedError

    def getArenaScreenIcon(self):
        raise NotImplementedError

    def getArenaRespawnIcon(self):
        raise NotImplementedError

    def setLastArenaWinStatus(self, winStatus):
        raise NotImplementedError

    def extractLastArenaWinStatus(self):
        raise NotImplementedError


class IBattleSessionProvider(object):
    __slots__ = ('onBattleSessionStart', 'onBattleSessionStop')

    @property
    def shared(self):
        raise NotImplementedError

    @property
    def dynamic(self):
        raise NotImplementedError

    @property
    def arenaVisitor(self):
        raise NotImplementedError

    @property
    def invitations(self):
        raise NotImplementedError

    @property
    def battleCache(self):
        return None

    @property
    def isReplayPlaying(self):
        raise NotImplementedError

    def getCtx(self):
        raise NotImplementedError

    def sendRequest(self, ctx, callback, allowDelay=None):
        raise NotImplementedError

    def setPlayerVehicle(self, vID, vDesc):
        raise NotImplementedError

    def switchVehicle(self, vehicleID):
        raise NotImplementedError

    def getArenaDP(self):
        raise NotImplementedError

    def addArenaCtrl(self, controller):
        raise NotImplementedError

    def removeArenaCtrl(self, controller):
        raise NotImplementedError

    def registerViewComponentsCtrl(self, controller):
        raise NotImplementedError

    def registerViewComponents(self, *data):
        raise NotImplementedError

    def addViewComponent(self, componentID, component, **kwargs):
        raise NotImplementedError

    def removeViewComponent(self, componentID):
        raise NotImplementedError

    def getExitResult(self):
        raise NotImplementedError

    @staticmethod
    def exit():
        raise NotImplementedError

    def start(self, setup):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def switchToPostmortem(self, noRespawnPossible=True, respawnAvailable=False):
        raise NotImplementedError

    def updateVehicleQuickShellChanger(self, isActive):
        raise NotImplementedError

    def movingToRespawnBase(self, vehicle=None):
        raise NotImplementedError

    def invalidateVehicleState(self, state, value, vehicleID=0):
        raise NotImplementedError

    def setVehicleHealth(self, isPlayerVehicle, vehicleID, newHealth, attackerID, attackReasonID):
        raise NotImplementedError

    def repairPointAction(self, repairPointIndex, action, nextActionTime):
        raise NotImplementedError

    def updateAvatarPrivateStats(self, stats):
        raise NotImplementedError

    def addHitDirection(self, hitDirYaw, attackerID, damage, isBlocked, critFlags, isHighExplosive, damagedID, attackReasonID):
        raise NotImplementedError

    def startVehicleVisual(self, vProxy, isImmediate=False):
        raise NotImplementedError

    def stopVehicleVisual(self, vehicleID, isPlayerVehicle):
        raise NotImplementedError

    def handleShortcutChatCommand(self, key):
        raise NotImplementedError

    def handleContexChatCommand(self, key):
        raise NotImplementedError

    def updateVehicleEffects(self, vehicle):
        raise NotImplementedError

    def updateObservedVehicleData(self, vID, extraData):
        raise NotImplementedError
