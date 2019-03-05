# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/legacy/entity.py
import BigWorld
import account_helpers
from soft_exception import SoftException
from PlayerEvents import g_playerEvents
from constants import PREBATTLE_ACCOUNT_STATE, REQUEST_COOLDOWN, PREBATTLE_ERRORS
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.legacy.actions_validator import LegacyActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters import messages
from gui.prb_control.entities.base.cooldown import PrbCooldownManager
from gui.prb_control.entities.base.entity import BasePrbEntryPoint, BasePrbEntity
from gui.prb_control.entities.base.legacy.ctx import JoinLegacyModeCtx
from gui.prb_control.entities.base.legacy.limits import LegacyLimits
from gui.prb_control.entities.base.legacy.listener import ILegacyListener, ILegacyIntroListener
from gui.prb_control.entities.base.legacy.permissions import ILegacyPermissions, LegacyIntroPermissions, LegacyPermissions
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from gui.prb_control.items import prb_items
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE, PREBATTLE_ROSTER, REQUEST_TYPE, PREBATTLE_INIT_STEP, makePrebattleSettings
from gui.shared.utils.listeners_collection import ListenersCollection
from prebattle_shared import decodeRoster

class BaseLegacyEntity(BasePrbEntity):

    def init(self, clientPrb=None, ctx=None):
        return super(BaseLegacyEntity, self).init()

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        return super(BaseLegacyEntity, self).fini()

    def getCtrlType(self):
        return CTRL_ENTITY_TYPE.LEGACY

    def getSettings(self):
        return makePrebattleSettings()

    def getRosterKey(self, pID=None):
        return PREBATTLE_ROSTER.UNKNOWN

    def getRosters(self, keys=None):
        return dict.fromkeys(PREBATTLE_ROSTER.ALL, [])

    def getPlayerInfo(self, pID=None, rosterKey=None):
        return prb_items.PlayerPrbInfo(-1L)

    def getPlayerInfoByDbID(self, dbID):
        return prb_items.PlayerPrbInfo(-1L)

    def getPlayerTeam(self, pID=None):
        pass

    def getTeamState(self, team=None):
        return prb_items.TeamStateInfo(0)

    def getPlayersStateStats(self):
        return prb_items.PlayersStateStats(0, False, 0, 0)

    def getRoles(self, pDatabaseID=None, clanDBID=None, team=None):
        pass

    def getPermissions(self, pID=None):
        return ILegacyPermissions()

    def getLimits(self):
        return None

    def exitFromQueue(self):
        return False

    def hasGUIPage(self):
        return False

    def isGUIProcessed(self):
        return False


class LegacyIntroEntryPoint(BasePrbEntryPoint):

    def __init__(self, modeFlags, prbType):
        super(LegacyIntroEntryPoint, self).__init__(entityFlags=FUNCTIONAL_FLAG.LEGACY_INTRO, modeFlags=modeFlags)
        self._prbType = prbType

    def makeDefCtx(self):
        return JoinLegacyModeCtx(self._prbType)

    def create(self, ctx, callback=None):
        raise SoftException('PrbIntro is not create entity')

    def join(self, ctx, callback=None):
        if ctx.isForced():
            g_prbCtrlEvents.onLegacyIntroModeJoined(ctx.getEntityType())
            if callback:
                callback(True)

    def select(self, ctx, callback=None):
        self.join(ctx, callback)


class LegacyEntryPoint(BasePrbEntryPoint):

    def __init__(self, modeFlags):
        super(LegacyEntryPoint, self).__init__(entityFlags=FUNCTIONAL_FLAG.LEGACY, modeFlags=modeFlags)

    def create(self, ctx, callback=None):
        LOG_ERROR('Routine "create" must be implemented in subclass')

    def join(self, ctx, callback=None):
        if prb_getters.getClientPrebattle() is None or ctx.isForced():
            ctx.startProcessing(callback=callback)
            BigWorld.player().prb_join(ctx.getID())
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle', prb_getters.getPrebattleType())
            if callback:
                callback(False)
        return

    def select(self, ctx, callback=None):
        self.join(ctx, callback)


class _LegacyEntity(BaseLegacyEntity, ListenersCollection):

    def __init__(self, entityFlags, modeFlags, listenerClass, requestHandlers=None):
        super(_LegacyEntity, self).__init__(entityFlags=entityFlags, modeFlags=modeFlags)
        self._setListenerClass(listenerClass)
        self._requestHandlers = requestHandlers or {}
        self._deferredReset = False

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        self._requestHandlers.clear()
        self._deferredReset = False
        return super(_LegacyEntity, self).fini(clientPrb, ctx=ctx, woEvents=woEvents)

    def request(self, ctx, callback=None):
        requestType = ctx.getRequestType()
        handler = None
        if requestType in self._requestHandlers:
            handler = self._requestHandlers[requestType]
        if handler:
            LOG_DEBUG('Prebattle request', ctx)
            handler(ctx, callback=callback)
        else:
            LOG_ERROR('Handler not found', ctx)
            if callback:
                callback(False)
        return


class LegacyIntroEntity(_LegacyEntity):

    def __init__(self, modeFlags, prbType, listReq, requestHandlers=None):
        super(LegacyIntroEntity, self).__init__(FUNCTIONAL_FLAG.LEGACY_INTRO, modeFlags, ILegacyIntroListener, requestHandlers)
        self._prbType = prbType
        self._listReq = listReq

    def init(self, clientPrb=None, ctx=None):
        if self._listReq:
            self._listReq.start(self._onListReceived)
        return super(LegacyIntroEntity, self).init(clientPrb, ctx=ctx)

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        if self._listReq:
            self._listReq.stop()
            self._listReq = None
        result = super(LegacyIntroEntity, self).fini(clientPrb, woEvents=woEvents)
        self.clear()
        return result

    def getEntityType(self):
        return self._prbType

    def getPermissions(self, pID=None):
        return LegacyIntroPermissions()

    def getConfirmDialogMeta(self, ctx):
        return rally_dialog_meta.createPrbIntroLeaveMeta(ctx, self.getEntityType(), self.canSwitch(ctx))

    def leave(self, ctx, callback=None):
        g_prbCtrlEvents.onLegacyIntroModeLeft()
        if callback is not None:
            callback(True)
        return

    def _onListReceived(self, prebattles):
        self._invokeListeners('onLegacyListReceived', prebattles)


class LegacyInitEntity(BaseLegacyEntity):

    def __init__(self):
        super(LegacyInitEntity, self).__init__(FUNCTIONAL_FLAG.LEGACY_INIT, FUNCTIONAL_FLAG.UNDEFINED)
        self.__prbInitSteps = 0

    def init(self, clientPrb=None, ctx=None):
        result = super(LegacyInitEntity, self).init(clientPrb=clientPrb, ctx=ctx)
        if clientPrb is None:
            clientPrb = prb_getters.getClientPrebattle()
        if clientPrb is not None:
            clientPrb.onSettingsReceived += self.prb_onSettingsReceived
            clientPrb.onRosterReceived += self.prb_onRosterReceived
            if prb_getters.isPrebattleSettingsReceived(prebattle=clientPrb):
                self.prb_onSettingsReceived()
            if prb_getters.getPrebattleRosters(prebattle=clientPrb):
                self.prb_onRosterReceived()
        return result

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        if clientPrb is None:
            clientPrb = prb_getters.getClientPrebattle()
        if clientPrb is not None:
            clientPrb.onSettingsReceived -= self.prb_onSettingsReceived
            clientPrb.onRosterReceived -= self.prb_onRosterReceived
        return super(LegacyInitEntity, self).fini(clientPrb=clientPrb, ctx=ctx, woEvents=woEvents)

    def prb_onSettingsReceived(self):
        LOG_DEBUG('prb_onSettingsReceived')
        self.__prbInitSteps |= PREBATTLE_INIT_STEP.SETTING_RECEIVED
        self.__isPrebattleInited()

    def prb_onRosterReceived(self):
        LOG_DEBUG('prb_onRosterReceived')
        self.__prbInitSteps |= PREBATTLE_INIT_STEP.ROSTERS_RECEIVED
        self.__isPrebattleInited()

    def __isPrebattleInited(self):
        result = False
        if self.__prbInitSteps is PREBATTLE_INIT_STEP.INITED:
            g_prbCtrlEvents.onLegacyInited()
            result = True
            self.__prbInitSteps = 0
        return result


class LegacyEntity(_LegacyEntity):

    def __init__(self, modeFlags, settings, permClass=None, limits=None, requestHandlers=None):
        super(LegacyEntity, self).__init__(FUNCTIONAL_FLAG.LEGACY, modeFlags, ILegacyListener, requestHandlers)
        self._settings = settings
        self._permClass = permClass or LegacyPermissions
        self._limits = limits or LegacyLimits(self)
        self._cooldown = PrbCooldownManager()

    def init(self, clientPrb=None, ctx=None):
        if clientPrb is None:
            clientPrb = prb_getters.getClientPrebattle()
        if clientPrb is not None:
            clientPrb.onSettingUpdated += self.prb_onSettingUpdated
            clientPrb.onRosterReceived += self.prb_onRosterReceived
            clientPrb.onTeamStatesReceived += self.prb_onTeamStatesReceived
            clientPrb.onPlayerStateChanged += self.prb_onPlayerStateChanged
            clientPrb.onPlayerRosterChanged += self.prb_onPlayerRosterChanged
            clientPrb.onPlayerAdded += self.prb_onPlayerAdded
            clientPrb.onPlayerRemoved += self.prb_onPlayerRemoved
            clientPrb.onKickedFromQueue += self.prb_onKickedFromQueue
        else:
            LOG_ERROR('ClientPrebattle is not defined')
        return super(LegacyEntity, self).init(clientPrb, ctx)

    def fini(self, clientPrb=None, ctx=None, woEvents=False):
        self._settings = None
        result = super(LegacyEntity, self).fini(clientPrb, ctx=ctx, woEvents=woEvents)
        if self._limits is not None:
            self._limits.clear()
            self._limits = None
        self.clear()
        if clientPrb is None:
            clientPrb = prb_getters.getClientPrebattle()
        if clientPrb is not None:
            clientPrb.onSettingUpdated -= self.prb_onSettingUpdated
            clientPrb.onTeamStatesReceived -= self.prb_onTeamStatesReceived
            clientPrb.onPlayerStateChanged -= self.prb_onPlayerStateChanged
            clientPrb.onPlayerRosterChanged -= self.prb_onPlayerRosterChanged
            clientPrb.onPlayerAdded -= self.prb_onPlayerAdded
            clientPrb.onPlayerRemoved -= self.prb_onPlayerRemoved
            clientPrb.onKickedFromQueue -= self.prb_onKickedFromQueue
        return result

    def isPlayerJoined(self, ctx):
        return ctx.getCtrlType() is CTRL_ENTITY_TYPE.LEGACY and ctx.getEntityType() == self.getEntityType() and ctx.getID() == self.getID()

    def getID(self):
        return prb_getters.getPrebattleID()

    def getEntityType(self):
        return self._settings['type'] if self._settings else 0

    def getSettings(self):
        return self._settings

    def getLimits(self):
        return self._limits

    def getPermissions(self, pID=None):
        clazz = self._permClass
        rosterKey = self.getRosterKey(pID=pID)
        if rosterKey is not None:
            team, _ = decodeRoster(rosterKey)
            pInfo = self.getPlayerInfo(pID=pID, rosterKey=rosterKey)
            if pInfo is not None:
                return clazz(roles=self.getRoles(pDatabaseID=pInfo.dbID, clanDBID=pInfo.clanDBID, team=team), pState=pInfo.state, teamState=self.getTeamState(team=team), hasLockedState=self.hasLockedState())
        return clazz()

    def isCommander(self, pDatabaseID=None):
        return self._permClass.isCreator(self.getRoles(pDatabaseID=pDatabaseID))

    def hasLockedState(self):
        if g_playerEvents.isPlayerEntityChanging:
            return True
        _, assigned = decodeRoster(self.getRosterKey())
        return self.getTeamState().isInQueue() and self.getPlayerInfo().isReady() and assigned

    def getConfirmDialogMeta(self, ctx):
        if not self._settings or ctx.isForced():
            return None
        else:
            prbType = self.getEntityType()
            if self.hasLockedState():
                meta = rally_dialog_meta.RallyLeaveDisabledDialogMeta(CTRL_ENTITY_TYPE.LEGACY, prbType)
            else:
                meta = rally_dialog_meta.createPrbLeaveMeta(ctx, prbType, self.canSwitch(ctx))
            return meta

    def getRosterKey(self, pID=None):
        rosters = prb_getters.getPrebattleRosters()
        rosterRange = PREBATTLE_ROSTER.getRange(self.getEntityType())
        if pID is None:
            pID = account_helpers.getPlayerID()
        for roster in rosterRange:
            if roster in rosters and pID in rosters[roster].keys():
                return roster

        return PREBATTLE_ROSTER.UNKNOWN

    def getPlayerInfo(self, pID=None, rosterKey=None):
        rosters = prb_getters.getPrebattleRosters()
        if pID is None:
            pID = account_helpers.getPlayerID()
        if rosterKey is not None:
            if rosterKey in rosters and pID in rosters[rosterKey].keys():
                return prb_items.PlayerPrbInfo(pID, entity=self, roster=rosterKey, **rosters[rosterKey][pID])
        else:
            rosterRange = PREBATTLE_ROSTER.getRange(self.getEntityType())
            for roster in rosterRange:
                if roster in rosters and pID in rosters[roster].keys():
                    return prb_items.PlayerPrbInfo(pID, entity=self, roster=roster, **rosters[roster][pID])

        return prb_items.PlayerPrbInfo(-1L)

    def getPlayerInfoByDbID(self, dbID):
        rosters = prb_getters.getPrebattleRosters()
        rosterRange = PREBATTLE_ROSTER.getRange(self.getEntityType())
        for roster in rosterRange:
            if roster in rosters:
                for pID, data in rosters[roster].iteritems():
                    if data['dbID'] == dbID:
                        return prb_items.PlayerPrbInfo(pID, entity=self, roster=roster, **rosters[roster][pID])

        return prb_items.PlayerPrbInfo(-1L)

    def getPlayerTeam(self, pID=None):
        team = 0
        roster = self.getRosterKey(pID=pID)
        if roster is not PREBATTLE_ROSTER.UNKNOWN:
            team, _ = decodeRoster(roster)
        return team

    def getTeamState(self, team=None):
        result = prb_items.TeamStateInfo(0)
        if team is None:
            roster = self.getRosterKey()
            if roster is not PREBATTLE_ROSTER.UNKNOWN:
                team, _ = decodeRoster(self.getRosterKey())
        teamStates = prb_getters.getPrebattleTeamStates()
        if team is not None and team < len(teamStates):
            result = prb_items.TeamStateInfo(teamStates[team])
        return result

    def getRoles(self, pDatabaseID=None, clanDBID=None, team=None):
        result = 0
        if self._settings is None:
            return result
        else:
            if pDatabaseID is None:
                pDatabaseID = account_helpers.getAccountDatabaseID()
            roles = self._settings['roles']
            if pDatabaseID in roles:
                result = roles[pDatabaseID]
            if not result and clanDBID:
                roles = self._settings['clanRoles']
                if clanDBID in roles:
                    result = roles[clanDBID]
            if not result and team:
                roles = self._settings['teamRoles']
                if team in roles:
                    result = roles[team]
            return result

    def getProps(self):
        return prb_items.PrbPropsInfo(**prb_getters.getPrebattleProps())

    def leave(self, ctx, callback=None):
        ctx.startProcessing(callback)
        BigWorld.player().prb_leave(lambda *args: None)

    def resetPlayerState(self):

        def setNotReady(code):
            if code >= 0:
                BigWorld.player().prb_notReady(PREBATTLE_ACCOUNT_STATE.NOT_READY, lambda *args: None)

        if self.isCommander() and self.getTeamState().isInQueue():
            BigWorld.player().prb_teamNotReady(self.getPlayerTeam(), setNotReady)
        elif self.getPlayerInfo().isReady():
            if self.getTeamState().isInQueue():
                self._deferredReset = True
            else:
                setNotReady(0)

    def assign(self, ctx, callback=None):
        prevTeam, _ = decodeRoster(self.getRosterKey(pID=ctx.getPlayerID()))
        nextTeam, assigned = decodeRoster(ctx.getRoster())
        pPermissions = self.getPermissions()
        if prevTeam is nextTeam:
            if not pPermissions.canAssignToTeam(team=nextTeam):
                LOG_ERROR('Player can not change roster', nextTeam, assigned)
                if callback:
                    callback(False)
                return
        elif not pPermissions.canChangePlayerTeam():
            LOG_ERROR('Player can not change team', prevTeam, nextTeam)
            if callback:
                callback(False)
            return
        result = self.getLimits().isMaxCountValid(nextTeam, assigned)
        if result is not None and not result.isValid:
            LOG_ERROR('Max count limit', nextTeam, assigned)
            ctx.setErrorString(PREBATTLE_ERRORS.ROSTER_LIMIT)
            if callback:
                callback(False)
            return
        else:
            ctx.startProcessing(callback)
            BigWorld.player().prb_assign(ctx.getPlayerID(), ctx.getRoster(), ctx.onResponseReceived)
            return

    def setTeamState(self, ctx, callback=None):
        team = ctx.getTeam()
        if not self.getPermissions().canSetTeamState(team=team):
            LOG_ERROR('Player can not change state of team', team)
            if callback:
                callback(False)
            return
        teamState = self.getTeamState()
        setReady = ctx.isReadyState()
        if setReady and teamState.isNotReady():
            if teamState.isLocked():
                LOG_ERROR('Team is locked')
                if callback:
                    callback(False)
            else:
                self._setTeamReady(ctx, callback=callback)
        elif not setReady and teamState.isInQueue():
            self._setTeamNotReady(ctx, callback=callback)
        elif callback:
            callback(True)

    def setPlayerState(self, ctx, callback=None):
        playerInfo = self.getPlayerInfo()
        if playerInfo is not None:
            playerIsReady = playerInfo.isReady()
            setReady = ctx.isReadyState()
            if setReady and not playerIsReady:
                self._setPlayerReady(ctx, callback=callback)
            elif not setReady and playerIsReady:
                self._setPlayerNotReady(ctx, callback=callback)
            elif callback:
                callback(True)
        else:
            LOG_ERROR('Account info not found in prebattle.rosters', ctx)
            if callback:
                callback(False)
        return

    def kickPlayer(self, ctx, callback=None):
        pID = ctx.getPlayerID()
        rosterKey = self.getRosterKey(pID=pID)
        team, assigned = decodeRoster(rosterKey)
        pPermissions = self.getPermissions()
        if not pPermissions.canKick(team=team):
            LOG_ERROR('Player can not kick from team', team, pPermissions)
            if callback:
                callback(False)
            return
        if assigned and self.getPlayerInfo(pID=pID, rosterKey=rosterKey).isReady():
            if self.getTeamState(team=team).isInQueue():
                LOG_ERROR('Player is ready, assigned and team is ready or locked', ctx)
                if callback:
                    callback(False)
                return
        ctx.startProcessing(callback)
        BigWorld.player().prb_kick(ctx.getPlayerID(), ctx.onResponseReceived)

    def swapTeams(self, ctx, callback=None):
        if self._cooldown.validate(REQUEST_TYPE.SWAP_TEAMS):
            if callback:
                callback(False)
            return
        pPermissions = self.getPermissions()
        if self.getPermissions().canChangePlayerTeam():
            ctx.startProcessing(callback)
            BigWorld.player().prb_swapTeams(ctx.onResponseReceived)
            self._cooldown.process(REQUEST_TYPE.SWAP_TEAMS)
        else:
            LOG_ERROR('Player can not swap teams', pPermissions)
            if callback:
                callback(False)

    def sendInvites(self, ctx, callback=None):
        if self._cooldown.validate(REQUEST_TYPE.SEND_INVITE):
            if callback:
                callback(False)
            return
        pPermissions = self.getPermissions()
        if self.getPermissions().canSendInvite():
            BigWorld.player().prb_sendInvites(ctx.getDatabaseIDs(), ctx.getComment())
            self._cooldown.process(REQUEST_TYPE.SEND_INVITE, coolDown=REQUEST_COOLDOWN.PREBATTLE_INVITES)
            if callback:
                callback(True)
        else:
            LOG_ERROR('Player can not send invite', pPermissions)
            if callback:
                callback(False)

    def prb_onSettingUpdated(self, settingName):
        settingValue = self._settings[settingName]
        LOG_DEBUG('prb_onSettingUpdated', settingName, settingValue)
        self._invokeListeners('onSettingUpdated', self, settingName, settingValue)

    def prb_onTeamStatesReceived(self):
        team1State = self.getTeamState(team=1)
        team2State = self.getTeamState(team=2)
        LOG_DEBUG('prb_onTeamStatesReceived', team1State, team2State)
        if self._deferredReset and not self.getTeamState().isInQueue():
            self._deferredReset = False
            self.resetPlayerState()
        self._invokeListeners('onTeamStatesReceived', self, team1State, team2State)

    def prb_onPlayerStateChanged(self, pID, roster):
        accountInfo = self.getPlayerInfo(pID=pID)
        LOG_DEBUG('prb_onPlayerStateChanged', accountInfo)
        self._invokeListeners('onPlayerStateChanged', self, roster, accountInfo)

    def prb_onRosterReceived(self):
        LOG_DEBUG('prb_onRosterReceived')
        rosters = self.getRosters()
        self._invokeListeners('onRostersChanged', self, rosters, True)
        team = self.getPlayerTeam()
        self._invokeListeners('onPlayerTeamNumberChanged', self, team)

    def prb_onPlayerRosterChanged(self, pID, prevRoster, roster, actorID):
        LOG_DEBUG('prb_onPlayerRosterChanged', pID, prevRoster, roster, actorID)
        rosters = self.getRosters(keys=[prevRoster, roster])
        actorInfo = self.getPlayerInfo(pID=actorID)
        playerInfo = self.getPlayerInfo(pID=pID)
        for listener in self.getListenersIterator():
            if actorInfo and playerInfo:
                listener.onPlayerRosterChanged(self, actorInfo, playerInfo)
            listener.onRostersChanged(self, rosters, False)

        if pID == account_helpers.getPlayerID():
            prevTeam, _ = decodeRoster(prevRoster)
            currentTeam, _ = decodeRoster(roster)
            if currentTeam is not prevTeam:
                self._invokeListeners('onPlayerTeamNumberChanged', self, currentTeam)

    def prb_onPlayerAdded(self, pID, roster):
        LOG_DEBUG('prb_onPlayerAdded', pID, roster)
        rosters = self.getRosters(keys=[roster])
        playerInfo = self.getPlayerInfo(pID=pID, rosterKey=roster)
        for listener in self.getListenersIterator():
            listener.onPlayerAdded(self, playerInfo)
            listener.onRostersChanged(self, rosters, False)

    def prb_onPlayerRemoved(self, pID, roster, name):
        LOG_DEBUG('prb_onPlayerRemoved', pID, roster, name)
        rosters = self.getRosters(keys=[roster])
        playerInfo = prb_items.PlayerPrbInfo(pID, name=name)
        for listener in self.getListenersIterator():
            listener.onPlayerRemoved(self, playerInfo)
            listener.onRostersChanged(self, rosters, False)

    def prb_onKickedFromQueue(self):
        LOG_DEBUG('prb_onKickedFromQueue')
        message = messages.getPrbKickedFromQueueMessage(prb_getters.getPrebattleTypeName(self.getEntityType()))
        if message:
            SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Warning)

    def _createActionsValidator(self):
        return LegacyActionsValidator(self)

    def _setTeamReady(self, ctx, callback=None):
        if prb_getters.isParentControlActivated():
            g_eventDispatcher.showParentControlNotification()
            if callback:
                callback(False)
            return
        else:
            result = self._limits.isTeamValid()

            def _requestResponse(code, errStr):
                msg = messages.getInvalidTeamServerMessage(errStr, entity=self)
                if msg is not None:
                    SystemMessages.pushMessage(msg, type=SystemMessages.SM_TYPE.Error)
                ctx.onResponseReceived(code)
                return

            if result is None or result.isValid:
                ctx.startProcessing(callback)
                BigWorld.player().prb_teamReady(ctx.getTeam(), ctx.isForced(), ctx.getGamePlayMask(), _requestResponse)
            else:
                notValidReason = result.restriction
                LOG_ERROR('Team is invalid', notValidReason)
                if callback:
                    callback(False)
                SystemMessages.pushMessage(messages.getInvalidTeamMessage(notValidReason, entity=self), type=SystemMessages.SM_TYPE.Error)
            return

    def _setTeamNotReady(self, ctx, callback=None):
        if self._cooldown.validate(REQUEST_TYPE.SET_TEAM_STATE):
            if callback:
                callback(False)
            return
        ctx.startProcessing(callback)
        BigWorld.player().prb_teamNotReady(ctx.getTeam(), ctx.onResponseReceived)
        self._cooldown.process(REQUEST_TYPE.SET_TEAM_STATE, coolDown=REQUEST_COOLDOWN.PREBATTLE_TEAM_NOT_READY)

    def _setPlayerNotReady(self, ctx, callback=None):
        if self._cooldown.validate(REQUEST_TYPE.SET_PLAYER_STATE, REQUEST_COOLDOWN.PREBATTLE_NOT_READY):
            if callback:
                callback(False)
            return
        rosterKey = self.getRosterKey()
        team, assigned = decodeRoster(rosterKey)
        if assigned and self.getTeamState(team=team).isInQueue():
            LOG_ERROR('Account assigned and team is ready or locked')
            if callback:
                callback(False)
            return
        ctx.startProcessing(callback)
        BigWorld.player().prb_notReady(PREBATTLE_ACCOUNT_STATE.NOT_READY, ctx.onResponseReceived)
        self._cooldown.process(REQUEST_TYPE.SET_PLAYER_STATE, coolDown=REQUEST_COOLDOWN.PREBATTLE_NOT_READY)

    def _setPlayerReady(self, ctx, callback=None):
        if prb_getters.isParentControlActivated():
            g_eventDispatcher.showParentControlNotification()
            if callback:
                callback(False)
            return
        if ctx.doVehicleValidation():
            result = self._limits.isVehicleValid()
            if not self._processValidationResult(ctx, result):
                if callback:
                    callback(False)
                return
        rosterKey = self.getRosterKey()
        team, assigned = decodeRoster(rosterKey)
        if assigned and self.getTeamState(team=team).isInQueue():
            LOG_ERROR('Account assigned and team is ready or locked')
            if callback:
                callback(False)
            return
        ctx.startProcessing(callback)
        BigWorld.player().prb_ready(ctx.getVehicleInventoryID(), ctx.onResponseReceived)

    def _processValidationResult(self, ctx, result):
        if result is not None and not result.isValid:
            if not (ctx.isInitial() and result.restriction == PREBATTLE_RESTRICTION.VEHICLE_NOT_READY):
                SystemMessages.pushMessage(messages.getInvalidVehicleMessage(result.restriction, self), type=SystemMessages.SM_TYPE.Error)
            return False
        else:
            return True

    def _getPlayersStateStats(self, rosterKey):
        clientPrb = prb_getters.getClientPrebattle()
        notReadyCount = 0
        playersCount = 0
        limitMaxCount = 0
        haveInBattle = False
        if clientPrb:
            players = clientPrb.rosters.get(rosterKey, {})
            playersCount = len(players)
            team, assigned = decodeRoster(rosterKey)
            teamLimits = self._settings.getTeamLimits(team)
            limitMaxCount = teamLimits['maxCount'][not assigned]
            for _, accInfo in players.iteritems():
                state = accInfo.get('state', PREBATTLE_ACCOUNT_STATE.UNKNOWN)
                if not state & PREBATTLE_ACCOUNT_STATE.READY:
                    notReadyCount += 1
                    if not haveInBattle and state & PREBATTLE_ACCOUNT_STATE.IN_BATTLE:
                        haveInBattle = True

        return prb_items.PlayersStateStats(notReadyCount, haveInBattle, playersCount, limitMaxCount)
