# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/TrainingRoomBase.py
import BigWorld
import ArenaType
from adisp import process
from gui import SystemMessages, GUI_SETTINGS
from gui.Scaleform.daapi.view.lobby.lobby_vehicle_marker_view import LOBBY_TYPE
from gui.Scaleform.genConsts.BATTLE_TYPES import BATTLE_TYPES
from gui.Scaleform.settings import ICONS_SIZES
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.Scaleform.daapi.view.meta.TrainingRoomBaseMeta import TrainingRoomBaseMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.legacy.ctx import SetTeamStateCtx, AssignLegacyCtx, SwapTeamsCtx
from gui.prb_control.entities.base.legacy.listener import ILegacyListener
from gui.prb_control.entities.epic_battle_training.ctx import SetPlayerObserverStateCtx, ChangeArenaVoipCtx
from gui.prb_control.items.prb_items import getPlayersComparator
from gui.prb_control.settings import PREBATTLE_ROSTER, PREBATTLE_SETTING_NAME
from gui.prb_control.settings import REQUEST_TYPE, CTRL_ENTITY_TYPE
from gui.Scaleform.daapi.view.lobby.trainings.sound_constants import TRAININGS_SOUND_SPACE
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.sounds.ambients import LobbySubViewEnv
from helpers import int2roman, i18n
from gui.impl import backport
from messenger.ext import passCensor
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from prebattle_shared import decodeRoster
from skeletons.helpers.statistics import IStatisticsCollector
from helpers.statistics import HANGAR_LOADING_STATE
from constants import PREBATTLE_MAX_OBSERVERS_IN_TEAM, OBSERVERS_BONUS_TYPES, PREBATTLE_ERRORS, PREBATTLE_TYPE
from gui.shared.events import CoolDownEvent
BATTLE_TYPES_ICONS = {PREBATTLE_TYPE.TRAINING: BATTLE_TYPES.TRAINING,
 PREBATTLE_TYPE.EPIC_TRAINING: BATTLE_TYPES.EPIC_TRAINING}

class TrainingRoomBase(LobbySubView, TrainingRoomBaseMeta, ILegacyListener):
    __sound_env__ = LobbySubViewEnv
    _COMMON_SOUND_SPACE = TRAININGS_SOUND_SPACE
    lobbyContext = dependency.descriptor(ILobbyContext)
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, _=None):
        super(TrainingRoomBase, self).__init__()

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def showTrainingSettings(self):
        pass

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
            settings = self.prbEntity.getSettings()
            playerName = BigWorld.player().name
            return settings[PREBATTLE_SETTING_NAME.CREATOR] == playerName and settings[PREBATTLE_SETTING_NAME.DESTROY_IF_CREATOR_OUT]
        return False

    def getPlayerTeam(self, accID):
        return self.prbEntity.getPlayerTeam(accID)

    def showPrebattleInvitationsForm(self):
        self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ctx={'prbName': 'training',
         'ctrlType': CTRL_ENTITY_TYPE.LEGACY}), scope=EVENT_BUS_SCOPE.LOBBY)

    def startTraining(self):
        self._closeWindows()
        self.__doStartTraining()

    def onTeamStatesReceived(self, entity, team1State, team2State):
        _, assigned = decodeRoster(entity.getRosterKey())
        if team1State.isInQueue() and team2State.isInQueue() and assigned:
            self.as_disableControlsS(True)
        elif assigned is False:
            self.as_enabledCloseButtonS(True)

    def closeTrainingRoom(self):
        self._doLeave(False)

    def onSettingUpdated(self, entity, settingName, settingValue):
        if settingName in (PREBATTLE_SETTING_NAME.ARENA_TYPE_ID, PREBATTLE_SETTING_NAME.LIMITS):
            settings = entity.getSettings()
            if settingName == PREBATTLE_SETTING_NAME.ARENA_TYPE_ID:
                arenaTypeID = settingValue
            else:
                arenaTypeID = settings[PREBATTLE_SETTING_NAME.ARENA_TYPE_ID]
            arenaType = ArenaType.g_cache.get(arenaTypeID)
            self.as_updateMapS(arenaTypeID, arenaType.maxPlayersInTeam * 2, arenaType.name, formatters.getTrainingRoomTitle(arenaType), formatters.getArenaSubTypeString(arenaTypeID), arenaType.description, self.__battleTypeIcon(settings[PREBATTLE_SETTING_NAME.BATTLE_TYPE]))
        elif settingName == PREBATTLE_SETTING_NAME.ROUND_LENGTH:
            self.as_updateTimeoutS(formatters.getRoundLenString(settingValue))
        elif settingName == PREBATTLE_SETTING_NAME.COMMENT:
            self.as_updateCommentS(settingValue)
        elif settingName == PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS:
            self.as_setArenaVoipChannelsS(settingValue)
        self._updateStartButton(entity)

    def onRostersChanged(self, entity, rosters, full):
        self._updateStartButton(entity)

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
        badge = accountInfo.getBadge()
        badgeVO = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': False}) if badge else {}
        if roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
            self.as_setPlayerStateInTeam1S(accountInfo.dbID, stateString, vContourIcon, vShortName, vLevel, accountInfo.igrType, badgeVO)
        elif roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2:
            self.as_setPlayerStateInTeam2S(accountInfo.dbID, stateString, vContourIcon, vShortName, vLevel, accountInfo.igrType, badgeVO)
        else:
            self.as_setPlayerStateInOtherS(accountInfo.dbID, stateString, vContourIcon, vShortName, vLevel, accountInfo.igrType, badgeVO)
        creator = self.__getCreatorFromRosters()
        if accountInfo.dbID == creator.dbID:
            self.__showSettings(entity)
        self._updateStartButton(entity)

    def onPlayerTeamNumberChanged(self, entity, team):
        if VIEW_ALIAS.MINIMAP_LOBBY in self.components:
            self.components[VIEW_ALIAS.MINIMAP_LOBBY].swapTeams(team)

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
            self._showActionErrorMessage(ctx.getLastErrorString())

    @process
    def swapTeams(self):
        result = yield self.prbDispatcher.sendPrbRequest(SwapTeamsCtx(waitingID='prebattle/swap'))
        if not result:
            self._showActionErrorMessage()

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
                self.as_setObserverS(True)
                self._showActionErrorMessage(PREBATTLE_ERRORS.PLAYERS_LIMIT)
                return
        result = yield self.prbDispatcher.sendPrbRequest(SetPlayerObserverStateCtx(isObserver, True, waitingID='prebattle/change_user_status'))
        if not result:
            self.as_setObserverS(False)
            self._showActionErrorMessage()

    @process
    def selectCommonVoiceChat(self, index):
        result = yield self.prbDispatcher.sendPrbRequest(ChangeArenaVoipCtx(int(index), waitingID='prebattle/change_arena_voip'))
        if not result:
            prbSettings = self.prbEntity.getSettings()
            self.as_setArenaVoipChannelsS(prbSettings[PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS])
            self._showActionErrorMessage()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def _populate(self):
        super(TrainingRoomBase, self)._populate()
        entity = self.prbEntity
        if entity.getEntityType():
            self.__showSettings(entity)
            self._showRosters(entity, entity.getRosters())
            self.__swapTeamsInMinimap(entity.getPlayerTeam())
        self.startPrbListening()
        self._addListeners()
        self.as_setObserverS(entity.getPlayerInfo().getVehicle().isObserver)
        self._onPopulateEnd()
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.TRAINING_UI_READY, showSummaryNow=True)

    def _onPopulateEnd(self):
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, ctx={'lobbyType': LOBBY_TYPE.TRAINING_ROOM}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _addListeners(self):
        g_messengerEvents.users.onUserActionReceived += self.__me_onUserActionReceived
        self.addListener(events.CoolDownEvent.PREBATTLE, self._handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        g_messengerEvents.users.onUserActionReceived -= self.__me_onUserActionReceived
        self.removeListener(events.CoolDownEvent.PREBATTLE, self._handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.stopPrbListening()
        self._removeListeners()
        self._closeWindows()
        super(TrainingRoomBase, self)._dispose()

    def _handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.CHANGE_SETTINGS:
            self.as_startCoolDownSettingS(event.coolDown)
        elif event.requestID is REQUEST_TYPE.CHANGE_ARENA_VOIP:
            self.as_startCoolDownVoiceChatS(event.coolDown)
        elif event.requestID is REQUEST_TYPE.CHANGE_USER_STATUS:
            self.as_startCoolDownObserverS(event.coolDown)

    def _showRosters(self, entity, rosters):
        self._updateStartButton(entity)

    def _updateStartButton(self, entity):
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

    def _closeWindows(self):
        pass

    def _closeWindow(self, windowAlias):
        window = self.app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: windowAlias})
        if window is not None:
            window.destroy()
        return

    def _makeAccountsData(self, accounts, rLabel=None):
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
            badge = account.getBadge()
            badgeVO = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': False}) if badge else {}
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
             'badgeVisualVO': badgeVO})

        label = ''
        if rLabel is not None:
            label = text_styles.main(backport.text(rLabel, total=text_styles.stats(str(len(listData)))))
        result = {'listData': listData,
         'teamLabel': label}
        return result

    def _showActionErrorMessage(self, errType=None):
        errors = {PREBATTLE_ERRORS.ROSTER_LIMIT: (SYSTEM_MESSAGES.TRAINING_ERROR_ADDPLAYER, {}),
         PREBATTLE_ERRORS.PLAYERS_LIMIT: (SYSTEM_MESSAGES.TRAINING_ERROR_SELECTOBSERVER, {'numPlayers': self.__getPlayersMaxCount()})}
        errMsg = errors.get(errType, (SYSTEM_MESSAGES.TRAINING_ERROR_DOACTION, {}))
        SystemMessages.pushMessage(i18n.makeString(errMsg[0], **errMsg[1]), type=SystemMessages.SM_TYPE.Error)

    def _isObserverModeEnabled(self):
        minCount = self.prbEntity.getSettings().getTeamLimits(1)['minCount']
        return GUI_SETTINGS.trainingObserverModeEnabled and minCount > 0

    def _updateTrainingRoom(self, event):
        self.__changeTrainingRoomSettings(event.ctx.get('settings', None))
        return

    @process
    def _doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit=isExit))

    @process
    def __changeTrainingRoomSettings(self, settings):
        if settings and settings.areSettingsChanged(self.prbEntity.getSettings()):
            settings.setWaitingID('prebattle/change_settings')
            result = yield self.prbDispatcher.sendPrbRequest(settings)
            if not result:
                self._showActionErrorMessage()

    def __getPlayersMaxCount(self):
        playersMaxCount = self.prbEntity.getTeamLimits()['maxCount'][0]
        if self.prbEntity.getSettings()['bonusType'] in OBSERVERS_BONUS_TYPES:
            playersMaxCount -= PREBATTLE_MAX_OBSERVERS_IN_TEAM
        return playersMaxCount

    def __showSettings(self, entity):
        settings = entity.getSettings()
        if settings is None:
            return
        else:
            isCreator = entity.isCommander()
            permissions = entity.getPermissions()
            arenaTypeID = settings['arenaTypeID']
            arenaType = ArenaType.g_cache.get(arenaTypeID)
            if isCreator:
                comment = settings['comment']
            else:
                comment = passCensor(settings['comment'])
            creatorFullName, creatorClan, creatorRegion, creatorIgrType = (None, None, None, 0)
            creator = self.__getCreatorFromRosters()
            badgeVO = {}
            if creator:
                creatorFullName = creator.getFullName()
                creatorClan = creator.clanAbbrev
                creatorRegion = self.lobbyContext.getRegionCode(creator.dbID)
                creatorIgrType = creator.igrType
                badge = creator.getBadge()
                badgeVO = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': False}) if badge else {}
            self.as_setInfoS({'isCreator': isCreator,
             'creator': settings[PREBATTLE_SETTING_NAME.CREATOR],
             'creatorFullName': creatorFullName,
             'creatorClan': creatorClan,
             'creatorRegion': creatorRegion,
             'creatorIgrType': creatorIgrType,
             'title': formatters.getTrainingRoomTitle(arenaType),
             'arenaName': arenaType.name,
             'arenaTypeID': arenaTypeID,
             'arenaSubType': formatters.getArenaSubTypeString(arenaTypeID),
             'battleTypeIco': self.__battleTypeIcon(settings[PREBATTLE_SETTING_NAME.BATTLE_TYPE]),
             'description': arenaType.description,
             'maxPlayersCount': arenaType.maxPlayersInTeam * 2,
             'roundLenString': formatters.getRoundLenString(settings['roundLength']),
             'comment': comment,
             'arenaVoipChannels': settings[PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS],
             'canChangeArenaVOIP': permissions.canChangeArenaVOIP(),
             'isObserverModeEnabled': self._isObserverModeEnabled(),
             'badgeVisualVO': badgeVO})
            return

    def __getCreatorFromRosters(self):
        rosters = self.prbEntity.getRosters()
        for _, roster in rosters.iteritems():
            for account in roster:
                if account.isCreator:
                    return account

        return None

    def __battleTypeIcon(self, prebattleType):
        return BATTLE_TYPES_ICONS.get(prebattleType, BATTLE_TYPES.TRAINING)

    def __swapTeamsInMinimap(self, team):
        if VIEW_ALIAS.MINIMAP_LOBBY in self.components:
            self.components[VIEW_ALIAS.MINIMAP_LOBBY].swapTeams(team)

    def __me_onUserActionReceived(self, _, user, shadowMode):
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
    def __doStartTraining(self):
        result = yield self.prbDispatcher.sendPrbRequest(SetTeamStateCtx(1, True))
        if result:
            result = yield self.prbDispatcher.sendPrbRequest(SetTeamStateCtx(2, True))
            if not result:
                yield self.prbDispatcher.sendPrbRequest(SetTeamStateCtx(1, False))
        if not result:
            self._showActionErrorMessage()
            self.as_disableControlsS(False)
            self._updateStartButton(self.prbEntity)
