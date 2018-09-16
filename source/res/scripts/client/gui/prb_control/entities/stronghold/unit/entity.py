# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/entity.py
import datetime
import time
from functools import partial
import BigWorld
import account_helpers
from client_request_lib.exceptions import ResponseCodes
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui import SystemMessages
from gui.clans.clan_helpers import isStrongholdsEnabled
from gui.prb_control import prb_getters
from gui.prb_control import settings
from gui.prb_control.entities.base.unit.entity import UnitEntity, UnitEntryPoint, UnitBrowserEntryPoint, UnitBrowserEntity
from gui.prb_control.entities.stronghold.unit.actions_handler import StrongholdActionsHandler
from gui.prb_control.entities.stronghold.unit.actions_validator import StrongholdActionsValidator
from gui.prb_control.entities.stronghold.unit.permissions import StrongholdPermissions
from gui.prb_control.entities.stronghold.unit.requester import StrongholdUnitRequestProcessor
from gui.prb_control.entities.stronghold.unit.waiting import WaitingManager
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters import messages
from gui.prb_control.items import SelectResult
from gui.prb_control.items import ValidationResult, unit_items
from gui.prb_control.items.stronghold_items import StrongholdSettings
from gui.prb_control.items.unit_items import DynamicRosterSettings
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.ClanCache import _ClanCache
from gui.Scaleform.daapi.view.dialogs.rally_dialog_meta import StrongholdConfirmDialogMeta
from gui.SystemMessages import SM_TYPE
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES as I18N_SYSTEM_MESSAGES
from gui.shared.utils.requesters.abstract import Response
from gui.wgcg.strongholds.contexts import StrongholdJoinBattleCtx, StrongholdUpdateCtx
from helpers import time_utils, i18n
from UnitBase import UNIT_ERROR, UNIT_ROLE
_CREATION_TIMEOUT = 30
ERROR_MAX_RETRY_COUNT = 3
SUCCESS_STATUSES = (200, 201, 403, 409)

class StrongholdDynamicRosterSettings(DynamicRosterSettings):

    def __init__(self, unit, strongholdData):
        kwargs = self._extractSettings(unit, strongholdData)
        super(DynamicRosterSettings, self).__init__(**kwargs)

    def _extractSettings(self, unit, strongholdData):
        kwargs = {}
        roster = None
        if unit is not None:
            roster = unit.getRoster()
        if strongholdData.isValid():
            header = strongholdData.getHeader()
            maxSlots = header.getMaxPlayersCount() - 1
            maxEmptySlots = maxSlots - header.getMinPlayersCount()
            kwargs['minLevel'] = header.getMinLevel()
            kwargs['maxLevel'] = header.getMaxLevel()
            kwargs['maxSlots'] = maxSlots
            kwargs['maxClosedSlots'] = maxEmptySlots
            kwargs['maxEmptySlots'] = maxEmptySlots
            kwargs['minTotalLevel'] = roster.MIN_UNIT_POINTS_SUM
            kwargs['maxTotalLevel'] = roster.MAX_UNIT_POINTS_SUM
            kwargs['maxLegionariesCount'] = header.getMaxLegionariesCount()
        else:
            LOG_ERROR('Unit roster is not defined')
        return kwargs


class StrongholdBrowserEntryPoint(UnitBrowserEntryPoint):

    def __init__(self):
        super(StrongholdBrowserEntryPoint, self).__init__(FUNCTIONAL_FLAG.STRONGHOLD, PREBATTLE_TYPE.EXTERNAL)


class StrongholdEntryPoint(UnitEntryPoint):

    def __init__(self, accountsToInvite=None):
        self.__timeout = None
        self.__currentCtx = None
        self.__isLegionary = False
        super(StrongholdEntryPoint, self).__init__(FUNCTIONAL_FLAG.STRONGHOLD, accountsToInvite)
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
        processor.doRequest(StrongholdJoinBattleCtx(ctx.getID()), 'join', callback=onResponse)

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


class StrongholdBrowserEntity(UnitBrowserEntity):

    def __init__(self):
        super(StrongholdBrowserEntity, self).__init__(FUNCTIONAL_FLAG.STRONGHOLD, PREBATTLE_TYPE.EXTERNAL)

    def canKeepMode(self):
        return False

    def _loadUnit(self):
        g_eventDispatcher.loadStrongholds(self._prbType)

    def _unloadUnit(self):
        g_eventDispatcher.removeUnitFromCarousel(self._prbType)

    def _showWindow(self):
        g_eventDispatcher.showStrongholdsWindow()


class StrongholdEntity(UnitEntity):
    MATCHMAKING_BATTLE_BUTTON_BATTLE = 10 * time_utils.ONE_MINUTE
    MATCHMAKING_BATTLE_BUTTON_SORTIE = 10 * time_utils.ONE_MINUTE
    MATCHMAKING_ZERO_TIME_WAITING_FOR_DATA = 5
    CWL_REGULAR_MODE = 1
    CWL_RETURN_MATCHING_BUTTON_STATUS = 16
    CWL_RETURN_MATCHMAKER_NEXT_TICK = 256
    CWL_INVOKE_LISTENERS = 4096
    CWL_FORCE_UPDATE_BUILDINGS = 65536

    class SH_REQUEST_COOLDOWN(object):
        PREBATTLE_ASSIGN = 0.6

    def __init__(self):
        super(StrongholdEntity, self).__init__(FUNCTIONAL_FLAG.STRONGHOLD, PREBATTLE_TYPE.EXTERNAL)
        self.__g_clanCache = _ClanCache()
        self.__revisionId = 0
        self.__battleModeData = {}
        self.__strongholdSettings = StrongholdSettings()
        self.__waitingManager = WaitingManager()
        self.__errorCount = 0
        self.__timerID = None
        self.__leaveInitiator = False
        self.__isInSlot = False
        self.__isInactiveMatchingButton = True
        self.__prevMatchmakingTimerState = None
        self.__strongholdUpdateEventsMapping = {}
        return

    def init(self, ctx=None):
        self.storage.release()
        ret = super(StrongholdEntity, self).init(ctx)
        _, unit = self.getUnit()
        if unit._extras.get('rev', 0) > 1:
            self.requestUpdateStronghold()
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived += self.onUnitResponseReceived
            unitMgr.onUnitNotifyReceived += self.onUnitNotifyReceived
        g_eventDispatcher.loadHangar()
        self.__strongholdSettings.init()
        self.__strongholdUpdateEventsMapping = {'header': self.__onUpdateHeader,
         'timer': self.__onUpdateTimer,
         'state': self.__onUpdateState,
         'reserve': self.__onUpdateReserve}
        playerInfo = self.getPlayerInfo()
        self.__isInSlot = playerInfo.isInSlot
        return ret

    def fini(self, ctx=None, woEvents=False):
        self.__cancelMatchmakingTimer()
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived -= self.onUnitResponseReceived
            unitMgr.onUnitNotifyReceived -= self.onUnitNotifyReceived
        self.__strongholdSettings.fini()
        self.__strongholdUpdateEventsMapping = {}
        super(StrongholdEntity, self).fini(ctx, woEvents)

    def initEvents(self, listener):
        super(StrongholdEntity, self).initEvents(listener)
        if self.canShowMaintenance():
            self._invokeListeners('onStrongholdMaintenance', True)

    @prequeue_storage_getter(QUEUE_TYPE.EXTERNAL_UNITS)
    def storage(self):
        return None

    def onUnitResponseReceived(self, requestID):
        LOG_DEBUG('Unit response requestID = ' + str(requestID))
        self.__waitingManager.onResponseWebReqID(requestID)

    def onUnitNotifyReceived(self, unitMgrID, notifyCode, notifyString, argsList):
        if notifyCode == UNIT_ERROR.NO_CLAN_MEMBERS and not self.__leaveInitiator:
            SystemMessages.pushMessage(i18n.makeString(TOOLTIPS.STRONGHOLD_PREBATTLE_NOCLANMEMBERS), type=SM_TYPE.Warning)
        elif notifyCode == UNIT_ERROR.FAIL_EXT_UNIT_QUEUE_START and not self.getFlags().isInQueue():
            self.__waitingManager.onResponseError()

    def canShowMaintenance(self):
        return self.__errorCount >= ERROR_MAX_RETRY_COUNT

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.STRONGHOLD:
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
                isFirstBattle = self.__strongholdSettings.isFirstBattle()
                isLastClanMember = len(clanMembers) == 1 and clanMembers[0] == pDbID
                subKey = 'Defeat' if isLastClanMember and not isFirstBattle else ''
                meta = StrongholdConfirmDialogMeta(key='leave', subKey=subKey)
            else:
                meta = None
        return meta

    def getQueueType(self):
        return QUEUE_TYPE.EXTERNAL_UNITS

    def rejoin(self):
        super(StrongholdEntity, self).rejoin()
        if self.isStrongholdUnitWaitingForData():
            LOG_DEBUG('force wgsh request on end of battle')
            self.__strongholdSettings.forceCleanData()
            self.requestUpdateStronghold()

    def unit_onUnitFlagsChanged(self, prevFlags, nextFlags):
        _, unit = self.getUnit()
        isReady = unit.arePlayersReady(ignored=[settings.CREATOR_SLOT_INDEX])
        flags = unit_items.UnitFlags(nextFlags, prevFlags, isReady)
        isInQueue = flags.isInQueue()
        if isInQueue:
            matchmakerNextTick = self.__doClockworkLogic(self.CWL_RETURN_MATCHMAKER_NEXT_TICK)
            if matchmakerNextTick is not None:
                unit.setModalTimestamp(matchmakerNextTick)
        regularBattleEnd = flags.isArenaFinishedChanged() and flags.isArenaFinished() and flags.isExternalLocked()
        wgshBattleEnd = flags.isExternalLockedStateChanged() and not flags.isExternalLocked()
        if regularBattleEnd or wgshBattleEnd:
            LOG_DEBUG('force wgsh request on end of battle (r,x):', regularBattleEnd, wgshBattleEnd)
            self.__strongholdSettings.forceCleanData()
            self.requestUpdateStronghold()
        super(StrongholdEntity, self).unit_onUnitFlagsChanged(prevFlags, nextFlags)
        self.__doClockworkLogic(self.CWL_INVOKE_LISTENERS | self.CWL_FORCE_UPDATE_BUILDINGS)
        if not self.hasLockedState():
            self.resetCoolDown(settings.REQUEST_TYPE.BATTLE_QUEUE)
            self.resetCoolDown(settings.REQUEST_TYPE.DECLINE_SEARCH)
            self.resetCoolDown(settings.REQUEST_TYPE.AUTO_SEARCH)
        if isInQueue:
            self._invokeListeners('onCommanderIsReady', True)
        elif prevFlags != nextFlags and nextFlags == 0:
            self._invokeListeners('onCommanderIsReady', False)
        return

    def unit_onUnitExtraChanged(self, extras):
        super(StrongholdEntity, self).unit_onUnitExtraChanged(extras)
        revisionId = extras['rev']
        if revisionId == self.__revisionId:
            return
        self.requestUpdateStronghold()
        self.__revisionId = revisionId

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(StrongholdEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        diff = prevRoleFlags ^ nextRoleFlags
        if diff & UNIT_ROLE.CREATOR > 0:
            pInfo = self.getPlayerInfo(dbID=playerID)
            if not pInfo.isCommander() and pInfo.isCurrentPlayer():
                SystemMessages.pushMessage(i18n.makeString(I18N_SYSTEM_MESSAGES.UNIT_WARNINGS_ANOTHER_PLAYER_BECOME_COMMANDER), type=SM_TYPE.Warning)
        userNoLongerEquipmentCommander = prevRoleFlags & UNIT_ROLE.CAN_USE_EXTRA_EQUIPMENTS > 0 and not nextRoleFlags & UNIT_ROLE.CAN_USE_EXTRA_EQUIPMENTS > 0
        userBecomesEquipmentCommander = nextRoleFlags & UNIT_ROLE.CAN_USE_EXTRA_EQUIPMENTS > 0 and not prevRoleFlags & UNIT_ROLE.CAN_USE_EXTRA_EQUIPMENTS > 0
        if not userBecomesEquipmentCommander and not userNoLongerEquipmentCommander:
            return
        pInfo = self.getPlayerInfo(dbID=playerID)
        if userNoLongerEquipmentCommander and pInfo.isCurrentPlayer():
            SystemMessages.pushMessage(i18n.makeString(I18N_SYSTEM_MESSAGES.UNIT_WARNINGS_ANOTHER_PLAYER_BECOME_EQUIPMENT_COMMANDER), type=SM_TYPE.Warning)
            return
        if userBecomesEquipmentCommander and pInfo.isCurrentPlayer():
            SystemMessages.pushMessage(i18n.makeString(I18N_SYSTEM_MESSAGES.UNIT_NOTIFICATION_PLAYER_BECOME_EQUIPMENT_COMMANDER), type=SM_TYPE.Information)
            return
        myPInfo = self.getPlayerInfo()
        userEquipmentRoleChanged = userBecomesEquipmentCommander or userNoLongerEquipmentCommander
        if userEquipmentRoleChanged and not pInfo.isCurrentPlayer() and myPInfo.isCommander():
            SystemMessages.pushMessage(i18n.makeString(I18N_SYSTEM_MESSAGES.UNIT_WARNINGS_ANOTHER_PLAYER_BECOME_EQUIPMENT_COMMANDER), type=SM_TYPE.Warning)
            return

    def unit_onUnitMembersListChanged(self):
        playerInfo = self.getPlayerInfo()
        self.__isInSlot = playerInfo.isInSlot
        super(StrongholdEntity, self).unit_onUnitMembersListChanged()

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
        self.storage.suspend()
        self.__leaveInitiator = True

        def callbackWrapper(response):
            if not self.__processResponseMessage(response):
                super(StrongholdEntity, self).leave(ctx, callback)

        if self.__errorCount > 0:
            super(StrongholdEntity, self).leave(ctx, callback)
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
        self._invokeListeners('onStrongholdDoBattleQueue', self.isFirstBattle(), False, self.__strongholdSettings.getReserveOrder())
        super(StrongholdEntity, self).doBattleQueue(ctx, callback)

    def setReserve(self, ctx, callback=None):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeConsumables():
            LOG_ERROR('Player can not change consumables', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'activateReserve', callback=callback)
        self.setCoolDown(settings.REQUEST_TYPE.SET_RESERVE, coolDown=ctx.getCooldown())

    def unsetReserve(self, ctx, callback=None):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeConsumables():
            LOG_ERROR('Player can not change consumables', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'deactivateReserve', callback=callback)
        self.setCoolDown(settings.REQUEST_TYPE.UNSET_RESERVE, coolDown=ctx.getCooldown())

    def setEquipmentCommander(self, ctx, callback=None):
        self._requestsProcessor.doRequest(ctx, 'setEquipmentCommander', callback=callback)
        self.setCoolDown(settings.REQUEST_TYPE.SET_EQUIPMENT_COMMANDER, coolDown=ctx.getCooldown())

    def assign(self, ctx, callback=None):
        if self.isInCoolDown(settings.REQUEST_TYPE.ASSIGN):
            return
        super(StrongholdEntity, self).assign(ctx, callback)
        self.setCoolDown(settings.REQUEST_TYPE.ASSIGN, coolDown=self.SH_REQUEST_COOLDOWN.PREBATTLE_ASSIGN)

    def canKeepMode(self):
        return False if not isStrongholdsEnabled() else super(StrongholdEntity, self).canKeepMode()

    def changeOpened(self, ctx, callback=None):
        self._requestsProcessor.doRequest(ctx, 'openUnit', isOpen=ctx.isOpened(), callback=callback)
        self.setCoolDown(settings.REQUEST_TYPE.CHANGE_UNIT_STATE, coolDown=ctx.getCooldown())

    def canPlayerDoAction(self):
        if self.__errorCount > 0:
            return ValidationResult(False, UNIT_RESTRICTION.UNIT_MAINTENANCE)
        elif self.isStrongholdUnitFreezed() or self.isStrongholdUnitWaitingForData():
            isPlayerInSlot = self._isPlayerInSlot()
            if isPlayerInSlot and self.isStrongholdUnitWaitingForData():
                return ValidationResult(False, UNIT_RESTRICTION.UNIT_WAITINGFORDATA)
            if isPlayerInSlot and self._hasInArenaMembers():
                return ValidationResult(False, UNIT_RESTRICTION.IS_IN_ARENA)
            result = self._actionsValidator.canPlayerDoAction() or ValidationResult(False, UNIT_RESTRICTION.UNDEFINED)
            return ValidationResult(False, result.restriction, result.ctx)
        else:
            isStrongholdSettingsValid = self.isStrongholdSettingsValid()
            self.__isInactiveMatchingButton = self.__doClockworkLogic(self.CWL_RETURN_MATCHING_BUTTON_STATUS)
            if isStrongholdSettingsValid and self.__isInactiveMatchingButton and self.isCommander() and not self.getFlags().isInIdle():
                resultId = UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_UNDEF
                if isStrongholdSettingsValid:
                    if self.isSortie():
                        resultId = UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_SORTIE
                    else:
                        resultId = UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_BATTLE
                matchingCommanderRestriction = ValidationResult(False, resultId)
            else:
                matchingCommanderRestriction = None
            return self._actionsValidator.canPlayerDoAction() or matchingCommanderRestriction or ValidationResult(True, UNIT_RESTRICTION.UNDEFINED)
            return

    def isPlayerJoined(self, ctx):
        return ctx.getCtrlType() is settings.CTRL_ENTITY_TYPE.UNIT and ctx.getEntityType() == self._prbType and ctx.getID() == self.getID()

    def requestMaintenanceUpdate(self):
        self._invokeListeners('onStrongholdMaintenance', False)
        self.requestUpdateStronghold()

    def requestUpdateStronghold(self):
        if self._requestsProcessor:
            unitMgrId = prb_getters.getUnitMgrID()
            ctx = StrongholdUpdateCtx(unitMgrId=unitMgrId, waitingID='')
            self._requestsProcessor.doRequest(ctx, 'updateStronghold', callback=self.__onStrongholdUpdate)

    def strongholdDataChanged(self):
        if self.isStrongholdSettingsValid():
            header = self.__strongholdSettings.getHeader()
            isFirstBattle = self.isFirstBattle()
            self.__checkBattleMode(header, isFirstBattle)
            self._updateMatchmakingTimer()
            self._invokeListeners('onStrongholdDataChanged', header, isFirstBattle, self.__strongholdSettings.getReserve(), self.__strongholdSettings.getReserveOrder())

    def getCandidates(self, unitMgrID=None):
        unitMgrID, unit = self.getUnit(unitMgrID=unitMgrID)
        players = unit.getPlayers()
        memberIDs = set((value['accountDBID'] for value in unit.getMembers().itervalues()))
        dbIDs = set(players.keys()).difference(memberIDs)
        result = {}
        for dbID, data in players.iteritems():
            if dbID not in dbIDs:
                continue
            result[dbID] = self._buildPlayerInfo(unitMgrID, unit, dbID, -1, data)

        return result

    def getStrongholdSettings(self):
        return self.__strongholdSettings

    def isStrongholdSettingsValid(self):
        return self.__strongholdSettings.isValid()

    def isStrongholdUnitFreezed(self):
        return self.getFlags().isExternalLocked()

    def isStrongholdUnitWaitingForData(self):
        if self.isStrongholdSettingsValid():
            readyButtonEnabled = not self.__strongholdSettings.isStrongholdUnitFreezed()
        else:
            readyButtonEnabled = True
        flags = self.getFlags()
        return self.canShowMaintenance() or flags.isArenaFinished() and flags.isExternalLocked() or not flags.isInIdle() and not self.getFlags().isInArena() and not flags.isExternalLocked() and not readyButtonEnabled

    def isFirstBattle(self):
        return self.__strongholdSettings.isFirstBattle()

    def isSortie(self):
        return self.__strongholdSettings.isSortie()

    def getRosterSettings(self):
        return self.__updateRosterSettings() if self.isStrongholdSettingsValid() else self._rosterSettings

    def animationNotAvailable(self):
        battleIdx = self.__strongholdSettings.getHeader().getBattleIdx()
        if self.storage.getActiveAnimationIdx() != battleIdx and battleIdx != 0:
            self.storage.setActiveAnimationIdx(battleIdx)
            return False
        return True

    def updateStrongholdData(self):
        if self.isStrongholdSettingsValid():
            self.__onUpdateHeader()
            self.__onUpdateTimer()
            self.__onUpdateReserve()
            self.__onUpdateState()

    def forceTimerEvent(self):
        return self.__doClockworkLogic(self.CWL_INVOKE_LISTENERS | self.CWL_RETURN_MATCHMAKER_NEXT_TICK)

    def _createActionsValidator(self):
        return StrongholdActionsValidator(self)

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
        mode = self.CWL_REGULAR_MODE | self.CWL_RETURN_MATCHING_BUTTON_STATUS | self.CWL_INVOKE_LISTENERS
        self.__isInactiveMatchingButton = self.__doClockworkLogic(mode)
        if tempInactiveMatchingButton != self.__isInactiveMatchingButton:
            self._invokeListeners('onStrongholdOnReadyStateChanged')
        self.__timerID = BigWorld.callback(1.0, self._updateMatchmakingTimer)

    def _createActionsHandler(self):
        return StrongholdActionsHandler(self)

    def _getClanMembers(self):
        _, unit = self.getUnit()
        members = [ member['accountDBID'] for member in unit.getMembers().itervalues() ]
        clanMembers = []
        for memberDBID in members:
            pInfo = self.getPlayerInfo(dbID=memberDBID)
            if not pInfo.isLegionary():
                clanMembers.append(memberDBID)

        return (members, clanMembers)

    def _buildPermissions(self, roles, flags, isCurrentPlayer=False, isPlayerReady=False, hasLockedState=False):
        playerInfo = self.getPlayerInfo()
        myClanRole = self.__g_clanCache.clanRole
        strongholdManageReservesRoles = None
        strongholdStealLeadershipRoles = None
        if self.isStrongholdSettingsValid():
            strongholdPermissions = self.__strongholdSettings.getReserve().getPermissions()
            strongholdManageReservesRoles = strongholdPermissions.get('manage_reserves')
            strongholdStealLeadershipRoles = strongholdPermissions.get('take_away_leadership')
        return StrongholdPermissions(roles, flags, isCurrentPlayer, isPlayerReady, clanRoles=myClanRole, strongholdManageReservesRoles=strongholdManageReservesRoles, strongholdStealLeadershipRoles=strongholdStealLeadershipRoles, isLegionary=playerInfo.isLegionary(), isInSlot=playerInfo.isInSlot, isFreezed=self.isStrongholdUnitFreezed(), isInIdle=self.getFlags().isInIdle())

    def _getRequestHandlers(self):
        RQ_TYPE = settings.REQUEST_TYPE
        handlers = super(StrongholdEntity, self)._getRequestHandlers()
        handlers.update({RQ_TYPE.SET_RESERVE: self.setReserve,
         RQ_TYPE.UNSET_RESERVE: self.unsetReserve,
         RQ_TYPE.SET_EQUIPMENT_COMMANDER: self.setEquipmentCommander})
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
        return super(StrongholdEntity, self)._buildPlayerInfo(unitMgrID, unit, dbID, slotIdx=slotIdx, data=data)

    def _getRequestProcessor(self):
        return StrongholdUnitRequestProcessor()

    def _getCurrentUTCTime(self):
        return (time_utils.getDateTimeInUTC(time_utils.getServerUTCTime()), datetime.datetime.utcnow())

    def _convertUTCStructToLocalTimestamp(self, val):
        val = time_utils.utcToLocalDatetime(val).timetuple()
        return time_utils.getTimestampFromLocal(val)

    def __updateRosterSettings(self):
        _, unit = self.getUnit()
        return StrongholdDynamicRosterSettings(unit, self.__strongholdSettings)

    def __onStrongholdUpdate(self, response):
        if not self.__processResponseMessage(response):
            BigWorld.callback(0.0, self.requestUpdateStronghold)
            return
        else:
            rawData = response.getData()
            if response.getCode() != ResponseCodes.NO_ERRORS and not rawData:
                return
            self.__waitingManager.onResponseWebReqID(0)
            _, unit = self.getUnit(unitMgrID=None, safe=True)
            if unit is None:
                return
            diffToUpdate = self.__strongholdSettings.updateData(rawData)
            if diffToUpdate is None:
                self._invokeListeners('onStrongholdMaintenance', True)
                return
            LOG_DEBUG('onStrongholdUpdate, timer data (r,m): ', self.__strongholdSettings.getTimer().getTimeToReady(), self.__strongholdSettings.getTimer().getMatchmakerNextTick())
            if not self.__isMatchmakingTimerLoopExist():
                self._updateMatchmakingTimer()
            self.__doClockworkLogic(self.CWL_INVOKE_LISTENERS | self.CWL_FORCE_UPDATE_BUILDINGS)
            if self.isStrongholdSettingsValid():
                header = self.__strongholdSettings.getHeader()
                isFirstBattle = self.isFirstBattle()
                self.__checkBattleMode(header, isFirstBattle)
                self._invokeListeners('onStrongholdDataChanged', header, isFirstBattle, self.__strongholdSettings.getReserve(), self.__strongholdSettings.getReserveOrder())
            if 'all' in diffToUpdate:
                self.updateStrongholdData()
            else:
                for toUpdate in diffToUpdate:
                    listener = self.__strongholdUpdateEventsMapping.get(toUpdate)
                    if listener is not None:
                        listener()

            return

    def __checkBattleMode(self, header, isFirstBattle):
        if isFirstBattle:
            gettersMapping = {'type': header.getType,
             'direction': header.getDirection,
             'max_level': header.getMaxLevel,
             'max_players_count': header.getMaxPlayersCount}
            battleModeFields = (('type', 'STRONGHOLDS_MODE_CHANGED'),
             ('direction', 'STRONGHOLDS_DIRECTION_CHANGED'),
             ('max_level', 'STRONGHOLDS_MODE_CHANGED'),
             ('max_players_count', 'STRONGHOLDS_MODE_CHANGED'))
            if self.__battleModeData:
                for field, key in battleModeFields:
                    if self.__battleModeData.get(field) != gettersMapping[field]():
                        SystemMessages.pushI18nMessage(messages.getUnitWarningMessage(key), type=SystemMessages.SM_TYPE.Warning)
                        break

            for field, _ in battleModeFields:
                self.__battleModeData[field] = gettersMapping[field]()

    def __onUpdateHeader(self):
        header = self.__strongholdSettings.getHeader()
        isFirstBattle = self.isFirstBattle()
        battleIdx = header.getBattleIdx()
        flags = self.getFlags()
        if battleIdx == 0 or flags.isInArena() or flags.isInQueue():
            self.storage.setActiveAnimationIdx(battleIdx)
        self.__checkBattleMode(header, isFirstBattle)
        self._invokeListeners('onUpdateHeader', header, isFirstBattle, self.isStrongholdUnitFreezed())

    def __onUpdateTimer(self):
        self._invokeListeners('onUpdateTimer', self.__strongholdSettings.getTimer())

    def __onUpdateState(self):
        self._invokeListeners('onUpdateState', self.__strongholdSettings.getState())

    def __onUpdateReserve(self):
        self._invokeListeners('onUpdateReserve', self.__strongholdSettings.getReserve(), self.__strongholdSettings.getReserveOrder())

    def __processResponseMessage(self, response):
        if isinstance(response, Response):
            txtMsg = ''
            notificationType = None
            data = response.getData()
            hasErrors = response.getCode() != ResponseCodes.NO_ERRORS
            if hasErrors and response.extraCode not in SUCCESS_STATUSES:
                self.__errorCount += 1
                if self.canShowMaintenance():
                    self._invokeListeners('onStrongholdMaintenance', True)
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
                SystemMessages.pushMessage(txtMsg, type=notificationType)
            if response.getCode() != ResponseCodes.NO_ERRORS:
                self.__waitingManager.onResponseError()
        return True

    def __onReadyButtonEnabled(self):
        self._invokeListeners('onStrongholdOnReadyStateChanged')

    def __isMatchmakingTimerLoopExist(self):
        return self.__timerID is not None

    def __cancelMatchmakingTimer(self):
        if self.__timerID is not None:
            BigWorld.cancelCallback(self.__timerID)
            self.__timerID = None
        return

    def __calculatePeripheryTimeHelper(self, baseTimeUTC):
        timer = self.__strongholdSettings.getTimer()
        peripheryStartTimeUTC = time.strptime(timer.getBattlesStartTime(), '%H:%M')
        peripheryEndTimeUTC = time.strptime(timer.getBattlesEndTime(), '%H:%M')
        peripheryStartTimeUTC = baseTimeUTC.replace(hour=peripheryStartTimeUTC.tm_hour, minute=peripheryStartTimeUTC.tm_min, second=0, microsecond=0)
        peripheryEndTimeUTC = baseTimeUTC.replace(hour=peripheryEndTimeUTC.tm_hour, minute=peripheryEndTimeUTC.tm_min, second=0, microsecond=0)
        if peripheryStartTimeUTC > peripheryEndTimeUTC:
            shiftedStartTimeUTC = peripheryStartTimeUTC - datetime.timedelta(days=1)
            if shiftedStartTimeUTC <= baseTimeUTC <= peripheryEndTimeUTC:
                peripheryStartTimeUTC = shiftedStartTimeUTC
            else:
                peripheryEndTimeUTC += datetime.timedelta(days=1)
        if baseTimeUTC > peripheryEndTimeUTC and baseTimeUTC > peripheryStartTimeUTC:
            peripheryEndTimeUTC += datetime.timedelta(days=1)
            peripheryStartTimeUTC += datetime.timedelta(days=1)
        return (peripheryStartTimeUTC, peripheryEndTimeUTC)

    def __doClockworkLogic(self, mode):
        if not self.isStrongholdSettingsValid():
            if mode & self.CWL_RETURN_MATCHING_BUTTON_STATUS == self.CWL_RETURN_MATCHING_BUTTON_STATUS:
                return True
            return
        isInBattle = self._hasInArenaMembers()
        isInQueue = self._isInQueue()
        dtime = None
        peripheryStartTimestampUTC = 0
        currentTimestampUTC = 0
        matchmakerNextTick = None
        inactiveMatchingButton = True
        forceUpdateBuildings = mode & self.CWL_FORCE_UPDATE_BUILDINGS == self.CWL_FORCE_UPDATE_BUILDINGS
        currentTimeUTC, clientTimeUTC = self._getCurrentUTCTime()
        timer = self.__strongholdSettings.getTimer()
        peripheryStartTimeUTC = currentTimeUTC.replace(hour=0, minute=0, second=0, microsecond=0)
        peripheryEndTimeUTC = currentTimeUTC.replace(hour=0, minute=0, second=0, microsecond=0)
        if timer.getBattlesStartTime() and timer.getBattlesEndTime():
            isInactivePeriphery = False
            peripheryStartTimeUTC, peripheryEndTimeUTC = self.__calculatePeripheryTimeHelper(currentTimeUTC)
            peripheryStartTimestampUTC = int(time_utils.getTimestampFromUTC(peripheryStartTimeUTC.timetuple()))
            currentTimestampUTC = int(time_utils.getTimestampFromUTC(currentTimeUTC.timetuple()))
        else:
            peripheryEndTimeUTC -= datetime.timedelta(days=1)
            peripheryStartTimeUTC -= datetime.timedelta(days=1)
            isInactivePeriphery = True
            dtime = 0
        if self.__strongholdSettings.isSortie():
            textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_UNAVAILABLE
            if isInQueue:
                textid = TOOLTIPS.STRONGHOLDS_TIMER_SQUADINQUEUE
                dtime = peripheryStartTimestampUTC - currentTimestampUTC
                if dtime < 0 or dtime > timer.getSortiesBeforeStartLag():
                    dtime = 0
            elif isInBattle:
                textid = TOOLTIPS.STRONGHOLDS_TIMER_SQUADINBATTLE
            elif self.isStrongholdUnitWaitingForData():
                textid = TOOLTIPS.STRONGHOLDS_TIMER_WAITINGFORDATA
            elif peripheryStartTimeUTC <= currentTimeUTC <= peripheryEndTimeUTC:
                dtime = int((peripheryEndTimeUTC - currentTimeUTC).total_seconds())
                inactiveMatchingButton = False
                if dtime <= timer.getSortiesBeforeEndLag():
                    textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_ENDOFBATTLESOON
                else:
                    textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_AVAILABLE
            elif isInactivePeriphery:
                dtime = 0
            else:
                dtime = peripheryStartTimestampUTC - currentTimestampUTC
                if dtime <= timer.getSortiesBeforeStartLag():
                    if dtime < 0:
                        dtime = 0
                    textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON
                    if dtime <= self.MATCHMAKING_BATTLE_BUTTON_SORTIE:
                        inactiveMatchingButton = False
                else:
                    peripheryStartTimeUTC, _ = self.__calculatePeripheryTimeHelper(clientTimeUTC)
                    peripheryStartTimestampUTC = int(time_utils.getTimestampFromUTC(peripheryStartTimeUTC.timetuple()))
                    currentTimestampUTC = int(time_utils.getTimestampFromUTC(clientTimeUTC.timetuple()))
                    peripheryStartTimestamp = self._convertUTCStructToLocalTimestamp(peripheryStartTimeUTC)
                    currentTimestamp = self._convertUTCStructToLocalTimestamp(clientTimeUTC)
                    dtime = peripheryStartTimestampUTC - currentTimestampUTC
                    currDayStart, currDayEnd = time_utils.getDayTimeBoundsForLocal(peripheryStartTimestamp)
                    if currDayStart - time_utils.ONE_DAY <= currentTimestamp <= currDayEnd - time_utils.ONE_DAY:
                        textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETOMORROW
                    elif currDayStart <= currentTimestamp <= currDayEnd:
                        textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETODAY
        else:
            textid = FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_UNAVAILABLE
            if not isInactivePeriphery:
                dtime = time_utils.ONE_YEAR
                matchmakerNextTick = timer.getTimeToReady()
                dtime = matchmakerNextTick is not None and int(matchmakerNextTick - currentTimestampUTC)
            else:
                matchmakerNextTick = timer.getMatchmakerNextTick()
                if matchmakerNextTick is not None:
                    dtime = int(matchmakerNextTick - currentTimestampUTC)
            battlesBeforeStartLag = timer.getFortBattlesBeforeStartLag()
            if self.__prevMatchmakingTimerState == FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON:
                if 0 <= int(dtime - battlesBeforeStartLag) < self.MATCHMAKING_ZERO_TIME_WAITING_FOR_DATA and mode & self.CWL_REGULAR_MODE == self.CWL_REGULAR_MODE:
                    dtime = battlesBeforeStartLag
                if isInQueue:
                    textid = TOOLTIPS.STRONGHOLDS_TIMER_SQUADINQUEUE
                    if dtime < 0 or dtime > battlesBeforeStartLag:
                        dtime = 0
                elif isInBattle:
                    textid = TOOLTIPS.STRONGHOLDS_TIMER_SQUADINBATTLE
                elif self.isStrongholdUnitWaitingForData():
                    textid = TOOLTIPS.STRONGHOLDS_TIMER_WAITINGFORDATA
                elif dtime > battlesBeforeStartLag:
                    textid = FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_UNAVAILABLE
                    if matchmakerNextTick is not None:
                        peripheryStartTimeUTC, _ = self.__calculatePeripheryTimeHelper(clientTimeUTC)
                        peripheryStartTimestampUTC = int(time_utils.getTimestampFromUTC(peripheryStartTimeUTC.timetuple()))
                        currentTimestampUTC = int(time_utils.getTimestampFromUTC(clientTimeUTC.timetuple()))
                        currentTimestamp = self._convertUTCStructToLocalTimestamp(clientTimeUTC)
                        dtime = int(matchmakerNextTick - currentTimestampUTC)
                        matchmakerNextTickLocal = time_utils.getDateTimeInUTC(matchmakerNextTick)
                        matchmakerNextTickLocal = self._convertUTCStructToLocalTimestamp(matchmakerNextTickLocal)
                        currDayStart, currDayEnd = time_utils.getDayTimeBoundsForLocal(matchmakerNextTickLocal)
                        if currDayStart - time_utils.ONE_DAY <= currentTimestamp <= currDayEnd - time_utils.ONE_DAY:
                            textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETOMORROW
                        elif currDayStart <= currentTimestamp <= currDayEnd:
                            textid = FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETODAY
                elif dtime >= 0:
                    textid = FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON
                    if dtime <= self.MATCHMAKING_BATTLE_BUTTON_BATTLE or not self.__strongholdSettings.isFirstBattle():
                        inactiveMatchingButton = False
                else:
                    dtimeWD = dtime + self.MATCHMAKING_ZERO_TIME_WAITING_FOR_DATA
                    if dtimeWD >= 0:
                        textid = FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON
                    dtime = 0
        if mode & self.CWL_REGULAR_MODE == self.CWL_REGULAR_MODE:
            self.__prevMatchmakingTimerState = textid
        if mode & self.CWL_INVOKE_LISTENERS == self.CWL_INVOKE_LISTENERS:
            header = self.__strongholdSettings.getHeader()
            g_eventDispatcher.strongholdsOnTimer({'peripheryStartTimestamp': peripheryStartTimestampUTC,
             'matchmakerNextTick': matchmakerNextTick,
             'clan': header.getClan(),
             'enemyClan': header.getEnemyClan(),
             'textid': textid,
             'dtime': dtime,
             'isSortie': self.__strongholdSettings.isSortie(),
             'isFirstBattle': self.__strongholdSettings.isFirstBattle(),
             'currentBattle': header.getCurrentBattle(),
             'maxLevel': header.getMaxLevel(),
             'direction': header.getDirection(),
             'forceUpdateBuildings': forceUpdateBuildings})
        if mode & self.CWL_RETURN_MATCHING_BUTTON_STATUS == self.CWL_RETURN_MATCHING_BUTTON_STATUS:
            return inactiveMatchingButton
        else:
            return matchmakerNextTick if mode & self.CWL_RETURN_MATCHMAKER_NEXT_TICK == self.CWL_RETURN_MATCHMAKER_NEXT_TICK else None
