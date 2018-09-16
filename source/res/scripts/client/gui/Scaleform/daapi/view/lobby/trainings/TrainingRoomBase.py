# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/TrainingRoomBase.py
import BigWorld
import ArenaType
from adisp import process
from gui import SystemMessages, GUI_SETTINGS
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
from gui.prb_control.entities.training.legacy.ctx import SetPlayerObserverStateCtx, ChangeArenaVoipCtx
from gui.prb_control.items.prb_items import getPlayersComparator
from gui.prb_control.settings import PREBATTLE_ROSTER, PREBATTLE_SETTING_NAME
from gui.prb_control.settings import REQUEST_TYPE, CTRL_ENTITY_TYPE
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.sounds.ambients import LobbySubViewEnv
from helpers import int2roman, i18n
from messenger.ext import passCensor
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from prebattle_shared import decodeRoster

class TrainingRoomBase(LobbySubView, TrainingRoomBaseMeta, ILegacyListener):
    __sound_env__ = LobbySubViewEnv
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, _=None):
        super(TrainingRoomBase, self).__init__()

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
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__updateTrainingRoomBase, scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_setObserverS(entity.getPlayerInfo().getVehicle().isObserver)
        g_messengerEvents.users.onUserActionReceived += self.__me_onUserActionReceived

    def _dispose(self):
        self.stopPrbListening()
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__updateTrainingRoomBase, scope=EVENT_BUS_SCOPE.LOBBY)
        g_messengerEvents.users.onUserActionReceived -= self.__me_onUserActionReceived
        self.__closeWindows()
        super(TrainingRoomBase, self)._dispose()

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
        self.__closeWindows()
        self.__doStartTraining()

    @process
    def __updateTrainingRoomBase(self, event):
        settings = event.ctx.get('settings', None)
        if settings and settings.areSettingsChanged(self.prbEntity.getSettings()):
            settings.setWaitingID('prebattle/change_settings')
            result = yield self.prbDispatcher.sendPrbRequest(settings)
            if not result:
                self._showActionErrorMessage()
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

    def onTeamStatesReceived(self, entity, team1State, team2State):
        _, assigned = decodeRoster(entity.getRosterKey())
        if team1State.isInQueue() and team2State.isInQueue() and assigned:
            self.as_disableControlsS(True)
        elif assigned is False:
            self.as_enabledCloseButtonS(True)

    def closeTrainingRoom(self):
        self._doLeave(False)

    def _showActionErrorMessage(self):
        SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.TRAINING_ERROR_DOACTION), type=SystemMessages.SM_TYPE.Error)

    @process
    def changeTeam(self, accID, slot):
        roster = int(slot)
        if not slot:
            roster = self.prbEntity.getRosterKey(accID)
            if not roster & PREBATTLE_ROSTER.UNASSIGNED:
                roster |= PREBATTLE_ROSTER.UNASSIGNED
        result = yield self.prbDispatcher.sendPrbRequest(AssignLegacyCtx(accID, roster, waitingID='prebattle/assign'))
        if not result:
            self._showActionErrorMessage()

    @process
    def swapTeams(self):
        result = yield self.prbDispatcher.sendPrbRequest(SwapTeamsCtx(waitingID='prebattle/swap'))
        if not result:
            self._showActionErrorMessage()

    @process
    def selectObserver(self, isObserver):
        result = yield self.prbDispatcher.sendPrbRequest(SetPlayerObserverStateCtx(isObserver, True, waitingID='prebattle/change_user_status'))
        if not result:
            self.as_setObserverS(False)
            self._showActionErrorMessage()

    @process
    def selectCommonVoiceChat(self, index):
        result = yield self.prbDispatcher.sendPrbRequest(ChangeArenaVoipCtx(int(index), waitingID='prebattle/change_arena_voip'))
        if not result:
            settings = self.prbEntity.getSettings()
            self.as_setArenaVoipChannelsS(settings[PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS])
            self._showActionErrorMessage()

    def onSettingUpdated(self, entity, settingName, settingValue):
        if settingName == PREBATTLE_SETTING_NAME.ARENA_TYPE_ID:
            arenaType = ArenaType.g_cache.get(settingValue)
            self.as_updateMapS(settingValue, arenaType.maxPlayersInTeam * 2, arenaType.name, formatters.getTrainingRoomBaseTitle(arenaType), formatters.getArenaSubTypeString(settingValue), arenaType.description)
        elif settingName == PREBATTLE_SETTING_NAME.ROUND_LENGTH:
            self.as_updateTimeoutS(formatters.getRoundLenString(settingValue))
        elif settingName == PREBATTLE_SETTING_NAME.COMMENT:
            self.as_updateCommentS(settingValue)
        elif settingName == PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS:
            self.as_setArenaVoipChannelsS(settingValue)
        self._updateStartButton(entity)

    def onRostersChanged(self, entity, rosters, full):
        pass

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
        if roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
            self.as_setPlayerStateInTeam1S(accountInfo.dbID, stateString, vContourIcon, vShortName, vLevel, accountInfo.igrType)
        elif roster == PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2:
            self.as_setPlayerStateInTeam2S(accountInfo.dbID, stateString, vContourIcon, vShortName, vLevel, accountInfo.igrType)
        else:
            self.as_setPlayerStateInOtherS(accountInfo.dbID, stateString, vContourIcon, vShortName, vLevel, accountInfo.igrType)
        creator = self.__getCreatorFromRosters()
        if accountInfo.dbID == creator.dbID:
            self.__showSettings(entity)
        self._updateStartButton(entity)

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
            if creator:
                creatorFullName = creator.getFullName()
                creatorClan = creator.clanAbbrev
                creatorRegion = self.lobbyContext.getRegionCode(creator.dbID)
                creatorIgrType = creator.igrType
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
             'description': arenaType.description,
             'maxPlayersCount': arenaType.maxPlayersInTeam * 2,
             'roundLenString': formatters.getRoundLenString(settings['roundLength']),
             'comment': comment,
             'arenaVoipChannels': settings[PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS],
             'canChangeArenaVOIP': permissions.canChangeArenaVOIP(),
             'isObserverModeEnabled': self.__isObserverModeEnabled()})
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

    def _showRosters(self, entity, rosters):
        pass

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

    def __swapTeamsInMinimap(self, team):
        if VIEW_ALIAS.MINIMAP_LOBBY in self.components:
            self.components[VIEW_ALIAS.MINIMAP_LOBBY].swapTeams(team)

    def _makeAccountsData(self, accounts, label=None):
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
             'igrType': account.igrType})

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
