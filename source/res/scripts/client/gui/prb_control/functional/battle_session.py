# Embedded file name: scripts/client/gui/prb_control/functional/battle_session.py
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES as I18N_SYSTEM_MESSAGES
from gui.prb_control.context import prb_ctx
from gui.prb_control.functional.decorators import vehicleAmmoCheck
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent
from gui.shared.utils import showInvitationInWindowsBar
from helpers import i18n
from gui import SystemMessages
from gui.prb_control import prb_getters
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import prb_seqs, prb_items, SelectResult
from gui.prb_control.functional.default import PrbEntry, PrbFunctional
from gui.prb_control.functional.interfaces import IPrbListRequester
from gui.prb_control.settings import REQUEST_TYPE, PREBATTLE_ROSTER, PREBATTLE_ACTION_NAME
from gui.prb_control.settings import PREBATTLE_SETTING_NAME, FUNCTIONAL_FLAG
from gui.prb_control.restrictions.limits import BattleSessionLimits
from gui.prb_control.restrictions.permissions import BattleSessionPrbPermissions
from prebattle_shared import decodeRoster

class BattleSessionListEntry(PrbEntry):

    def makeDefCtx(self):
        return prb_ctx.JoinModeCtx(PREBATTLE_TYPE.CLAN)

    def create(self, ctx, callback = None):
        raise Exception, 'BattleSession can be created through the web only'

    def join(self, ctx, callback = None):
        g_eventDispatcher.loadBattleSessionList()
        if callback:
            callback(True)

    def select(self, ctx, callback = None):
        self.join(ctx, callback=callback)


class BattleSessionEntry(PrbEntry):

    def create(self, ctx, callback = None):
        raise Exception, 'BattleSession can be created through the web only'

    def join(self, ctx, callback = None):
        prbID = ctx.getID()
        if not AutoInvitesNotifier.hasInvite(prbID):
            SystemMessages.pushI18nMessage(I18N_SYSTEM_MESSAGES.ARENA_START_ERRORS_JOIN_NOT_FOUND, type=SystemMessages.SM_TYPE.Error)
            if callback:
                callback(False)
            return
        peripheryID = AutoInvitesNotifier.getInvite(prbID).peripheryID
        if g_lobbyContext.isAnotherPeriphery(peripheryID):
            hostName = g_lobbyContext.getPeripheryName(peripheryID)
            if hostName:
                message = i18n.makeString(I18N_SYSTEM_MESSAGES.ARENA_START_ERRORS_JOIN_WRONG_PERIPHERY_KNOWN, hostName)
            else:
                message = i18n.makeString(I18N_SYSTEM_MESSAGES.ARENA_START_ERRORS_JOIN_WRONG_PERIPHERY_UNKNOWN)
            SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Warning)
            if callback:
                callback(False)
        else:
            super(BattleSessionEntry, self).join(ctx, callback)


class AutoInvitesRequester(IPrbListRequester):

    def __init__(self):
        self.__callback = None
        return

    def start(self, callback):
        if callback is not None and callable(callback):
            self.__callback = callback
        else:
            LOG_ERROR('Callback is None or is not callable')
            return
        g_playerEvents.onPrebattleAutoInvitesChanged += self.__pe_onPrbAutoInvitesChanged
        return

    def stop(self):
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.__pe_onPrbAutoInvitesChanged
        self.__callback = None
        return

    def request(self, ctx = None):
        self.__fetchList()

    def getItem(self, prbID):
        return prb_seqs.AutoInviteItem(prbID, **prb_getters.getPrebattleAutoInvites().get(prbID, {}))

    def __pe_onPrbAutoInvitesChanged(self):
        self.__fetchList()

    def __fetchList(self):
        if self.__callback is not None:
            self.__callback(prb_seqs.AutoInvitesIterator())
        return


class AutoInvitesNotifier(object):

    def __init__(self, loader):
        super(AutoInvitesNotifier, self).__init__()
        self.__notified = set()
        self.__isStarted = False
        self.__loader = loader

    def __del__(self):
        LOG_DEBUG('AutoInvitesNotifier deleted')

    def start(self):
        if self.__isStarted:
            self.__doNotify()
            return
        self.__isStarted = True
        g_playerEvents.onPrebattleAutoInvitesChanged += self.__pe_onPrbAutoInvitesChanged
        self.__doNotify()

    def stop(self):
        if not self.__isStarted:
            return
        self.__isStarted = False
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.__pe_onPrbAutoInvitesChanged
        self.__notified.clear()

    def fini(self):
        self.stop()
        self.__loader = None
        return

    def getNotified(self):
        result = []
        for invite in prb_seqs.AutoInvitesIterator():
            if invite.prbID in self.__notified:
                result.append(invite)

        return result

    @classmethod
    def hasInvite(cls, prbID):
        return prbID in prb_getters.getPrebattleAutoInvites()

    @classmethod
    def getInvite(cls, prbID):
        return prb_seqs.AutoInviteItem(prbID, **prb_getters.getPrebattleAutoInvites().get(prbID, {}))

    def canAcceptInvite(self, invite):
        result = True
        dispatcher = self.__loader.getDispatcher()
        if dispatcher:
            prbFunctional = dispatcher.getPrbFunctional()
            unitFunctional = dispatcher.getUnitFunctional()
            if prbFunctional and prbFunctional.hasLockedState() or unitFunctional and unitFunctional.hasLockedState():
                result = False
        peripheryID = invite.peripheryID
        if result and g_lobbyContext.isAnotherPeriphery(peripheryID):
            result = g_lobbyContext.isPeripheryAvailable(peripheryID)
        return result

    def __doNotify(self):
        haveInvites = False
        for invite in prb_seqs.AutoInvitesIterator():
            prbID = invite.prbID
            haveInvites = True
            if prbID in self.__notified:
                continue
            if not len(invite.description):
                continue
            g_eventDispatcher.fireAutoInviteReceived(invite)
            showInvitationInWindowsBar()
            self.__notified.add(prbID)

        if not haveInvites:
            self.__notified.clear()

    def __pe_onPrbAutoInvitesChanged(self):
        self.__doNotify()


class BattleSessionFunctional(PrbFunctional):

    def __init__(self, settings):
        requests = {REQUEST_TYPE.ASSIGN: self.assign,
         REQUEST_TYPE.SET_TEAM_STATE: self.setTeamState,
         REQUEST_TYPE.SET_PLAYER_STATE: self.setPlayerState,
         REQUEST_TYPE.KICK: self.kickPlayer}
        super(BattleSessionFunctional, self).__init__(settings, permClass=BattleSessionPrbPermissions, limits=BattleSessionLimits(self), requestHandlers=requests)

    def init(self, clientPrb = None, ctx = None):
        result = super(BattleSessionFunctional, self).init(clientPrb=clientPrb)
        g_eventDispatcher.loadHangar()
        g_eventDispatcher.loadBattleSessionWindow(self.getEntityType())
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_WINDOW)
        result = FUNCTIONAL_FLAG.addIfNot(result, FUNCTIONAL_FLAG.LOAD_PAGE)
        g_eventBus.addListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventDispatcher.updateUI()
        return result

    def isGUIProcessed(self):
        return True

    def fini(self, clientPrb = None, woEvents = False):
        prbType = self.getEntityType()
        super(BattleSessionFunctional, self).fini(clientPrb=clientPrb, woEvents=woEvents)
        if not woEvents:
            g_eventDispatcher.unloadBattleSessionWindow(prbType)
        else:
            g_eventDispatcher.removeSpecBattleFromCarousel(prbType)
        g_eventDispatcher.updateUI()
        g_eventBus.removeListener(ChannelCarouselEvent.CAROUSEL_INITED, self.__handleCarouselInited, scope=EVENT_BUS_SCOPE.LOBBY)
        return FUNCTIONAL_FLAG.UNDEFINED

    @vehicleAmmoCheck
    def setPlayerState(self, ctx, callback = None):
        super(BattleSessionFunctional, self).setPlayerState(ctx, callback)

    def showGUI(self, ctx = None):
        g_eventDispatcher.loadBattleSessionWindow(self.getEntityType())

    def getRosters(self, keys = None):
        rosters = prb_getters.getPrebattleRosters()
        prbRosters = PREBATTLE_ROSTER.getRange(self.getEntityType(), self.getPlayerTeam())
        result = dict(((r, []) for r in prbRosters))
        for roster in prbRosters:
            if roster in rosters:
                result[roster] = map(lambda accInfo: prb_items.PlayerPrbInfo(accInfo[0], functional=self, roster=roster, **accInfo[1]), rosters[roster].iteritems())

        return result

    def getTeamLimits(self):
        return prb_getters.getPrebattleSettings().getTeamLimits(self.getPlayerTeam())

    def canPlayerDoAction(self):
        isValid, notValidReason = True, ''
        team, assigned = decodeRoster(self.getRosterKey())
        if self.isCreator():
            isValid, notValidReason = self._limits.isTeamValid()
        elif self.getTeamState().isInQueue() and assigned:
            isValid = False
        elif not g_currentVehicle.isReadyToPrebattle():
            isValid = False
        return (isValid, notValidReason)

    def doAction(self, action = None):
        if self.getPlayerInfo().isReady():
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))
        else:
            self.setPlayerState(prb_ctx.SetPlayerStateCtx(True, waitingID='prebattle/player_ready'))
        return True

    def doSelectAction(self, action):
        result = False
        if action.actionName == PREBATTLE_ACTION_NAME.SPEC_BATTLE:
            g_eventDispatcher.showBattleSessionWindow()
            result = True
        return SelectResult(result, None)

    def prb_onSettingUpdated(self, settingName):
        super(BattleSessionFunctional, self).prb_onSettingUpdated(settingName)
        if settingName == PREBATTLE_SETTING_NAME.LIMITS:
            g_eventDispatcher.updateUI()

    def prb_onPlayerStateChanged(self, pID, roster):
        super(BattleSessionFunctional, self).prb_onPlayerStateChanged(pID, roster)
        g_eventDispatcher.updateUI()

    def prb_onRosterReceived(self):
        super(BattleSessionFunctional, self).prb_onRosterReceived()
        g_eventDispatcher.updateUI()

    def prb_onPlayerRosterChanged(self, pID, prevRoster, roster, actorID):
        super(BattleSessionFunctional, self).prb_onPlayerRosterChanged(pID, prevRoster, roster, actorID)
        g_eventDispatcher.updateUI()

    def __handleCarouselInited(self, _):
        g_eventDispatcher.addSpecBattleToCarousel(self.getEntityType())
