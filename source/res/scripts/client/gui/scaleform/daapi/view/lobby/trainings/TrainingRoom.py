# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/TrainingRoom.py
import BigWorld
import ArenaType
from adisp import process
from gui import SystemMessages, GUI_SETTINGS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.Scaleform.daapi.view.lobby.trainings.sound_constants import TRAININGS_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.TrainingRoomMeta import TrainingRoomMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.legacy.ctx import SetTeamStateCtx, AssignLegacyCtx, SwapTeamsCtx
from gui.prb_control.entities.base.legacy.listener import ILegacyListener
from gui.prb_control.entities.training.legacy.ctx import SetPlayerObserverStateCtx, ChangeArenaVoipCtx
from gui.prb_control.items.prb_items import getPlayersComparator
from gui.prb_control.settings import PREBATTLE_ROSTER, PREBATTLE_SETTING_NAME
from gui.prb_control.settings import REQUEST_TYPE, CTRL_ENTITY_TYPE
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.events import CoolDownEvent
from gui.shared.formatters import text_styles
from gui.sounds.ambients import LobbySubViewEnv
from helpers import dependency
from helpers import int2roman, i18n
from helpers.statistics import HANGAR_LOADING_STATE
from messenger.ext import passCensor
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from prebattle_shared import decodeRoster
from constants import PREBATTLE_MAX_OBSERVERS_IN_TEAM, OBSERVERS_BONUS_TYPES, PREBATTLE_ERRORS, PREBATTLE_TYPE
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.helpers.statistics import IStatisticsCollector

class TrainingRoom(LobbySubView, TrainingRoomMeta, ILegacyListener):
    __sound_env__ = LobbySubViewEnv
    _COMMON_SOUND_SPACE = TRAININGS_SOUND_SPACE
    lobbyContext = dependency.descriptor(ILobbyContext)
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, _=None):
        super(TrainingRoom, self).__init__()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def _populate(self):
        super(TrainingRoom, self)._populate()
        funcState = self.prbDispatcher.getFunctionalState()
        if not funcState.isInLegacy(PREBATTLE_TYPE.TRAINING):
            g_eventDispatcher.removeTrainingFromCarousel(False)
            return
        entity = self.prbEntity
        if entity.getEntityType():
            self.__showSettings(entity)
            self.__showRosters(entity, entity.getRosters())
            self.__swapTeamsInMinimap(entity.getPlayerTeam())
        self.startPrbListening()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__updateTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_setObserverS(entity.getPlayerInfo().getVehicle().isObserver)
        g_messengerEvents.users.onUserActionReceived += self.__me_onUserActionReceived
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.TRAINING_UI_READY, showSummaryNow=True)

    def _dispose(self):
        self.stopPrbListening()
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__updateTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        g_messengerEvents.users.onUserActionReceived -= self.__me_onUserActionReceived
        self.__closeWindows()
        super(TrainingRoom, self)._dispose()

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def showTrainingSettings(self):
        self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY, ctx={'isCreateRequest': False}), scope=EVENT_BUS_SCOPE.LOBBY)

    def onWindowMinimize(self):
        g_eventDispatcher.loadHangar()

    def onTryClosing(self):
        self._dispose()
        return True

    def canSendInvite(self):
        return self.prbEntity.getPermissions().canSendInvite() if self.prbEntity else False

    def canChangePlayerTeam(self):
        return self.prbEntity.getPermissions().canChangePlayerTeam() if self.prbEntity else False

    def canChangeSetting(self):
        return self.prbEntity.getPermissions().canChangeSetting() if self.prbEntity else False

    def canStartBattle(self):
        return self.prbEntity.getPermissions().canStartBattle() if self.prbEntity else False

    def canAssignToTeam(self, team):
        return self.prbEntity.getPermissions().canAssignToTeam(int(team)) if self.prbEntity else False

    def canDestroyRoom(self):
        if self.prbEntity:
            prbSettings = self.prbEntity.getSettings()
            playerName = BigWorld.player().name
            return prbSettings[PREBATTLE_SETTING_NAME.CREATOR] == playerName and prbSettings[PREBATTLE_SETTING_NAME.DESTROY_IF_CREATOR_OUT]
        return False

    def getPlayerTeam(self, accID):
        return self.prbEntity.getPlayerTeam(accID)

    def showPrebattleInvitationsForm(self):
        self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ctx={'prbName': 'training',
         'ctrlType': CTRL_ENTITY_TYPE.LEGACY}), scope=EVENT_BUS_SCOPE.LOBBY)

    def startTraining(self):
        self.__closeWindows()
        self.__doStartTraining()

    @process
    def __updateTrainingRoom(self, event):
        self._closeWindow(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY)
        prbSettings = event.ctx.get('settings', None)
        if prbSettings and prbSettings.areSettingsChanged(self.prbEntity.getSettings()):
            prbSettings.setWaitingID('prebattle/change_settings')
            result = yield self.prbDispatcher.sendPrbRequest(prbSettings)
            if not result:
                self.__showActionErrorMessage()
        return

    @process
    def __doStartTraining(self):
        result = yield self.prbDispatcher.sendPrbRequest(SetTeamStateCtx(1, True))
        if result:
            result = yield self.prbDispatcher.sendPrbRequest(SetTeamStateCtx(2, True))
            if not result:
                yield self.prbDispatcher.sendPrbRequest(SetTeamStateCtx(1, False))
        if not result:
            self.__showActionErrorMessage()
            self.as_disableControlsS(False)
            self.__updateStartButton(self.prbEntity)

    def onTeamStatesReceived(self, entity, team1State, team2State):
        _, assigned = decodeRoster(entity.getRosterKey())
        if team1State.isInQueue() and team2State.isInQueue() and assigned:
            self.as_disableControlsS(True)
        elif assigned is False:
            self.as_enabledCloseButtonS(True)

    def closeTrainingRoom(self):
        self._doLeave(False)

    def __getPlayersMaxCount(self):
        playersMaxCount = self.prbEntity.getTeamLimits()['maxCount'][0]
        if self.prbEntity.getSettings()['bonusType'] in OBSERVERS_BONUS_TYPES:
            playersMaxCount -= PREBATTLE_MAX_OBSERVERS_IN_TEAM
        return playersMaxCount

    def __showActionErrorMessage(self, errType=None):
        errors = {PREBATTLE_ERRORS.ROSTER_LIMIT: (SYSTEM_MESSAGES.TRAINING_ERROR_ADDPLAYER, {}),
         PREBATTLE_ERRORS.PLAYERS_LIMIT: (SYSTEM_MESSAGES.TRAINING_ERROR_SELECTOBSERVER, {'numPlayers': self.__getPlayersMaxCount()})}
        errMsg = errors.get(errType, (SYSTEM_MESSAGES.TRAINING_ERROR_DOACTION, {}))
        SystemMessages.pushMessage(i18n.makeString(errMsg[0], **errMsg[1]), type=SystemMessages.SM_TYPE.Error)

    @process
    def changeTeam(self, accID, slot):
        roster = int(slot)
        if not slot:
            roster = self.prbEntity.getRosterKey(accID)
            if not roster & PREBATTLE_ROSTER.UNASSIGNED:
                roster |= PREBATTLE_ROSTER.UNASSIGNED
        ctx = AssignLegacyCtx(accID, roster, waitingID='prebattle/assign')
        result = yield self.prbDispatcher.sendPrbRequest(ctx)
        if not result:
            self.__showActionErrorMessage(ctx.getLastErrorString())

    @process
    def swapTeams(self):
        result = yield self.prbDispatcher.sendPrbRequest(SwapTeamsCtx(waitingID='prebattle/swap'))
        if not result:
            self.__showActionErrorMessage()

    @process
    def selectObserver(self, isObserver):
        if not isObserver:
            playersCount = 0
            roster = self.prbEntity.getRosterKey()
            if roster != PREBATTLE_ROSTER.UNKNOWN and roster & PREBATTLE_ROSTER.UNASSIGNED == 0:
                accounts = self.prbEntity.getRosters()[roster]
                for account in accounts:
                    if account.isVehicleSpecified():
                        vehicle = account.getVehicle()
                        if not vehicle.isObserver:
                            playersCount += 1

            playersMaxCount = self.__getPlayersMaxCount()
            if playersCount >= playersMaxCount:
                event = CoolDownEvent()
                self.as_startCoolDownObserverS(event.coolDown)
                self.as_setObserverS(not isObserver)
                self.__showActionErrorMessage(PREBATTLE_ERRORS.PLAYERS_LIMIT)
                return
        result = yield self.prbDispatcher.sendPrbRequest(SetPlayerObserverStateCtx(isObserver, True, waitingID='prebattle/change_user_status'))
        if not result:
            self.as_setObserverS(False)
            self.__showActionErrorMessage()

    @process
    def selectCommonVoiceChat(self, index):
        result = yield self.prbDispatcher.sendPrbRequest(ChangeArenaVoipCtx(int(index), waitingID='prebattle/change_arena_voip'))
        if not result:
            prbSettings = self.prbEntity.getSettings()
            self.as_setArenaVoipChannelsS(prbSettings[PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS])
            self.__showActionErrorMessage()

    def onSettingUpdated(self, entity, settingName, settingValue):
        if settingName in (PREBATTLE_SETTING_NAME.ARENA_TYPE_ID, PREBATTLE_SETTING_NAME.LIMITS):
            if settingName == PREBATTLE_SETTING_NAME.ARENA_TYPE_ID:
                arenaTypeID = settingValue
            else:
                arenaTypeID = entity.getSettings()[PREBATTLE_SETTING_NAME.ARENA_TYPE_ID]
            arenaType = ArenaType.g_cache.get(arenaTypeID)
            self.as_updateMapS(arenaTypeID, entity.getTeamLimits()['maxCount'][0] * 2, arenaType.name, formatters.getTrainingRoomTitle(arenaType), formatters.getArenaSubTypeString(arenaTypeID), arenaType.description)
        elif settingName == PREBATTLE_SETTING_NAME.ROUND_LENGTH:
            self.as_updateTimeoutS(formatters.getRoundLenString(settingValue))
        elif settingName == PREBATTLE_SETTING_NAME.COMMENT:
            self.as_updateCommentS(settingValue)
        elif settingName == PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS:
            self.as_setArenaVoipChannelsS(settingValue)
        self.__updateStartButton(entity)

    def onRostersChanged(self, entity, rosters, full):
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            self.as_setTeam1S(self.__makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1], MENU.TRAINING_INFO_TEAM1LABEL))
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
            self.as_setTeam2S(self.__makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2], MENU.TRAINING_INFO_TEAM2LABEL))
        if PREBATTLE_ROSTER.UNASSIGNED in rosters:
            self.as_setOtherS(self.__makeAccountsData(rosters[PREBATTLE_ROSTER.UNASSIGNED], MENU.TRAINING_INFO_OTHERLABEL))
        self.__updateStartButton(entity)

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        stateString = formatters.getPlayerStateString(accountInfo.state)
        vContourIcon = ''
        vShortName = ''
        vLevel = ''
        if accountInfo.isVehicleSpecified():
            vehicle = accountInfo.getVehicle()
            vContourIcon = vehicle.iconContour
            vShortName = vehicle.shortUserName
            vLevel = int2roman(vehicle.level)
        badgeID = accountInfo.getBadgeID()
        badgeIcon = accountInfo.getBadgeImgStr()
        if roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
            self.as_setPlayerStateInTeam1S(accountInfo.dbID, stateString, vContourIcon, vShortName, vLevel, accountInfo.igrType, badgeID, badgeIcon)
        elif roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2:
            self.as_setPlayerStateInTeam2S(accountInfo.dbID, stateString, vContourIcon, vShortName, vLevel, accountInfo.igrType, badgeID, badgeIcon)
        else:
            self.as_setPlayerStateInOtherS(accountInfo.dbID, stateString, vContourIcon, vShortName, vLevel, accountInfo.igrType, badgeID, badgeIcon)
        creator = self.__getCreatorFromRosters()
        if accountInfo.dbID == creator.dbID:
            self.__showSettings(entity)
        self.__updateStartButton(entity)

    def onPlayerTeamNumberChanged(self, entity, team):
        if VIEW_ALIAS.MINIMAP_LOBBY in self.components:
            self.components[VIEW_ALIAS.MINIMAP_LOBBY].swapTeams(team)

    def _closeWindow(self, windowAlias):
        window = self.app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: windowAlias})
        if window is not None:
            window.destroy()
        return

    def __closeWindows(self):
        self._closeWindow(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY)
        self._closeWindow(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY)

    def __showSettings(self, entity):
        entitySettings = entity.getSettings()
        if entitySettings is None:
            return
        else:
            isCreator = entity.isCommander()
            permissions = entity.getPermissions()
            arenaTypeID = entitySettings['arenaTypeID']
            arenaType = ArenaType.g_cache.get(arenaTypeID)
            if isCreator:
                comment = entitySettings['comment']
            else:
                comment = passCensor(entitySettings['comment'])
            creatorFullName, creatorClan, creatorRegion, creatorIgrType = (None, None, None, 0)
            creator = self.__getCreatorFromRosters()
            badgeID = 0
            badgeIcon = ''
            if creator:
                creatorFullName = creator.getFullName()
                creatorClan = creator.clanAbbrev
                creatorRegion = self.lobbyContext.getRegionCode(creator.dbID)
                creatorIgrType = creator.igrType
                badgeID = creator.getBadgeID()
                badgeIcon = creator.getBadgeImgStr()
            self.as_setInfoS({'isCreator': isCreator,
             'creator': entitySettings[PREBATTLE_SETTING_NAME.CREATOR],
             'creatorFullName': creatorFullName,
             'creatorClan': creatorClan,
             'creatorRegion': creatorRegion,
             'creatorIgrType': creatorIgrType,
             'title': formatters.getTrainingRoomTitle(arenaType),
             'arenaName': arenaType.name,
             'arenaTypeID': arenaTypeID,
             'arenaSubType': formatters.getArenaSubTypeString(arenaTypeID),
             'description': arenaType.description,
             'maxPlayersCount': entity.getTeamLimits()['maxCount'][0] * 2,
             'roundLenString': formatters.getRoundLenString(entitySettings['roundLength']),
             'comment': comment,
             'arenaVoipChannels': entitySettings[PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS],
             'canChangeArenaVOIP': permissions.canChangeArenaVOIP(),
             'isObserverModeEnabled': self.__isObserverModeEnabled(),
             'badge': badgeID,
             'badgeImgStr': badgeIcon})
            return

    def __getCreatorFromRosters(self):
        rosters = self.prbEntity.getRosters()
        for _, roster in rosters.iteritems():
            for account in roster:
                if account.isCreator:
                    return account

        return None

    def __isObserverModeEnabled(self):
        minCount = self.prbEntity.getSettings().getTeamLimits(1)['minCount']
        return GUI_SETTINGS.trainingObserverModeEnabled and minCount > 0

    def __showRosters(self, entity, rosters):
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]
        self.as_setTeam1S(self.__makeAccountsData(accounts, MENU.TRAINING_INFO_TEAM1LABEL))
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2]
        self.as_setTeam2S(self.__makeAccountsData(accounts, MENU.TRAINING_INFO_TEAM2LABEL))
        accounts = rosters[PREBATTLE_ROSTER.UNASSIGNED]
        self.as_setOtherS(self.__makeAccountsData(accounts, MENU.TRAINING_INFO_OTHERLABEL))
        self.__updateStartButton(entity)

    def __updateStartButton(self, entity):
        if entity.getPermissions().canStartBattle():
            validationResult = entity.getLimits().isTeamsValid()
            if validationResult is None or validationResult.isValid:
                self.as_enabledCloseButtonS(True)
                self.as_disableStartButtonS(False)
            else:
                self.as_disableStartButtonS(True)
        else:
            self.as_disableStartButtonS(True)
        return

    def __swapTeamsInMinimap(self, team):
        if VIEW_ALIAS.MINIMAP_LOBBY in self.components:
            self.components[VIEW_ALIAS.MINIMAP_LOBBY].swapTeams(team)

    def __makeAccountsData(self, accounts, label=None):
        listData = []
        isPlayerSpeaking = self.bwProto.voipController.isPlayerSpeaking
        accounts = sorted(accounts, cmp=getPlayersComparator())
        getUser = self.usersStorage.getUser
        for account in accounts:
            vContourIcon = ''
            vShortName = ''
            vLevel = ''
            dbID = account.dbID
            user = getUser(dbID)
            if account.isVehicleSpecified():
                vehicle = account.getVehicle()
                vContourIcon = vehicle.iconContour
                vShortName = vehicle.shortUserName
                vLevel = int2roman(vehicle.level)
            listData.append({'accID': account.accID,
             'dbID': account.dbID,
             'userName': account.name,
             'fullName': account.getFullName(),
             'stateString': formatters.getPlayerStateString(account.state),
             'icon': vContourIcon,
             'vShortName': vShortName,
             'vLevel': vLevel,
             'tags': list(user.getTags()) if user else [],
             'isPlayerSpeaking': bool(isPlayerSpeaking(account.dbID)),
             'clanAbbrev': account.clanAbbrev,
             'region': self.lobbyContext.getRegionCode(account.dbID),
             'igrType': account.igrType,
             'badge': account.getBadgeID(),
             'badgeImgStr': account.getBadgeImgStr()})

        if label is not None:
            label = text_styles.main(i18n.makeString(label, total=text_styles.stats(str(len(listData)))))
        result = {'listData': listData,
         'teamLabel': label}
        return result

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.CHANGE_SETTINGS:
            self.as_startCoolDownSettingS(event.coolDown)
        elif event.requestID is REQUEST_TYPE.SWAP_TEAMS:
            self.as_startCoolDownSwapButtonS(event.coolDown)
        elif event.requestID is REQUEST_TYPE.CHANGE_ARENA_VOIP:
            self.as_startCoolDownVoiceChatS(event.coolDown)
        elif event.requestID is REQUEST_TYPE.CHANGE_USER_STATUS:
            self.as_startCoolDownObserverS(event.coolDown)

    def __me_onUserActionReceived(self, _, user):
        dbID = user.getID()
        playerInfo = self.prbEntity.getPlayerInfoByDbID(dbID)
        if playerInfo is None:
            return
        else:
            roster = playerInfo.roster
            tags = list(user.getTags())
            if roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
                self.as_setPlayerTagsInTeam1S(dbID, tags)
            elif roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2:
                self.as_setPlayerTagsInTeam2S(dbID, tags)
            else:
                self.as_setPlayerTagsInOtherS(dbID, tags)
            return

    @process
    def _doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit=isExit))
