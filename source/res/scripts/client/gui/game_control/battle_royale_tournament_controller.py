# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_royale_tournament_controller.py
import logging
import calendar
from collections import Counter
import BigWorld
from gui.prb_control.items import prb_seqs
import AccountCommands
import Event
from adisp import process
from constants import PREBATTLE_TYPE
from gui import SystemMessages
from gui.prb_control.events_dispatcher import g_eventDispatcher
from PlayerEvents import g_playerEvents
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IBattleRoyaleTournamentController
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from BattleRoyaleTournament import BattleRoyaleTourmanentToken
_logger = logging.getLogger(__name__)
_R_BR_TOURNAMENT_TYPE = R.strings.battle_royale.tournament.type
_INVITE_START_ID = 1000000000

class BattleRoyaleTournamentController(IBattleRoyaleTournamentController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__isAvailable = False
        self.__prbType = PREBATTLE_TYPE.BATTLE_ROYALE
        self.__tokens = {}
        self.__currentToken = None
        self.__participants = None
        self.__isReJoin = False
        self.__isChangingInternalState = False
        self.__previousInviteIDs = set()
        self.onUpdatedParticipants = Event.Event()
        self.onSelectBattleRoyaleTournament = Event.Event()
        return

    def onLobbyInited(self, event):
        super(BattleRoyaleTournamentController, self).onLobbyInited(event)
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        g_playerEvents.onCollectPrebattleInvites += self.__onCollectPrebattleInvites
        g_playerEvents.onPrebattleAutoInvitesChanged += self.__onPrebattleAutoInvitesChanged
        g_playerEvents.onPrebattleAutoInvitesChanged()
        if self.__currentToken is not None:
            self.onSelectBattleRoyaleTournament()
        return

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clearInternalData()
        self.__clear()

    def getSelectedToken(self):
        return self.__currentToken

    def isAvailable(self):
        return self.__isAvailable

    def getTokens(self):
        return self.__tokens

    def updateParticipants(self, participants):
        self.__participants = participants
        self.onUpdatedParticipants()

    def getParticipants(self):
        return self.__participants

    def selectBattleRoyaleTournament(self, token):
        if token:
            tokenData = BattleRoyaleTourmanentToken(token)
            if self.__currentToken and self.__currentToken.tournamentID == tokenData.tournamentID:
                return
            self.leaveBattleRoyaleTournament()
            self.__currentToken = tokenData
            self.onSelectBattleRoyaleTournament()
        elif not self.__isChangingInternalState and self.isSelected():
            self.__clearInternalData()
            self.__selectRandom()

    def join(self, tokenStr):
        self.__tournamentComponent.tournamentJoin(tokenStr, self.__joinResult)

    def leave(self):
        self.__tournamentComponent.tournamentLeave(self.__leaveResult)

    def ready(self, vehicleID):
        self.__tournamentComponent.tournamentReady(vehicleID, str(self.__currentToken.tournamentID), self.__readyResult)

    def notReady(self):
        self.__tournamentComponent.tournamentNotReady(str(self.__currentToken.tournamentID), self.__notReadyResult)

    def leaveCurrentAndJoinToAnotherTournament(self, internalTournamentID):
        self.__isReJoin = True
        self.__isChangingInternalState = True
        self.__currentToken = self.__tokens.get(internalTournamentID)
        self.leave()

    def leaveBattleRoyaleTournament(self, isChangingToBattleRoyaleHangar=False):
        if self.__currentToken:
            self.__isChangingInternalState = isChangingToBattleRoyaleHangar
            self.leave()
        self.__currentToken = None
        return

    def isSelected(self):
        return self.__currentToken is not None

    @property
    def __tournamentComponent(self):
        return BigWorld.player().AccountBattleRoyaleTournamentComponent

    def __selectRandom(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            self.__doSelectRandomPrb(dispatcher)
            return

    @process
    def __doSelectRandomPrb(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))

    def __clear(self):
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        g_playerEvents.onCollectPrebattleInvites -= self.__onCollectPrebattleInvites
        g_playerEvents.onPrebattleAutoInvitesChanged += self.__onPrebattleAutoInvitesChanged

    def __clearInternalData(self):
        self.__previousInviteIDs = set()
        self.__currentToken = None
        self.__tokens = {}
        self.__participants = []
        self.__isReJoin = False
        return

    def __onClientUpdated(self, diff, _):
        if 'tokens' not in diff:
            return
        for token in diff['tokens']:
            if BattleRoyaleTourmanentToken(token).isValid:
                g_playerEvents.onPrebattleAutoInvitesChanged()
                return

    def __onPrebattleAutoInvitesChanged(self):
        inviteIDs = {invite.prbID for invite in prb_seqs.AutoInvitesIterator()}
        if inviteIDs != self.__previousInviteIDs:
            self.__previousInviteIDs = inviteIDs
            g_playerEvents.onUpdateSpecBattlesWindow()
            g_eventDispatcher.notifySpecialBattleWindow()

    def __onCollectPrebattleInvites(self, autoInvites):
        self.__isAvailable = False
        for key, invite in autoInvites.items():
            if invite['type'] == PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT:
                autoInvites.pop(key)

        tokens = self.__itemsCache.items.tokens
        parsedTokens = [ BattleRoyaleTourmanentToken(token) for token in tokens.getTokens() if token.startswith('br_trn') and tokens.isTokenAvailable(token) ]
        availableTokens = [ tokenData for tokenData in parsedTokens if tokenData.isValid and not self.__lobbyContext.isAnotherPeriphery(tokenData.peripheryID) ]
        key = lambda v: (v.tournamentID, v.type)
        counts = Counter((key(tokenData) for tokenData in availableTokens))
        currentInviteID = _INVITE_START_ID
        for tokenData in availableTokens:
            if counts[key(tokenData)] > 1:
                sessionName = '{} [{}]'.format(tokenData.tournamentID, tokenData.participantShortDescr)
            else:
                sessionName = str(tokenData.tournamentID)
            typeLabel = _R_BR_TOURNAMENT_TYPE.solo if tokenData.isSolo else _R_BR_TOURNAMENT_TYPE.squad
            descr = {'localized_data': '',
             'descr': {'event_name': backport.text(R.strings.battle_royale.tournament.description()),
                       'session_name': sessionName},
             'type': backport.text(typeLabel())}
            startTimeTimeStamp = calendar.timegm(tokenData.startTime.utctimetuple())
            while currentInviteID in autoInvites:
                currentInviteID += 1

            self.__tokens[currentInviteID] = tokenData
            autoInvites[currentInviteID] = {'peripheryID': tokenData.peripheryID,
             'type': PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT,
             'startTime': startTimeTimeStamp,
             'description': descr,
             'isValid': True,
             'addInfo': tokenData.data}
            self.__isAvailable = True

        if not self.__isAvailable:
            self.leaveBattleRoyaleTournament()
            self.__clearInternalData()
            g_playerEvents.onUpdateSpecBattlesWindow()

    def __joinResult(self, requestID, resultID, errorStr):
        if resultID == AccountCommands.RES_SUCCESS:
            g_eventDispatcher.hideSpecialBattleWindow()
        if resultID == AccountCommands.RES_FAILURE:
            _logger.error('joining to battle royale tournament failed with error = %r', errorStr)
            self.__pushErrorSystemMessage(errorStr)

    def __leaveResult(self, requestID, resultID, errorStr):
        if resultID == AccountCommands.RES_FAILURE:
            _logger.error('leave from current tournament failed with error = %r', errorStr)
            self.__pushErrorSystemMessage(errorStr)
        elif resultID == AccountCommands.RES_SUCCESS:
            if self.__isReJoin:
                self.join(str(self.__currentToken.data))
        self.__isChangingInternalState = False
        self.__isReJoin = False

    def __readyResult(self, requestID, resultID, errorStr):
        if resultID == AccountCommands.RES_FAILURE:
            _logger.error('tournament ready request with failed, str = %r', errorStr)
            self.__pushErrorSystemMessage(errorStr)

    def __notReadyResult(self, requestID, resultID, errorStr):
        if resultID == AccountCommands.RES_FAILURE:
            _logger.error('tournament not ready request fini with failed, str = %r', errorStr)
            self.__pushErrorSystemMessage(errorStr)

    def __pushErrorSystemMessage(self, stringCode):
        _r = R.strings.battle_royale.tournament.notification
        _resId = _r.dyn(stringCode) if _r.dyn(stringCode).exists() else _r.commonErrorMessage
        errorStr = backport.text(_resId(), errorString=stringCode)
        SystemMessages.pushI18nMessage(errorStr, type=SystemMessages.SM_TYPE.Warning, priority='medium')
