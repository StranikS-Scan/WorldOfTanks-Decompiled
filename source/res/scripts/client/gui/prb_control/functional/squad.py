# Embedded file name: scripts/client/gui/prb_control/functional/squad.py
import BigWorld
from account_helpers import gameplay_ctx
from debug_utils import LOG_ERROR
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.prb_control import events_dispatcher, getPrebattleRosters
from gui.prb_control import getClientPrebattle, getPrebattleType, prb_cooldown
from gui.prb_control.context import prb_ctx
from gui.prb_control.items import prb_items
from gui.prb_control.functional.decorators import vehicleAmmoCheck
from gui.prb_control.functional.default import PrbEntry, PrbFunctional
from gui.prb_control.restrictions.permissions import SquadPrbPermissions
from gui.prb_control.restrictions.limits import SquadLimits
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE
from gui.prb_control.settings import FUNCTIONAL_INIT_RESULT
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent

class SquadEntry(PrbEntry):

    def doAction(self, action, dispatcher = None):
        result = False
        if action.actionName == PREBATTLE_ACTION_NAME.SQUAD:
            ctx = prb_ctx.SquadSettingsCtx(waitingID='prebattle/create')
            if dispatcher is not None:
                if dispatcher._setRequestCtx(ctx):
                    self.create(ctx)
            else:
                LOG_ERROR('Prebattle dispatcher is required')
            result = True
        return result

    def create(self, ctx, callback = None):
        if not isinstance(ctx, prb_ctx.SquadSettingsCtx):
            LOG_ERROR('Invalid context to create squad', ctx)
            if callback:
                callback(False)
        elif prb_cooldown.validatePrbCreationCooldown():
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
        LOG_ERROR('Player can join to squad by invite')
        if callback:
            callback(False)


class SquadFunctional(PrbFunctional):

    def __init__(self, settings):
        requests = {REQUEST_TYPE.SET_TEAM_STATE: self.setTeamState,
         REQUEST_TYPE.SET_PLAYER_STATE: self.setPlayerState,
         REQUEST_TYPE.KICK: self.kickPlayer,
         REQUEST_TYPE.SEND_INVITE: self.sendInvites}
        super(SquadFunctional, self).__init__(settings, permClass=SquadPrbPermissions, requestHandlers=requests, limits=SquadLimits(self))
        self.__doTeamReady = False

    def init(self, clientPrb = None, ctx = None):
        result = super(SquadFunctional, self).init(clientPrb=clientPrb)
        isInvitesOpen = False
        if ctx is not None:
            isInvitesOpen = ctx.getRequestType() is REQUEST_TYPE.CREATE
        if self.getPlayerInfo().isReady() and self.getTeamState(team=1).isInQueue():
            events_dispatcher.loadBattleQueue()
        else:
            events_dispatcher.loadHangar()
        events_dispatcher.loadSquad(isInvitesOpen=isInvitesOpen)
        g_eventBus.addListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        result = FUNCTIONAL_INIT_RESULT.addIfNot(result, FUNCTIONAL_INIT_RESULT.LOAD_WINDOW)
        result = FUNCTIONAL_INIT_RESULT.addIfNot(result, FUNCTIONAL_INIT_RESULT.LOAD_PAGE)
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
            events_dispatcher.unloadSquad()
        else:
            events_dispatcher.removeSquadFromCarousel()
        g_eventBus.removeListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)

    @vehicleAmmoCheck
    def setPlayerState(self, ctx, callback = None):
        super(SquadFunctional, self).setPlayerState(ctx, callback)

    def showGUI(self):
        events_dispatcher.loadSquad()

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
            notReadyCount = stats.notReadyCount
            if not self.getPlayerInfo().isReady():
                notReadyCount -= 1
            if notReadyCount > 0:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers', messageCtx={'notReadyCount': notReadyCount,
                 'playersCount': stats.playersCount}), self.__setCreatorReady)
                return True
            self.__setCreatorReady(True)
        elif self.getPlayerInfo().isReady():
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(True, waitingID='prebattle/player_ready'))
        return True

    def exitFromQueue(self):
        if self.isCreator():
            self.setTeamState(prb_ctx.SetTeamStateCtx(1, False, waitingID='prebattle/team_not_ready'))
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
        return True

    def prb_onPlayerStateChanged(self, pID, roster):
        super(SquadFunctional, self).prb_onPlayerStateChanged(pID, roster)
        if self.__doTeamReady:
            self.__doTeamReady = False
            self.__setTeamReady()
        events_dispatcher.updateUI()

    def prb_onPlayerRosterChanged(self, pID, prevRoster, roster, actorID):
        super(SquadFunctional, self).prb_onPlayerRosterChanged(pID, prevRoster, roster, actorID)
        events_dispatcher.updateUI()

    def prb_onPlayerRemoved(self, pID, roster, name):
        super(SquadFunctional, self).prb_onPlayerRemoved(pID, roster, name)
        events_dispatcher.updateUI()

    def prb_onTeamStatesReceived(self):
        super(SquadFunctional, self).prb_onTeamStatesReceived()
        events_dispatcher.updateUI()
        if self.getPlayerInfo().isReady() or self.isCreator():
            if self.getTeamState(team=1).isInQueue():
                events_dispatcher.loadBattleQueue()
            else:
                events_dispatcher.loadHangar()

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

    def __handleCarouselInited(self, _):
        events_dispatcher.addSquadToCarousel()
