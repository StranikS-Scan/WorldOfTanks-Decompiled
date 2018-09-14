# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/entity.py
import BigWorld
import time
import account_helpers
import datetime
from helpers import time_utils
from debug_utils import LOG_DEBUG, LOG_ERROR
from client_request_lib.exceptions import ResponseCodes
from constants import PREBATTLE_TYPE, QUEUE_TYPE, CLAN_MEMBER_FLAGS
from gui.prb_control.items.unit_items import DynamicRosterSettings
from shared_utils import makeTupleByDict
from gui.clans import contexts
from gui.clans.clan_helpers import isStrongholdsEnabled
from gui.shared.utils.requesters.abstract import Response
from UnitBase import UNIT_ROLE
from gui.prb_control import settings
from gui.prb_control import prb_getters
from gui.prb_control.items import ValidationResult, unit_items
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.unit.entity import UnitEntity, UnitEntryPoint, UnitBrowserEntryPoint, UnitBrowserEntity
from gui.prb_control.entities.stronghold.unit.actions_handler import StrongholdActionsHandler
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.prb_control.entities.stronghold.unit.requester import StrongholdUnitRequestProcessor
from gui.prb_control.entities.stronghold.unit.waiting import WaitingManager
from gui.prb_control.entities.stronghold.unit.actions_validator import StrongholdActionsValidator
from gui.prb_control.items.stronghold_items import StrongholdSettings, StrongholdDataDiffer
from gui.prb_control.entities.stronghold.unit.permissions import StrongholdPermissions
from gui.shared.ClanCache import _ClanCache
from gui.Scaleform.daapi.view.dialogs.rally_dialog_meta import StrongholdConfirmDialogMeta
from gui.SystemMessages import SM_TYPE
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from functools import partial
_CREATION_TIMEOUT = 30
ERROR_MAX_RETRY_COUNT = 3
SUCCESS_STATUSES = (200, 201, 403, 409)
MATCHMAKING_BATTLE_BUTTON_BATTLE = 10 * time_utils.ONE_MINUTE
MATCHMAKING_BATTLE_BUTTON_SORTIE = 10 * time_utils.ONE_MINUTE

class StrongholdDynamicRosterSettings(DynamicRosterSettings):

    def __init__(self, unit, strongholdData):
        kwargs = self._extractSettings(unit, strongholdData)
        super(DynamicRosterSettings, self).__init__(**kwargs)

    def _extractSettings(self, unit, strongholdData):
        kwargs = {}
        roster = None
        if unit is not None:
            roster = unit.getRoster()
        if strongholdData is not None:
            maxSlots = strongholdData.getMaxPlayerCount() - 1
            maxEmptySlots = maxSlots - strongholdData.getMinPlayerCount()
            kwargs['minLevel'] = strongholdData.getMinLevel()
            kwargs['maxLevel'] = strongholdData.getMaxLevel()
            kwargs['maxSlots'] = maxSlots
            kwargs['maxClosedSlots'] = maxEmptySlots
            kwargs['maxEmptySlots'] = maxEmptySlots
            kwargs['minTotalLevel'] = roster.MIN_UNIT_POINTS_SUM
            kwargs['maxTotalLevel'] = roster.MAX_UNIT_POINTS_SUM
            kwargs['maxLegionariesCount'] = strongholdData.getMaxLegCount()
        else:
            LOG_ERROR('Unit roster is not defined')
        return kwargs


class StrongholdBrowserEntryPoint(UnitBrowserEntryPoint):
    """
    Strongholds list entry point
    """

    def __init__(self):
        super(StrongholdBrowserEntryPoint, self).__init__(FUNCTIONAL_FLAG.FORT2, PREBATTLE_TYPE.EXTERNAL)


class StrongholdEntryPoint(UnitEntryPoint):
    """
    Strongholds entry point
    """

    def __init__(self, accountsToInvite=None):
        self.__timeout = None
        self.__currentCtx = None
        self.__isLegionary = False
        super(StrongholdEntryPoint, self).__init__(FUNCTIONAL_FLAG.FORT2, accountsToInvite)
        return

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

        processor = StrongholdUnitRequestProcessor()
        processor.doRequest(contexts.StrongholdJoinBattleCtx(ctx.getID()), 'join', callback=onResponse)

    def onUnitJoined(self, unitMgrID, unitIdx, prbType):
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


class StrongholdBrowserEntity(UnitBrowserEntity):
    """
    Strongholds browser entity
    """

    def __init__(self):
        super(StrongholdBrowserEntity, self).__init__(FUNCTIONAL_FLAG.FORT2, PREBATTLE_TYPE.EXTERNAL)

    def canKeepMode(self):
        return False

    def _loadUnit(self):
        g_eventDispatcher.loadStrongholds(self._prbType)

    def _unloadUnit(self):
        g_eventDispatcher.removeUnitFromCarousel(self._prbType)

    def _showWindow(self):
        g_eventDispatcher.showStrongholdsWindow()


class StrongholdEntity(UnitEntity):
    """
    StrongholdEntity entity
    """

    def __init__(self):
        super(StrongholdEntity, self).__init__(FUNCTIONAL_FLAG.FORT2, PREBATTLE_TYPE.EXTERNAL)
        self.__g_clanCache = _ClanCache()
        self.__revisionId = 0
        self.__strongholdData = None
        self.__strongholdDataDiffer = StrongholdDataDiffer()
        self.__waitingManager = WaitingManager()
        self.__errorCount = 0
        self.__timerID = None
        self.__preventInfinityLoopInMatchmakingTimer = False
        self.__isInactiveMatchingButton = True
        self.__showedBattleIdx = 0
        self.__listenersMapping = {'available_reserves': self.__onAvailableReservesChanged,
         'battle_series_status': self.__onBattleSeriesStatusChanged,
         'matchmaker_next_tick': self._updateMatchmakingTimer,
         'battles_end_time': self._updateMatchmakingTimer,
         'battles_start_time': self._updateMatchmakingTimer,
         'fort_battles_before_start_lag': self._updateMatchmakingTimer,
         'sorties_before_start_lag': self._updateMatchmakingTimer,
         'sorties_before_end_lag': self._updateMatchmakingTimer,
         'direction': self.__onDirectionChanged,
         'selected_reserves': self.__onSelectedReservesChanged,
         'requisition_bonus_percent': self.__onRequisitionBonusPercentChanged,
         'industrial_resource_multiplier': self.__onIndustrialResourceMultiplierChanged,
         'battle_duration': self.__onBattleDurationChanged,
         'time_to_ready': self.__onTimeToReadyChanged,
         'clan': self.__onClanChanged,
         'enemy_clan': self.__onEnemyClanChanged,
         'min_level': self.__onLevelChanged,
         'max_level': self.__onLevelChanged,
         'min_players_count': self.__onPlayersCountChanged,
         'max_players_count': self.__onPlayersCountChanged,
         'max_legionaries_count': self.__onMaxLegionariesCountChanged,
         'permissions': self.__onPermissionsChanged,
         'public': self.__onPublicStateChanged,
         'type': self.__onTypeChanged,
         'ready_button_enabled': self.__onReadyButtonEnabled,
         'update_all': self.__onUpdateAll}
        return

    def init(self, ctx=None):
        ret = super(StrongholdEntity, self).init(ctx)
        _, unit = self.getUnit()
        if unit._extras.get('rev', 0) > 1:
            self.requestUpdateStronghold()
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived += self.onUnitResponseReceived
        g_eventDispatcher.loadHangar()
        return ret

    def fini(self, ctx=None, woEvents=False):
        self.__cancelMatchmakingTimer()
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived -= self.onUnitResponseReceived
        super(StrongholdEntity, self).fini(ctx, woEvents)

    def initEvents(self, listener):
        super(StrongholdEntity, self).initEvents(listener)
        if self.canShowMaintenance():
            self._invokeListeners('onStrongholdMaintenance')

    def onUnitResponseReceived(self, requestID):
        LOG_DEBUG('Unit response requestID = ' + str(requestID))
        self.__waitingManager.onResponseWebReqID(requestID)

    def canShowMaintenance(self):
        return self.__errorCount >= ERROR_MAX_RETRY_COUNT

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.FORT2:
            g_eventDispatcher.showStrongholdsWindow()
            SelectResult(True)
        return super(StrongholdEntity, self).doSelectAction(action)

    def getConfirmDialogMeta(self, ctx):
        if self.__errorCount == 0 and self.hasLockedState():
            meta = super(StrongholdEntity, self).getConfirmDialogMeta(ctx)
        else:
            pDbID = account_helpers.getAccountDatabaseID()
            members, clanMembers = self._getClanMembers()
            if ctx.hasFlags(FUNCTIONAL_FLAG.EXIT) or pDbID in members:
                isFirstBattle = self.__strongholdData.isFirstBattle() if self.__strongholdData else True
                isLastClanMember = len(clanMembers) == 1 and clanMembers[0] == pDbID
                subKey = 'Defeat' if isLastClanMember and not isFirstBattle else ''
                meta = StrongholdConfirmDialogMeta(key='leave', subKey=subKey)
            else:
                meta = None
        return meta

    def getQueueType(self):
        return QUEUE_TYPE.EXTERNAL_UNITS

    def getStrongholdData(self):
        return self.__strongholdData

    def unit_onUnitFlagsChanged(self, prevFlags, nextFlags):
        super(StrongholdEntity, self).unit_onUnitFlagsChanged(prevFlags, nextFlags)
        isInQueue = self.getFlags().isInQueue()
        if isInQueue:
            self._invokeListeners('onCommanderIsReady', True)
        elif prevFlags != nextFlags and nextFlags == 0:
            self._invokeListeners('onCommanderIsReady', False)

    def unit_onUnitExtraChanged(self, extras):
        super(StrongholdEntity, self).unit_onUnitExtraChanged(extras)
        revisionId = extras['rev']
        if revisionId == self.__revisionId:
            return
        self.requestUpdateStronghold()
        self.__revisionId = revisionId

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

        super(StrongholdEntity, self).request(ctx, wrapper)

    def leave(self, ctx, callback=None):

        def callbackWrapper(response):
            if self.__processResponseMessage(response):
                callback(response)
            else:
                super(StrongholdEntity, self).leave(ctx, callback)

        isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
        if self.__errorCount > 0 or isSwitch:
            super(StrongholdEntity, self).leave(ctx, callback)
        else:
            self._requestsProcessor.doRequest(ctx, 'leave', callback=callbackWrapper)

    def doBattleQueue(self, ctx, callback=None):
        if ctx.isRequestToStart():
            self._cooldown.process(settings.REQUEST_TYPE.SET_PLAYER_STATE, ctx.getCooldown())
        super(StrongholdEntity, self).doBattleQueue(ctx, callback)

    def setReserve(self, ctx, callback=None):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeConsumables():
            LOG_ERROR('Player can not change consumables', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'activateReserve', callback=callback)
        self._cooldown.process(settings.REQUEST_TYPE.SET_RESERVE, coolDown=ctx.getCooldown())

    def unsetReserve(self, ctx, callback=None):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeConsumables():
            LOG_ERROR('Player can not change consumables', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'deactivateReserve', callback=callback)
        self._cooldown.process(settings.REQUEST_TYPE.UNSET_RESERVE, coolDown=ctx.getCooldown())

    def canKeepMode(self):
        return False if not isStrongholdsEnabled() else super(StrongholdEntity, self).canKeepMode()

    def changeOpened(self, ctx, callback=None):
        self._requestsProcessor.doRequest(ctx, 'openUnit', isOpen=ctx.isOpened(), callback=callback)
        self._cooldown.process(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown())

    def _createActionsValidator(self):
        return StrongholdActionsValidator(self)

    def canPlayerDoAction(self):
        """
        Can current player set ready state or go into battle.
        Validates it with actions validators.
        Returns:
            validation result object
        """
        if self.__errorCount > 0:
            return ValidationResult(False, UNIT_RESTRICTION.UNIT_MAINTENANCE)
        else:
            if self.__isInactiveMatchingButton and self.isCommander() and not self.getFlags().isInArena():
                resultId = UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_UNDEF
                if self.getStrongholdData() is not None:
                    if self.getStrongholdData().isSortie():
                        resultId = UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_SORTIE
                    else:
                        resultId = UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_BATTLE
                matchingCommanderRestriction = ValidationResult(False, resultId)
            else:
                matchingCommanderRestriction = None
            if not self.getStrongholdUnitIsFreezed():
                readyButtonEnableRestriction = None
            else:
                readyButtonEnableRestriction = ValidationResult(False, UNIT_RESTRICTION.UNIT_MAINTENANCE)
            return self._actionsValidator.canPlayerDoAction() or readyButtonEnableRestriction or matchingCommanderRestriction or ValidationResult(True, UNIT_RESTRICTION.UNDEFINED)
            return

    def isPlayerJoined(self, ctx):
        return ctx.getCtrlType() is settings.CTRL_ENTITY_TYPE.UNIT and ctx.getEntityType() == self._prbType and ctx.getID() == self.getID()

    def requestUpdateStronghold(self):
        if self._requestsProcessor:
            unitMgrId = prb_getters.getUnitMgrID()
            ctx = contexts.StrongholdUpdateCtx(unitMgrId=unitMgrId, waitingID='')
            self._requestsProcessor.doRequest(ctx, 'updateStronghold', callback=self.__onStrongholdUpdate)

    def strongholdDataChanged(self):
        if self.__strongholdData is not None:
            self._updateMatchmakingTimer()
            self._invokeListeners('onStrongholdDataChanged')
        return

    def getCandidates(self, unitIdx=None):
        unitIdx, unit = self.getUnit(unitIdx=unitIdx)
        players = unit.getPlayers()
        memberIDs = set((value['accountDBID'] for value in unit.getMembers().itervalues()))
        dbIDs = set(players.keys()).difference(memberIDs)
        result = {}
        for dbID, data in players.iteritems():
            if dbID not in dbIDs:
                continue
            result[dbID] = unit_items.PlayerUnitInfo(dbID, unitIdx, unit, **data)
            result[dbID] = self._buildPlayerInfo(unitIdx, unit, dbID, -1, data)

        return result

    def getStrongholdUnitIsFreezed(self):
        if self.__strongholdData:
            return not self.__strongholdData.getReadyButtonEnabled()
        else:
            return True

    def getRosterSettings(self):
        if self.__strongholdData is not None:
            return self.__updateRosterSettings()
        else:
            return self._rosterSettings
            return

    def animationNotAvailable(self):
        if self.__showedBattleIdx != self.__strongholdData.getBattleIdx():
            self.__showedBattleIdx = self.__strongholdData.getBattleIdx()
            return False
        else:
            return True

    def _updateMatchmakingTimer(self):
        self.__preventInfinityLoopInMatchmakingTimer = False
        self.__cancelMatchmakingTimer()
        self.__updateMatchmakingData()

    def _createActionsHandler(self):
        return StrongholdActionsHandler(self)

    def _getClanMembers(self):
        """
            Method returns lists of members and clan members in the unit
            [<accountDBID>, <accountDBID>, ...], [<accountDBID>, <accountDBID>, ...]
        """
        _, unit = self.getUnit()
        members = [ member['accountDBID'] for member in unit.getMembers().itervalues() ]
        clanMembers = []
        for memberDBID in members:
            pInfo = self.getPlayerInfo(dbID=memberDBID)
            if not pInfo.isLegionary():
                clanMembers.append(memberDBID)

        return (members, clanMembers)

    def _buildPermissions(self, roles, flags, isCurrentPlayer=False, isPlayerReady=False, hasLockedState=False):
        _, unit = self.getUnit(unitIdx=None)
        playerInfo = self.getPlayerInfo()
        myClanRole = self.__g_clanCache.clanRole
        canStealLeadership = not self.getFlags().isInIdle()
        commanderDBID = unit.getCreatorDBID()
        if playerInfo.dbID != commanderDBID:
            clanMembers = self.__g_clanCache.clanMembers
            commanderClanRole = CLAN_MEMBER_FLAGS.RESERVIST
            for member in clanMembers:
                if member.getID() == commanderDBID:
                    commanderClanRole = member.getClanRole()
                    break

            if myClanRole >= commanderClanRole:
                canStealLeadership = False
        strongholdRoles = None
        if self.__strongholdData is not None:
            strongholdRoles = self.__strongholdData.getPermissions().get('manage_reserves')
        return StrongholdPermissions(roles, flags, isCurrentPlayer, isPlayerReady, clanRoles=myClanRole, strongholdRoles=strongholdRoles, isLegionary=playerInfo.isLegionary(), isInSlot=playerInfo.isInSlot, canStealLeadership=canStealLeadership, isFreezed=self.getStrongholdUnitIsFreezed())

    def _getRequestHandlers(self):
        RQ_TYPE = settings.REQUEST_TYPE
        handlers = super(StrongholdEntity, self)._getRequestHandlers()
        handlers.update({RQ_TYPE.SET_RESERVE: self.setReserve,
         RQ_TYPE.UNSET_RESERVE: self.unsetReserve})
        return handlers

    def _buildPlayerInfo(self, unitIdx, unit, dbID, slotIdx=-1, data=None):
        cmderDBID = unit.getCommanderDBID()
        commander = unit.getPlayer(cmderDBID)
        player = unit.getPlayer(dbID)
        if player and commander and data:
            if commander['clanDBID'] != player['clanDBID']:
                data['role'] |= UNIT_ROLE.LEGIONARY
            else:
                data['role'] &= ~UNIT_ROLE.LEGIONARY
        return super(StrongholdEntity, self)._buildPlayerInfo(unitIdx, unit, dbID, slotIdx=slotIdx, data=data)

    def _getRequestProcessor(self):
        return StrongholdUnitRequestProcessor()

    def _getCurrentUTCTime(self):
        return datetime.datetime.utcnow()

    def _convertUTCStructToLocalTimestamp(self, val):
        val = time_utils.utcToLocalDatetime(val).timetuple()
        return time_utils.getTimestampFromLocal(val)

    def __updateRosterSettings(self):
        _, unit = self.getUnit()
        return StrongholdDynamicRosterSettings(unit, self.__strongholdData)

    def __onStrongholdUpdate(self, response):
        if not self.__processResponseMessage(response):
            BigWorld.callback(0.0, self.requestUpdateStronghold)
            return
        else:
            strongholdData = response.getData()
            if response.getCode() != ResponseCodes.NO_ERRORS and not strongholdData:
                return
            self.__waitingManager.onResponseWebReqID(0)
            _, unit = self.getUnit(unitIdx=None, safe=True)
            if unit is None:
                return
            diffToUpdate = self.__strongholdDataDiffer.makeDiff(strongholdData)
            self.__strongholdData = makeTupleByDict(StrongholdSettings, strongholdData)
            if diffToUpdate is None or self.__strongholdData is None:
                return
            self._updateMatchmakingTimer()
            self._invokeListeners('onStrongholdDataChanged')
            for toUpdate in diffToUpdate:
                listener = self.__listenersMapping.get(toUpdate)
                if listener is not None:
                    listener()

            if len(diffToUpdate) == 0:
                self.__onSelectedReservesChanged()
            return

    def __onAvailableReservesChanged(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onAvailableReservesChanged', self.__strongholdData.getSelectedReservesIdx(), self.__strongholdData.getReserveOrder())

    def __onBattleSeriesStatusChanged(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onBattleSeriesStatusChanged', self.__strongholdData.getCurrentBattle(), self.__strongholdData.getEnemyClan(), self.__strongholdData.getBattleIdx(), self.__strongholdData.getClan())

    def __onDirectionChanged(self):
        self._invokeListeners('onDirectionChanged', self.__strongholdData.isSortie(), self.__strongholdData.getDirection(), self.__strongholdData.getResourceMultiplier())

    def __onSelectedReservesChanged(self):
        self._invokeListeners('onSelectedReservesChanged', self.__strongholdData.getSelectedReservesIdx(), self.__strongholdData.getReserveOrder())

    def __onRequisitionBonusPercentChanged(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onRequisitionBonusPercentChanged')

    def __onIndustrialResourceMultiplierChanged(self):
        self._invokeListeners('onIndustrialResourceMultiplierChanged', self.__strongholdData.isSortie(), self.__strongholdData.getDirection(), self.__strongholdData.getResourceMultiplier())

    def __onBattleDurationChanged(self):
        self._invokeListeners('onBattleDurationChanged', self.__strongholdData.getCurrentBattle(), self.__strongholdData.getEnemyClan(), self.__strongholdData.getBattleIdx(), self.__strongholdData.getClan())

    def __onTimeToReadyChanged(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onTimeToReadyChanged')

    def __onClanChanged(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onClanChanged')

    def __onEnemyClanChanged(self):
        self._invokeListeners('onEnemyClanChanged', self.__strongholdData.getCurrentBattle(), self.__strongholdData.getEnemyClan(), self.__strongholdData.getBattleIdx(), self.__strongholdData.getClan())

    def __onLevelChanged(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onLevelChanged')

    def __onPlayersCountChanged(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onPlayersCountChanged', self.__strongholdData.getMaxPlayerCount(), self.__strongholdData.getMaxLegCount())

    def __onMaxLegionariesCountChanged(self):
        self._invokeListeners('onMaxLegionariesCountChanged', self.__strongholdData.getMaxPlayerCount(), self.__strongholdData.getMaxLegCount())

    def __onPermissionsChanged(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onPermissionsChanged', self.__strongholdData.getSelectedReservesIdx(), self.__strongholdData.getReserveOrder())

    def __onPublicStateChanged(self):
        self._invokeListeners('onPublicStateChanged', self.__strongholdData.getPublic())

    def __onTypeChanged(self):
        self._invokeListeners('onTypeChanged', self.__strongholdData.isSortie(), self.__strongholdData.getDirection(), self.__strongholdData.getResourceMultiplier())

    def __onUpdateAll(self):
        self._updateMatchmakingTimer()
        self._invokeListeners('onUpdateAll')
        self.__onReadyButtonEnabled()

    def __processResponseMessage(self, response):
        if isinstance(response, Response):
            txtMsg = ''
            notificationType = None
            data = response.getData()
            hasErrors = response.getCode() != ResponseCodes.NO_ERRORS
            if hasErrors and response.extraCode not in SUCCESS_STATUSES:
                self.__errorCount += 1
                if self.canShowMaintenance():
                    self._invokeListeners('onStrongholdMaintenance')
                else:
                    return False
            else:
                self.__errorCount = 0
            if isinstance(data, dict):
                webReqID = data.pop('web_request_id', None)
                if 'extra_data' in data:
                    extra_data = data['extra_data']
                    if isinstance(extra_data, dict):
                        data = extra_data
                    else:
                        data = {'description': extra_data}
                txtMsg = data.pop('description', '') or data.pop('title', '')
                notificationType = SM_TYPE.lookup(data.pop('notification_type', ''))
                if webReqID is not None:
                    LOG_DEBUG('Web response requestID = ' + str(webReqID))
                    self.__waitingManager.onResponseWebReqID(webReqID)
            if txtMsg:
                if not notificationType or notificationType not in [SM_TYPE.Error, SM_TYPE.Warning, SM_TYPE.Information]:
                    notificationType = SM_TYPE.Error
                self._invokeListeners('onStrongholdRequestTextMessage', notificationType, txtMsg)
            if response.getCode() != ResponseCodes.NO_ERRORS:
                self.__waitingManager.onResponseError()
        return True

    def __onReadyButtonEnabled(self):
        self._invokeListeners('onStrongholdOnReadyStateChanged')

    def __cancelMatchmakingTimer(self):
        if self.__timerID is not None:
            BigWorld.cancelCallback(self.__timerID)
            self.__timerID = None
        return

    def __updateMatchmakingData(self):
        self.__cancelMatchmakingTimer()
        data = self.getStrongholdData()
        isInSlot = False
        playerInfo = self.getPlayerInfo()
        if playerInfo is not None:
            isInSlot = playerInfo.isInSlot
        vInfos = self.getVehiclesInfo()
        isVehicleInBattle = False
        if vInfos is not None:
            for vInfo in vInfos:
                vehicle = vInfo.getVehicle()
                if vehicle is not None:
                    if vehicle.isInBattle:
                        isVehicleInBattle = True

        isInBattle = isVehicleInBattle or not isInSlot and self.getFlags().isInIdle() or isInSlot and self.getFlags().isInArena() and playerInfo.isInArena()
        dtime = None
        textid = None
        peripheryStartTimestampUTC = 0
        currentTimestampUTC = 0
        matchmakerNextTick = None
        tempIsInactiveMatchingButton = self.__isInactiveMatchingButton
        self.__isInactiveMatchingButton = True
        currentTimeUTC = self._getCurrentUTCTime()
        peripheryStartTimeUTC = currentTimeUTC.replace(hour=0, minute=0, second=0, microsecond=0)
        peripheryEndTimeUTC = currentTimeUTC.replace(hour=0, minute=0, second=0, microsecond=0)
        if data.getBattlesStartTime() and data.getBattlesEndTime():
            isInactivePeriphery = False
            peripheryStartTimeUTC = time.strptime(data.getBattlesStartTime(), '%H:%M')
            peripheryEndTimeUTC = time.strptime(data.getBattlesEndTime(), '%H:%M')
            peripheryStartTimeUTC = currentTimeUTC.replace(hour=peripheryStartTimeUTC.tm_hour, minute=peripheryStartTimeUTC.tm_min, second=0, microsecond=0)
            peripheryEndTimeUTC = currentTimeUTC.replace(hour=peripheryEndTimeUTC.tm_hour, minute=peripheryEndTimeUTC.tm_min, second=0, microsecond=0)
            if peripheryStartTimeUTC > peripheryEndTimeUTC:
                peripheryEndTimeUTC += datetime.timedelta(days=1)
            if not self.__preventInfinityLoopInMatchmakingTimer and currentTimeUTC > peripheryEndTimeUTC and currentTimeUTC > peripheryStartTimeUTC:
                peripheryEndTimeUTC += datetime.timedelta(days=1)
                peripheryStartTimeUTC += datetime.timedelta(days=1)
            peripheryStartTimestampUTC = int(time_utils.getTimestampFromUTC(peripheryStartTimeUTC.timetuple()))
            currentTimestampUTC = int(time_utils.getTimestampFromUTC(currentTimeUTC.timetuple()))
        else:
            peripheryEndTimeUTC -= datetime.timedelta(days=1)
            peripheryStartTimeUTC -= datetime.timedelta(days=1)
            isInactivePeriphery = True
            dtime = 0
        if data.isSortie():
            textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_UNAVAILABLE
            if isInBattle:
                textid = TOOLTIPS.STRONGHOLDS_TIMER_SQUADINBATTLE
            elif peripheryStartTimeUTC <= currentTimeUTC <= peripheryEndTimeUTC:
                self.__preventInfinityLoopInMatchmakingTimer = True
                dtime = int((peripheryEndTimeUTC - currentTimeUTC).total_seconds())
                self.__isInactiveMatchingButton = False
                if dtime <= data.getSortiesBeforeEndLag():
                    textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_ENDOFBATTLESOON
                else:
                    textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_AVAILABLE
            elif isInactivePeriphery or currentTimeUTC > peripheryEndTimeUTC:
                dtime = 0
            else:
                currentTimestamp = self._convertUTCStructToLocalTimestamp(currentTimeUTC)
                peripheryStartTimestamp = self._convertUTCStructToLocalTimestamp(peripheryStartTimeUTC)
                currDayStart, currDayEnd = time_utils.getDayTimeBoundsForLocal(currentTimestamp)
                dtime = peripheryStartTimestampUTC - currentTimestampUTC
                if dtime <= data.getSortiesBeforeStartLag():
                    if dtime < 0:
                        dtime = 0
                    textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON
                    if dtime <= MATCHMAKING_BATTLE_BUTTON_SORTIE:
                        self.__isInactiveMatchingButton = False
                elif currDayStart <= peripheryStartTimestamp - time_utils.ONE_DAY <= currDayEnd:
                    textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETOMORROW
                elif currDayStart <= peripheryStartTimestamp <= currDayEnd:
                    textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETODAY
        else:
            textid = FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_UNAVAILABLE
            if not isInactivePeriphery:
                dtime = time_utils.ONE_YEAR
                matchmakerNextTick = data.getChainMatchmakerNextTick()
                if matchmakerNextTick is not None:
                    dtime = matchmakerNextTick - currentTimestampUTC
                else:
                    matchmakerNextTick = data.getMatchmakerNextTick()
                    if matchmakerNextTick is not None:
                        dtime = matchmakerNextTick - currentTimestampUTC
                if isInBattle:
                    textid = TOOLTIPS.STRONGHOLDS_TIMER_SQUADINBATTLE
                elif dtime >= data.getFortBattlesBeforeStartLag():
                    textid = FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_UNAVAILABLE
                    if matchmakerNextTick is not None:
                        currentTimestamp = self._convertUTCStructToLocalTimestamp(currentTimeUTC)
                        matchmakerNextTickLocal = time_utils.getDateTimeInUTC(matchmakerNextTick)
                        matchmakerNextTickLocal = self._convertUTCStructToLocalTimestamp(matchmakerNextTickLocal)
                        currDayStart, currDayEnd = time_utils.getDayTimeBoundsForLocal(matchmakerNextTickLocal)
                        if currDayStart - time_utils.ONE_DAY <= currentTimestamp <= currDayEnd - time_utils.ONE_DAY:
                            textid = FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETOMORROW
                        elif currDayStart <= currentTimestamp <= currDayEnd:
                            textid = FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETODAY
                elif dtime >= 0:
                    textid = FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON
                    if dtime <= MATCHMAKING_BATTLE_BUTTON_BATTLE:
                        self.__isInactiveMatchingButton = False
                else:
                    dtime = 0
        g_eventDispatcher.strongholdsOnTimer({'peripheryStartTimestamp': peripheryStartTimestampUTC,
         'matchmakerNextTick': matchmakerNextTick,
         'clan': data.getClan(),
         'enemyClan': data.getEnemyClan(),
         'textid': textid,
         'dtime': dtime,
         'isSortie': data.isSortie(),
         'isFirstBattle': data.isFirstBattle(),
         'currentBattle': data.getCurrentBattle(),
         'maxLevel': data.getMaxLevel(),
         'direction': data.getDirection()})
        if tempIsInactiveMatchingButton != self.__isInactiveMatchingButton:
            self._invokeListeners('onStrongholdOnReadyStateChanged')
        self.__timerID = BigWorld.callback(1.0, self.__updateMatchmakingData)
        return
