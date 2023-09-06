# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/tournament/unit/entity.py
import logging
from functools import partial
import datetime
import BigWorld
from client_request_lib.exceptions import ResponseCodes
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui import SystemMessages
from gui.prb_control import prb_getters
from gui.prb_control import settings
from gui.prb_control.entities.base.unit.entity import UnitEntity, UnitEntryPoint, UnitBrowserEntryPoint, UnitBrowserEntity
from gui.prb_control.items import SelectResult
from gui.prb_control.items import ValidationResult, unit_items
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items.unit_items import DynamicRosterSettings
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.prb_control.storages import prequeue_storage_getter
from gui.SystemMessages import SM_TYPE
from gui.shared.utils.requesters.abstract import Response
from helpers import time_utils
from gui.impl import backport
from UnitBase import UNIT_ERROR, UNIT_ROLE
from gui.prb_control.entities.tournament.unit.requester import TournamentUnitRequestProcessor
from gui.prb_control.entities.base.external_battle_unit.base_external_battle_waiting_manager import BaseExternalUnitWaitingManager
from gui.prb_control.entities.tournament.unit.actions_validator import TournamentActionsValidator
from gui.prb_control.entities.tournament.unit.action_handler import TournamentActionsHandler
from gui.prb_control.entities.base.unit.ctx import JoinUnitModeCtx
from gui.wgcg.tournament.contexts import TournamentJoinBattleCtx, TournamentUpdateCtx, SlotVehicleFiltersUpdateCtx, TournamentMatchmakingInfoCtx, TournamentLeaveModeCtx
from gui.impl.gen import R
from gui.prb_control.items.tournament_items import TournamentSettings
_CREATION_TIMEOUT = 30
ERROR_MAX_RETRY_COUNT = 3
SUCCESS_STATUSES = (200, 201, 403, 409)
DEFAULT_OK_WEB_REQUEST_ID = 0
_logger = logging.getLogger(__name__)

class TournamentDynamicRosterSettings(DynamicRosterSettings):

    def __init__(self, unit, tournamentData):
        kwargs = self._extractSettings(unit, tournamentData)
        self._minClanMembersCount = kwargs.pop('minClanMembersCount', None)
        super(DynamicRosterSettings, self).__init__(**kwargs)
        return

    def _extractSettings(self, unit, tournamentData):
        if not tournamentData.isValid():
            _logger.error('Unit roster is not definded')
            return super(TournamentDynamicRosterSettings, self)._extractSettings(unit)
        else:
            kwargs = {}
            roster = None
            if unit is not None:
                roster = unit.getRoster()
            if roster is None:
                _logger.error('Unit roster is not definded')
                return kwargs
            header = tournamentData.getHeader()
            maxSlots = header.getMaxPlayersCount() - 1
            maxEmptySlots = maxSlots - header.getMinPlayersCount()
            minClanMembersCount = header.getMinPlayersCount() - header.getMaxLegionariesCount()
            kwargs['minLevel'] = header.getMinLevel()
            kwargs['maxLevel'] = header.getMaxLevel()
            kwargs['maxSlots'] = maxSlots
            kwargs['maxClosedSlots'] = maxEmptySlots
            kwargs['maxEmptySlots'] = maxEmptySlots
            kwargs['minTotalLevel'] = roster.MIN_UNIT_POINTS_SUM
            kwargs['maxTotalLevel'] = roster.MAX_UNIT_POINTS_SUM
            kwargs['maxLegionariesCount'] = header.getMaxLegionariesCount()
            kwargs['minClanMembersCount'] = minClanMembersCount
            return kwargs

    def getMinClanMembersCount(self):
        return self._minClanMembersCount


class TournamentBrowserEntryPoint(UnitBrowserEntryPoint):

    def __init__(self):
        super(TournamentBrowserEntryPoint, self).__init__(FUNCTIONAL_FLAG.TOURNAMENT, PREBATTLE_TYPE.TOURNAMENT)

    def makeDefCtx(self):
        return JoinUnitModeCtx(self._prbType, flags=self.getFunctionalFlags())


class TournamentEntryPoint(UnitEntryPoint):

    def __init__(self, accountsToInvite=None):
        self.__timeout = None
        self.__currentCtx = None
        self.__isLegionary = False
        super(TournamentEntryPoint, self).__init__(FUNCTIONAL_FLAG.TOURNAMENT, accountsToInvite)
        return

    def makeDefCtx(self):
        return JoinUnitModeCtx(PREBATTLE_TYPE.TOURNAMENT, flags=self.getFunctionalFlags())

    def create(self, ctx, callback=None):
        self.__startProcessingCtx(ctx, callback)

    def join(self, ctx, callback=None):
        self.__startProcessingCtx(ctx, callback)

        def onResponse(response):
            hasErrors = response.getCode() != ResponseCodes.NO_ERRORS
            if hasErrors:
                ctx.stopProcessing()
                self.__cancelProcessingTimeout()
                ctx.callErrorCallback(response.data)

        processor = TournamentUnitRequestProcessor()
        processor.doRequest(TournamentJoinBattleCtx(ctx.getID()), 'join', callback=onResponse)

    def onUnitJoined(self, unitMgrID, prbType):
        self.__cancelProcessingTimeout()

    def __startProcessingCtx(self, ctx, callback):
        self.__currentCtx = ctx
        self.__currentCtx.startProcessing(callback)
        self.__timeout = BigWorld.callback(_CREATION_TIMEOUT, self.__ctxProcessingTimeout)
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.onUnitJoined

    def __cancelProcessingTimeout(self):
        BigWorld.cancelCallback(self.__timeout)
        self.__clear()

    def __ctxProcessingTimeout(self):
        if self.__currentCtx:
            self.__currentCtx.callTimeoutCallback()
            self.__currentCtx.stopProcessing()
        self.__clear()

    def __clear(self):
        self.__timeout = None
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.onUnitJoined
        return


class TournamentBrowserEntity(UnitBrowserEntity):

    def __init__(self):
        super(TournamentBrowserEntity, self).__init__(FUNCTIONAL_FLAG.TOURNAMENT, PREBATTLE_TYPE.TOURNAMENT)

    def canKeepMode(self):
        return False

    def _loadUnit(self):
        g_eventDispatcher.loadTournaments()

    def _unloadUnit(self):
        g_eventDispatcher.removeUnitFromCarousel(self._prbType)

    def _showWindow(self):
        g_eventDispatcher.showTournamentWindow()

    def leave(self, ctx, callback=None):
        processor = TournamentUnitRequestProcessor()
        processor.doRequest(TournamentLeaveModeCtx(ctx.getID()), 'leave_mode')
        super(TournamentBrowserEntity, self).leave(ctx, callback)


class TournamentEntity(UnitEntity):
    MATCHMAKING_BATTLE_BUTTON_BATTLE = 10 * time_utils.ONE_MINUTE
    MATCHMAKING_BATTLE_BUTTON_SORTIE = 10 * time_utils.ONE_MINUTE
    MATCHMAKING_ZERO_TIME_WAITING_FOR_DATA = 5

    class SH_REQUEST_COOLDOWN(object):
        PREBATTLE_ASSIGN = 0.6

    def __init__(self):
        super(TournamentEntity, self).__init__(FUNCTIONAL_FLAG.TOURNAMENT, PREBATTLE_TYPE.TOURNAMENT)
        self.__revisionId = 0
        self.__battleModeData = {}
        self.__waitingManager = BaseExternalUnitWaitingManager()
        self.__errorCount = 0
        self.__timerID = None
        self.__leaveInitiator = False
        self.__isInSlot = False
        self.__isInactiveMatchingButton = True
        self.__prevMatchmakingTimerState = None
        self.__playersMatchingStartedAt = None
        self.__slotVehicleFilters = []
        self.__tournamentSettings = TournamentSettings()
        self.storage = prequeue_storage_getter(QUEUE_TYPE.TOURNAMENT_UNITS)()
        return

    def init(self, ctx=None):
        self.__playersMatchingStartedAt = None
        self.__slotVehicleFilters = []
        self.storage.release()
        ret = super(TournamentEntity, self).init(ctx)
        rev = self._getUnitRevision()
        if rev > 1:
            self.requestUpdateTournament()
            self.requestSlotVehicleFilters()
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived += self.onUnitResponseReceived
            unitMgr.onUnitNotifyReceived += self.onUnitNotifyReceived
        playerInfo = self.getPlayerInfo()
        self.__isInSlot = playerInfo.isInSlot
        if self.canShowTournamentQueue():
            g_eventDispatcher.showTournamentQueue()
        else:
            g_eventDispatcher.loadTournaments()
        self.__tournamentSettings.init()
        return ret

    def fini(self, ctx=None, woEvents=False):
        self.__cancelMatchmakingTimer()
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived -= self.onUnitResponseReceived
            unitMgr.onUnitNotifyReceived -= self.onUnitNotifyReceived
        self.__tournamentSettings.fini()
        self.__playersMatchingStartedAt = None
        self.__slotVehicleFilters = []
        self.storage.fini()
        super(TournamentEntity, self).fini(ctx, woEvents)
        return

    def initEvents(self, listener):
        super(TournamentEntity, self).initEvents(listener)
        if self.canShowMaintenance():
            self._invokeListeners('onTournamentMaintenance', True)
        if self.inPlayersMatchingMode():
            self._invokeListeners('onPlayersMatching', True)

    def onUnitResponseReceived(self, requestID):
        _logger.debug('Unit response requestID = %s', str(requestID))
        self.__waitingManager.onResponseWebReqID(requestID)

    def onUnitNotifyReceived(self, unitMgrID, notifyCode, notifyString, argsList):
        if notifyCode == UNIT_ERROR.FAIL_EXT_UNIT_QUEUE_START and not self.getFlags().isInQueue():
            self.__waitingManager.onResponseError()

    def canShowMaintenance(self):
        return self.__errorCount >= ERROR_MAX_RETRY_COUNT

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.TOURNAMENT:
            g_eventDispatcher.showTournamentWindow()
            SelectResult(True)
        return super(TournamentEntity, self).doSelectAction(action)

    def exitFromPlayersMatchingMode(self):
        self._actionsHandler.exitFromPlayersMatchingMode()

    def getConfirmDialogMeta(self, ctx):
        if self.__errorCount == 0 and self.hasLockedState():
            meta = super(TournamentEntity, self).getConfirmDialogMeta(ctx)
        else:
            meta = None
        return meta

    def getQueueType(self):
        return QUEUE_TYPE.TOURNAMENT_UNITS

    def rejoin(self):
        super(TournamentEntity, self).rejoin()
        if self.isTournamentUnitWaitingForData():
            _logger.debug('force wgsh request on end of battle')
            self.requestUpdateTournament()

    def unit_onUnitFlagsChanged(self, prevFlags, nextFlags):
        _, unit = self.getUnit(safe=False)
        isReady = unit.arePlayersReady(ignored=[settings.CREATOR_SLOT_INDEX])
        flags = unit_items.UnitFlags(nextFlags, prevFlags, isReady)
        isInQueue = flags.isInQueue()
        if flags.isInQueueChanged() and self.isCommander() and not isInQueue:
            self.requestSlotVehicleFilters()
        regularBattleEnd = flags.isArenaFinishedChanged() and flags.isArenaFinished() and flags.isExternalLocked()
        wgshBattleEnd = flags.isExternalLockedStateChanged() and not flags.isExternalLocked()
        if regularBattleEnd or wgshBattleEnd:
            _logger.debug('force wgsh request on end of battle (r,x): %s, %s', str(regularBattleEnd), str(wgshBattleEnd))
            self.requestUpdateTournament()
            self.requestSlotVehicleFilters()
        if flags.isExternalLegionariesMatchingChanged():
            self.__onExternalLegionariesMatchingToggle(flags.isInExternalLegionariesMatching())
        super(TournamentEntity, self).unit_onUnitFlagsChanged(prevFlags, nextFlags)
        if not self.hasLockedState():
            self.resetCoolDown(settings.REQUEST_TYPE.BATTLE_QUEUE)
            self.resetCoolDown(settings.REQUEST_TYPE.DECLINE_SEARCH)
            self.resetCoolDown(settings.REQUEST_TYPE.AUTO_SEARCH)
        if isInQueue:
            self._invokeListeners('onCommanderIsReady', True)
        elif prevFlags != nextFlags and nextFlags == 0:
            self._invokeListeners('onCommanderIsReady', False)

    def unit_onUnitExtraChanged(self, extras):
        super(TournamentEntity, self).unit_onUnitExtraChanged(extras)
        revisionId = extras['rev']
        if revisionId == self.__revisionId:
            return
        self.requestUpdateTournament()
        self.__revisionId = revisionId

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(TournamentEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        diff = prevRoleFlags ^ nextRoleFlags
        if diff & UNIT_ROLE.CREATOR > 0:
            pInfo = self.getPlayerInfo(dbID=playerID)
            if not pInfo.isCommander() and pInfo.isCurrentPlayer():
                SystemMessages.pushMessage(backport.text(R.strings.system_messages.unit.warnings.ANOTHER_PLAYER_BECOME_COMMANDER()))
            elif pInfo.isCommander() and pInfo.isCurrentPlayer():
                self.requestSlotVehicleFilters()

    def unit_onUnitMembersListChanged(self):
        playerInfo = self.getPlayerInfo()
        self.__isInSlot = playerInfo.isInSlot
        super(TournamentEntity, self).unit_onUnitMembersListChanged()

    def request(self, ctx, callback=None):
        self.__waitingManager.processRequest(ctx)

        def wrapper(response):
            if self.__processResponseMessage(response):
                isResponseSubclass = issubclass(type(response), Response)
                if not isResponseSubclass or response.getCode() != ResponseCodes.NO_ERRORS:
                    self.__waitingManager.stopRequest()
                if callback:
                    callback(response)
            else:
                BigWorld.callback(0.0, partial(self.request, ctx, callback))

        super(TournamentEntity, self).request(ctx, wrapper)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        self.__leaveInitiator = True

        def callbackWrapper(response):
            if not self.__processResponseMessage(response):
                super(TournamentEntity, self).leave(ctx, callback)

        if self.__errorCount > 0:
            super(TournamentEntity, self).leave(ctx, callback)
        else:
            ctx.startProcessing(callback)
            self._requestsProcessor.doRequest(ctx, 'leave', callback=callbackWrapper)

    def doBattleQueue(self, ctx, callback=None):
        if ctx.isRequestToStart():
            self.setCoolDown(settings.REQUEST_TYPE.SET_PLAYER_STATE, ctx.getCooldown())
        else:
            if self.isInCoolDown(ctx.getRequestType()):
                return
            self.setCoolDown(ctx.getRequestType(), ctx.getCooldown())
        super(TournamentEntity, self).doBattleQueue(ctx, callback)

    def getMatchmakingInfo(self, callback=None):
        ctx = TournamentMatchmakingInfoCtx(prb_getters.getUnitMgrID())
        self._requestsProcessor.doRequest(ctx, 'matchmakingInfo', callback=callback)

    def setReserve(self, ctx, callback=None):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeConsumables():
            _logger.error('Player can not change consumables %s', str(pPermissions))
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'activateReserve', callback=callback)
        self.setCoolDown(settings.REQUEST_TYPE.SET_RESERVE, coolDown=ctx.getCooldown())

    def unsetReserve(self, ctx, callback=None):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeConsumables():
            _logger.error('Player can not change consumables %s', str(pPermissions))
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'deactivateReserve', callback=callback)
        self.setCoolDown(settings.REQUEST_TYPE.UNSET_RESERVE, coolDown=ctx.getCooldown())

    def assign(self, ctx, callback=None):
        if self.isInCoolDown(settings.REQUEST_TYPE.ASSIGN):
            return
        super(TournamentEntity, self).assign(ctx, callback)
        self.setCoolDown(settings.REQUEST_TYPE.ASSIGN, coolDown=self.SH_REQUEST_COOLDOWN.PREBATTLE_ASSIGN)

    def updateTournamentData(self):
        if self.isTournamentSettingsValid():
            self.__onUpdateHeader()
            self.__onUpdateTimer()
            self.__onUpdateReserve()
            self.__onUpdateState()

    def changeOpened(self, ctx, callback=None):
        self._requestsProcessor.doRequest(ctx, 'openUnit', isOpen=ctx.isOpened(), callback=callback)
        self.setCoolDown(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown())

    def canPlayerDoAction(self):
        if self.__errorCount > 0:
            return ValidationResult(False, UNIT_RESTRICTION.UNIT_MAINTENANCE)
        elif self.isTournamentUnitWaitingForData():
            isPlayerInSlot = self._isPlayerInSlot()
            if isPlayerInSlot and self.isTournamentUnitWaitingForData():
                return ValidationResult(False, UNIT_RESTRICTION.UNIT_WAITINGFORDATA)
            if isPlayerInSlot and self._hasInArenaMembers():
                return ValidationResult(False, UNIT_RESTRICTION.IS_IN_ARENA)
            result = self._actionsValidator.canPlayerDoAction() or ValidationResult(False, UNIT_RESTRICTION.UNDEFINED)
            return ValidationResult(False, result.restriction, result.ctx)
        else:
            return ValidationResult(True, UNIT_RESTRICTION.UNDEFINED)

    def isPlayerJoined(self, ctx):
        return ctx.getCtrlType() is settings.CTRL_ENTITY_TYPE.UNIT and ctx.getEntityType() == self._prbType and ctx.getID() == self.getID()

    def requestMaintenanceUpdate(self):
        self._invokeListeners('onTournamentMaintenance', False)
        self.requestUpdateTournament()

    def requestUpdateTournament(self):
        if self._requestsProcessor:
            unitMgrId = prb_getters.getUnitMgrID()
            rev = self._getUnitRevision()
            ctx = TournamentUpdateCtx(unitMgrId=unitMgrId, rev=rev, waitingID='')
            self._requestsProcessor.doRequest(ctx, 'updateTournament', callback=self.__onTournamentUpdate)

    def tournamentDataChanged(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onTournamentDataChanged')

    def getCandidates(self, unitMgrID=None):
        unitMgrID, unit = self.getUnit(unitMgrID=unitMgrID, safe=True)
        if unit is None:
            return {}
        else:
            players = unit.getPlayers()
            memberIDs = set((value['accountDBID'] for value in unit.getMembers().itervalues()))
            dbIDs = set(players.keys()).difference(memberIDs)
            result = {}
            for dbID, data in players.iteritems():
                if dbID not in dbIDs:
                    continue
                result[dbID] = self._buildPlayerInfo(unitMgrID, unit, dbID, -1, data)

            return result

    def isTournamentUnitWaitingForData(self):
        readyButtonEnabled = True
        flags = self.getFlags()
        return self.canShowMaintenance() or flags.isArenaFinished() and flags.isExternalLocked() or not flags.isInIdle() and not self.getFlags().isInArena() and not flags.isExternalLocked() and not readyButtonEnabled

    def setVehicleTypeFilter(self, ctx, callback=None):
        if self.isInCoolDown(ctx.getRequestType()):
            return

        def _callback(data):
            if callback is not None:
                callback(data)
            self._onPlayersMatchingDataUpdated(data)
            self.__waitingManager.onResponseWebReqID(DEFAULT_OK_WEB_REQUEST_ID)
            return

        self._requestsProcessor.doRequest(ctx, 'setVehicleTypeFilter', callback=_callback)
        self.setCoolDown(settings.REQUEST_TYPE.SET_SLOT_VEHICLE_TYPE_FILTER, coolDown=ctx.getCooldown())

    def setVehiclesFilter(self, ctx, callback=None):
        if self.isInCoolDown(ctx.getRequestType()):
            return

        def _callback(data):
            if callback is not None:
                callback(data)
            self._onPlayersMatchingDataUpdated(data)
            self.__waitingManager.onResponseWebReqID(DEFAULT_OK_WEB_REQUEST_ID)
            return

        self._requestsProcessor.doRequest(ctx, 'setVehiclesFilter', callback=_callback)
        self.setCoolDown(settings.REQUEST_TYPE.SET_SLOT_VEHICLES_FILTER, coolDown=ctx.getCooldown())

    def requestSlotVehicleFilters(self):
        if not self.isCommander():
            return
        if self._requestsProcessor:
            unitMgrId = prb_getters.getUnitMgrID()
            ctx = SlotVehicleFiltersUpdateCtx(unitMgrId=unitMgrId, waitingID='')
            self._requestsProcessor.doRequest(ctx, 'getSlotVehicleFilters', callback=self._onPlayersMatchingDataUpdated)

    def stopPlayersMatching(self, ctx, callback=None):
        self._requestsProcessor.doRequest(ctx, 'stopPlayersMatching', callback=callback)
        self.setCoolDown(settings.REQUEST_TYPE.STOP_PLAYERS_MATCHING, coolDown=ctx.getCooldown())

    def getSecondsCountInPlayersMatching(self):
        if self.__playersMatchingStartedAt is None:
            return 0
        else:
            delta = datetime.datetime.utcnow() - self.__playersMatchingStartedAt
            return abs(int(delta.total_seconds()))

    def inPlayersMatchingMode(self):
        return self.getFlags().isInExternalLegionariesMatching()

    def getSlotsInPlayersMatching(self):
        return [ slot_id for slot_id in self.getSlotFilters().keys() ]

    def getSlotFilters(self):
        slotFilters = {item['slot_id']:{'vehicle_types': item['vehicle_types'],
         'vehicle_cds': item['vehicle_cds']} for item in self.__slotVehicleFilters}
        return slotFilters

    def getTournamentSettings(self):
        return self.__tournamentSettings

    def isTournamentSettingsValid(self):
        return self.__tournamentSettings.isValid()

    def isTournamentUnitFreezed(self):
        return self.getFlags().isExternalLocked()

    def isFirstBattle(self):
        return self.__tournamentSettings.isFirstBattle()

    def isSortie(self):
        return self.__tournamentSettings.isSortie()

    def getRosterSettings(self):
        return self._rosterSettings

    def hasLockedState(self):
        _hasLockedState = super(TournamentEntity, self).hasLockedState()
        pInfo = self.getPlayerInfo()
        flags = self.getFlags()
        return _hasLockedState or pInfo.isInSlot and flags.isInExternalLegionariesMatching()

    def canShowTournamentQueue(self):
        pInfo = self.getPlayerInfo()
        return self.isInQueue() and pInfo.isInSlot

    def _onPlayersMatchingDataUpdated(self, response):
        if not self.__processResponseMessage(response):
            return
        if response.getCode() != ResponseCodes.NO_ERRORS:
            return
        self.__slotVehicleFilters = response.getData()
        self._invokeListeners('onSlotVehileFiltersChanged')

    def _createActionsValidator(self):
        return TournamentActionsValidator(self)

    def _isPlayerInSlot(self):
        return self.__isInSlot

    def _hasInArenaMembers(self):
        flags = self.getFlags()
        return not flags.isArenaFinished() and flags.isExternalLocked() and not self._isInQueue() or flags.isInArena()

    def _isInQueue(self):
        return self.getFlags().isInIdle() and not self.getFlags().isInArena()

    def _updateMatchmakingTimer(self):
        self.__cancelMatchmakingTimer()
        tempInactiveMatchingButton = self.__isInactiveMatchingButton
        if tempInactiveMatchingButton != self.__isInactiveMatchingButton:
            self._invokeListeners('onTournamentOnReadyStateChanged')
        self.__timerID = BigWorld.callback(1.0, self._updateMatchmakingTimer)

    def _createActionsHandler(self):
        return TournamentActionsHandler(self)

    def _getClanMembers(self):
        _, unit = self.getUnit(safe=False)
        members = [ member['accountDBID'] for member in unit.getMembers().itervalues() ]
        clanMembers = []
        for memberDBID in members:
            pInfo = self.getPlayerInfo(dbID=memberDBID)
            if not pInfo.isLegionary():
                clanMembers.append(memberDBID)

        return (members, clanMembers)

    def _getRequestHandlers(self):
        RQ_TYPE = settings.REQUEST_TYPE
        handlers = super(TournamentEntity, self)._getRequestHandlers()
        handlers.update({RQ_TYPE.SET_RESERVE: self.setReserve,
         RQ_TYPE.UNSET_RESERVE: self.unsetReserve,
         RQ_TYPE.SET_SLOT_VEHICLE_TYPE_FILTER: self.setVehicleTypeFilter,
         RQ_TYPE.SET_SLOT_VEHICLES_FILTER: self.setVehiclesFilter,
         RQ_TYPE.STOP_PLAYERS_MATCHING: self.stopPlayersMatching})
        return handlers

    def _buildPlayerInfo(self, unitMgrID, unit, dbID, slotIdx=-1, data=None):
        cmderDBID = unit.getCommanderDBID()
        commander = unit.getPlayer(cmderDBID)
        player = unit.getPlayer(dbID)
        if player and commander and data:
            if commander['clanDBID'] != player['clanDBID']:
                data['role'] |= UNIT_ROLE.LEGIONARY
            else:
                data['role'] &= ~UNIT_ROLE.LEGIONARY
        return super(TournamentEntity, self)._buildPlayerInfo(unitMgrID, unit, dbID, slotIdx=slotIdx, data=data)

    def _getRequestProcessor(self):
        return TournamentUnitRequestProcessor()

    def _getCurrentUTCTime(self):
        return (time_utils.getDateTimeInUTC(time_utils.getServerUTCTime()), datetime.datetime.utcnow())

    def _convertUTCStructToLocalTimestamp(self, val):
        val = time_utils.utcToLocalDatetime(val).timetuple()
        return time_utils.getTimestampFromLocal(val)

    def _getUnitRevision(self):
        extra = self.getExtra()
        return extra.rev if extra is not None else 0

    def __onTournamentUpdate(self, response):
        if not self.__processResponseMessage(response):
            BigWorld.callback(0.0, self.requestUpdateTournament)
            return
        else:
            rawData = response.getData()
            if response.getCode() != ResponseCodes.NO_ERRORS and not rawData:
                return
            self.__waitingManager.onResponseWebReqID(DEFAULT_OK_WEB_REQUEST_ID)
            _, unit = self.getUnit(unitMgrID=None, safe=True)
            if unit is None:
                return
            if not self.__isMatchmakingTimerLoopExist():
                self._updateMatchmakingTimer()
            return

    def __processResponseMessage(self, response):
        if isinstance(response, Response):
            hasErrors = response.getCode() != ResponseCodes.NO_ERRORS
            if hasErrors and response.extraCode not in SUCCESS_STATUSES:
                self.__errorCount += 1
                if self.canShowMaintenance():
                    self._invokeListeners('onTournamentMaintenance', True)
                    return True
                return False
            self.__errorCount = 0
            data = response.getData()
            if isinstance(data, dict):
                webReqID = data.get('web_request_id')
                if webReqID is not None:
                    _logger.debug('Web response requestID = {%s}', str(webReqID))
                    self.__waitingManager.onResponseWebReqID(webReqID)
                if 'extra_data' in data:
                    data = data['extra_data']
                    if not isinstance(data, dict):
                        data = {'description': data}
                txtMsg = data.get('description') or data.get('title')
                if txtMsg:
                    notificationType = SM_TYPE.lookup(data.get('notification_type'))
                    if notificationType not in [SM_TYPE.Error, SM_TYPE.Warning, SM_TYPE.Information]:
                        notificationType = SM_TYPE.Error
                    SystemMessages.pushMessage(txtMsg, type=notificationType)
            if response.getCode() != ResponseCodes.NO_ERRORS:
                self.__waitingManager.onResponseError()
        return True

    def __onReadyButtonEnabled(self):
        self._invokeListeners('onTournamentOnReadyStateChanged')

    def __isMatchmakingTimerLoopExist(self):
        return self.__timerID is not None

    def __cancelMatchmakingTimer(self):
        if self.__timerID is not None:
            BigWorld.cancelCallback(self.__timerID)
            self.__timerID = None
        return

    def __onUpdateHeader(self):
        header = self.__tournamentSettings.getHeader()
        isFirstBattle = self.isFirstBattle()
        battleIdx = header.getBattleIdx()
        flags = self.getFlags()
        if battleIdx == 0 or flags.isInArena() or flags.isInQueue():
            self.storage.setActiveAnimationIdx(battleIdx)
        self._invokeListeners('onUpdateHeader', header, isFirstBattle, self.isTournamentUnitFreezed())

    def __onUpdateTimer(self):
        self._invokeListeners('onUpdateTimer', self.__tournamentSettings.getTimer())

    def __onUpdateState(self):
        state = self.__tournamentSettings.getState()
        self._invokeListeners('onUpdateState', state)

    def __onUpdateReserve(self):
        self._invokeListeners('onUpdateReserve', self.__tournamentSettings.getReserve(), self.__tournamentSettings.getReserveOrder())

    def __onExternalLegionariesMatchingToggle(self, inExternalLegionariesMatching):
        if inExternalLegionariesMatching:
            self.__playersMatchingStartedAt = datetime.datetime.utcnow()
        else:
            self.__playersMatchingStartedAt = None
        if self.isCommander() and not inExternalLegionariesMatching:
            self.requestSlotVehicleFilters()
        return
