# Embedded file name: scripts/client/gui/prb_control/functional/squad.py
import BigWorld
import constants
from account_helpers import gameplay_ctx, getPlayerDatabaseID
from debug_utils import LOG_ERROR
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.prb_control import getPrebattleRosters
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control import getClientPrebattle, getPrebattleType, prb_cooldown
from gui.prb_control.context import prb_ctx, SendInvitesCtx
from gui.prb_control.items import prb_items, unit_items
from gui.prb_control.functional.decorators import vehicleAmmoCheck
from gui.prb_control.functional.default import PrbEntry, PrbFunctional
from gui.prb_control.restrictions.permissions import SquadPrbPermissions
from gui.prb_control.restrictions.limits import SquadLimits
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE, PREBATTLE_ACTION_NAME
from gui.prb_control.settings import FUNCTIONAL_INIT_RESULT
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent

class SquadEntry(PrbEntry):

    def makeDefCtx(self):
        return prb_ctx.SquadSettingsCtx('prebattle/create')

    def create(self, ctx, callback = None):
        if prb_cooldown.validatePrbCreationCooldown():
            if callback:
                callback(False)
        elif getClientPrebattle() is None or ctx.isForced():
            ctx.startProcessing(callback=callback)
            BigWorld.player().prb_createSquad()
            prb_cooldown.setPrbCreationCooldown()
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle', getPrebattleType())
            if callback:
                callback(False)
        return

    def join(self, ctx, callback = None):
        LOG_ERROR('Player can not join to squad by invite')
        if callback:
            callback(False)

    def select(self, ctx, callback = None):
        self.create(ctx, callback=callback)


class SquadFunctional(PrbFunctional):
    SLOTS_COUNT = 3

    def __init__(self, settings):
        requests = {REQUEST_TYPE.SET_TEAM_STATE: self.setTeamState,
         REQUEST_TYPE.SET_PLAYER_STATE: self.setPlayerState,
         REQUEST_TYPE.KICK: self.kickPlayer,
         REQUEST_TYPE.SEND_INVITE: self.sendInvites}
        super(SquadFunctional, self).__init__(settings, permClass=SquadPrbPermissions, requestHandlers=requests, limits=SquadLimits(self))
        self.__doTeamReady = False

    def init(self, clientPrb = None, ctx = None):
        result = super(SquadFunctional, self).init(clientPrb=clientPrb)
        isCreationCtx, accountsToInvite = False, []
        if ctx is not None:
            isCreationCtx = ctx.getRequestType() is REQUEST_TYPE.CREATE
            if isCreationCtx:
                accountsToInvite = ctx.getAccountsToInvite()
        if self.getPlayerInfo().isReady() and self.getTeamState(team=1).isInQueue():
            g_eventDispatcher.loadBattleQueue()
        else:
            g_eventDispatcher.loadHangar()
        g_eventDispatcher.loadSquad(isInvitesOpen=isCreationCtx and not accountsToInvite, isReady=self.__isTeamRead())
        g_eventBus.addListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        result = FUNCTIONAL_INIT_RESULT.addIfNot(result, FUNCTIONAL_INIT_RESULT.LOAD_WINDOW)
        result = FUNCTIONAL_INIT_RESULT.addIfNot(result, FUNCTIONAL_INIT_RESULT.LOAD_PAGE)
        g_eventDispatcher.updateUI()
        if accountsToInvite:
            self.request(SendInvitesCtx(accountsToInvite, ''))
        return result

    def isGUIProcessed(self):
        return True

    def canPlayerDoAction(self):
        if self.getTeamState().isInQueue():
            return (False, '')
        return (True, '')

    def fini(self, clientPrb = None, woEvents = False):
        super(SquadFunctional, self).fini(clientPrb=clientPrb, woEvents=woEvents)
        if not woEvents:
            g_eventDispatcher.unloadSquad()
        else:
            g_eventDispatcher.removeSquadFromCarousel()
        g_eventDispatcher.updateUI()
        g_eventBus.removeListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)

    @vehicleAmmoCheck
    def setPlayerState(self, ctx, callback = None):
        super(SquadFunctional, self).setPlayerState(ctx, callback)

    def showGUI(self):
        g_eventDispatcher.loadSquad()

    def getPlayersStateStats(self):
        return self._getPlayersStateStats(PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1)

    def getRosters(self, keys = None):
        rosters = getPrebattleRosters()
        result = {PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1: []}
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            result[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1] = map(lambda accInfo: prb_items.PlayerPrbInfo(accInfo[0], functional=self, roster=PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1, **accInfo[1]), rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1].iteritems())
        return result

    def doAction(self, action = None, dispatcher = None):
        if self.isCreator():
            stats = self.getPlayersStateStats()
            if stats.haveInBattle:
                DialogsInterface.showI18nInfoDialog('squadHavePlayersInBattle', lambda result: None)
                return True
            if stats.playersCount == 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self.__setCreatorReady)
                return True
            notReadyCount = stats.notReadyCount
            if not self.getPlayerInfo().isReady():
                notReadyCount -= 1
            if notReadyCount == 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayer'), self.__setCreatorReady)
                return True
            if notReadyCount > 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers'), self.__setCreatorReady)
                return True
            self.__setCreatorReady(True)
        elif self.getPlayerInfo().isReady():
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(True, waitingID='prebattle/player_ready'))
        return True

    def doSelectAction(self, action):
        result = False
        if action.actionName == PREBATTLE_ACTION_NAME.SQUAD:
            g_eventDispatcher.showSquadWindow()
            result = True
        elif action.actionName == PREBATTLE_ACTION_NAME.JOIN_RANDOM_QUEUE:
            result = True
        return result

    def exitFromQueue(self):
        if self.isCreator():
            self.setTeamState(prb_ctx.SetTeamStateCtx(1, False, waitingID='prebattle/team_not_ready'))
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
        return True

    def getUnitFullData(self, unitIdx = None):
        dbID, rosters = getPlayerDatabaseID(), self.getRosters()
        pInfo = unit_items.PlayerUnitInfo.fromPrbInfo(self.getPlayerInfo())
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]
        unitState = self._buildState()
        unitStats = self._buildStats(accounts)
        slotsIter = self._getSlotsIterator(accounts)
        return (unitState,
         unitStats,
         pInfo,
         slotsIter)

    def kickPlayer(self, ctx, callback = None):
        playerInfo = self.getPlayerInfoByDbID(ctx.getPlayerID())
        super(SquadFunctional, self).kickPlayer(prb_ctx.KickPlayerCtx(playerInfo.accID), ctx.getWaitingID())

    def prb_onPlayerStateChanged(self, pID, roster):
        super(SquadFunctional, self).prb_onPlayerStateChanged(pID, roster)
        if self.__doTeamReady:
            self.__doTeamReady = False
            self.__setTeamReady()
        g_eventDispatcher.updateUI()
        g_eventDispatcher.setSquadTeamReadyInCarousel(self.getPrbType(), self.__isTeamRead())

    def prb_onPlayerRosterChanged(self, pID, prevRoster, roster, actorID):
        super(SquadFunctional, self).prb_onPlayerRosterChanged(pID, prevRoster, roster, actorID)
        g_eventDispatcher.updateUI()

    def prb_onPlayerRemoved(self, pID, roster, name):
        super(SquadFunctional, self).prb_onPlayerRemoved(pID, roster, name)
        g_eventDispatcher.updateUI()
        g_eventDispatcher.setSquadTeamReadyInCarousel(self.getPrbType(), self.__isTeamRead())

    def prb_onPlayerAdded(self, pID, roster):
        super(SquadFunctional, self).prb_onPlayerAdded(pID, roster)
        g_eventDispatcher.setSquadTeamReadyInCarousel(self.getPrbType(), self.__isTeamRead())

    def prb_onTeamStatesReceived(self):
        super(SquadFunctional, self).prb_onTeamStatesReceived()
        g_eventDispatcher.updateUI()
        if self.getPlayerInfo().isReady() or self.isCreator():
            if self.getTeamState(team=1).isInQueue():
                g_eventDispatcher.loadBattleQueue()
            else:
                g_eventDispatcher.loadHangar()

    def _buildState(self):
        return unit_items.UnitState(0, isReady=self.__isTeamRead())

    def _buildStats(self, accounts):
        readyCount = curTotalLevel = 0
        occupiedSlotsCount = len(accounts)
        openedSlotsCount = freeSlotsCount = self.SLOTS_COUNT - occupiedSlotsCount
        for account in accounts:
            if account.isReady():
                readyCount += 1
            if account.isVehicleSpecified():
                curTotalLevel += account.getVehicle().level

        return unit_items.UnitStats(readyCount, occupiedSlotsCount, openedSlotsCount, freeSlotsCount, curTotalLevel, [], 1, self.SLOTS_COUNT * constants.MAX_VEHICLE_LEVEL)

    def _getSlotsIterator(self, accounts):
        for slotIdx, account in enumerate(sorted(accounts, cmp=prb_items.getPlayersComparator())):
            state = unit_items.SlotState(False, False)
            player = unit_items.PlayerUnitInfo.fromPrbInfo(account, slotIdx=slotIdx)
            vehicleUnitData = None
            if account.isVehicleSpecified():
                vehiclePrbItem = account.getVehicle()
                vehicleUnitData = {'vehLevel': vehiclePrbItem.level,
                 'inNationIdx': vehiclePrbItem.innationID,
                 'nationIdx': vehiclePrbItem.nationID,
                 'vehInvID': vehiclePrbItem.invID,
                 'vehTypeCompDescr': vehiclePrbItem.intCD,
                 'vehClassIdx': constants.VEHICLE_CLASS_INDICES.get(vehiclePrbItem.type)}
            yield unit_items.SlotInfo(slotIdx, state, player, vehicleUnitData)

        for freeSlotIdx in range(len(accounts), self.SLOTS_COUNT):
            yield unit_items.SlotInfo(freeSlotIdx, unit_items.SlotState(False, True), None, None)

        return

    def __setCreatorReady(self, result):
        if not result:
            return
        if self.getPlayerInfo().isReady():
            self.__setTeamReady()
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(True, waitingID='prebattle/player_ready'), callback=self.__onCreatorReady)

    def __setTeamReady(self):
        if self.isCreator():
            self.setTeamState(prb_ctx.SetTeamStateCtx(1, True, waitingID='prebattle/team_ready', gamePlayMask=gameplay_ctx.getMask()))

    def __onCreatorReady(self, result):
        self.__doTeamReady = result

    def __isTeamRead(self):
        return not self.getPlayersStateStats().notReadyCount

    def __handleCarouselInited(self, _):
        g_eventDispatcher.addSquadToCarousel(self.__isTeamRead())
