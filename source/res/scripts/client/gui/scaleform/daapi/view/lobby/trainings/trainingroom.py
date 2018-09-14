# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/TrainingRoom.py
import ArenaType
import BigWorld
from adisp import process
from gui import SystemMessages, GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.TrainingRoomMeta import TrainingRoomMeta
from gui.prb_control.context import prb_ctx
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.items.prb_items import getPlayersComparator
from gui.prb_control.prb_helpers import PrbListener
from gui.prb_control.settings import PREBATTLE_ROSTER, PREBATTLE_SETTING_NAME
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.settings import REQUEST_TYPE, CTRL_ENTITY_TYPE
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import int2roman, i18n
from messenger.ext import passCensor
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from prebattle_shared import decodeRoster
from gui.LobbyContext import g_lobbyContext
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import text_styles

class TrainingRoom(LobbySubView, TrainingRoomMeta, PrbListener):

    def __init__(self, _ = None):
        super(TrainingRoom, self).__init__()

    @storage_getter('users')
    def usersStorage(self):
        return None

    def _populate(self):
        super(TrainingRoom, self)._populate()
        functional = self.prbFunctional
        if functional and functional.getEntityType():
            self.__showSettings(functional)
            self.__showRosters(functional, functional.getRosters())
            self.__swapTeamsInMinimap(functional.getPlayerTeam())
        else:
            self.destroy()
            g_eventDispatcher.loadTrainingList()
            return
        self.startPrbListening()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__updateTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_setObserverS(functional.getPlayerInfo().getVehicle().isObserver)
        g_messengerEvents.users.onUserActionReceived += self.__me_onUserActionReceived

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
        if self.prbFunctional:
            return self.prbFunctional.getPermissions().canSendInvite()
        return False

    def canChangePlayerTeam(self):
        if self.prbFunctional:
            return self.prbFunctional.getPermissions().canChangePlayerTeam()
        return False

    def canChangeSetting(self):
        if self.prbFunctional:
            return self.prbFunctional.getPermissions().canChangeSetting()
        return False

    def canStartBattle(self):
        if self.prbFunctional:
            return self.prbFunctional.getPermissions().canStartBattle()
        return False

    def canAssignToTeam(self, team):
        if self.prbFunctional:
            return self.prbFunctional.getPermissions().canAssignToTeam(int(team))
        return False

    def canDestroyRoom(self):
        if self.prbFunctional:
            settings = self.prbFunctional.getSettings()
            playerName = BigWorld.player().name
            return settings[PREBATTLE_SETTING_NAME.CREATOR] == playerName and settings[PREBATTLE_SETTING_NAME.DESTROY_IF_CREATOR_OUT]
        return False

    def getPlayerTeam(self, accID):
        return self.prbFunctional.getPlayerTeam(accID)

    def showPrebattleInvitationsForm(self):
        self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ctx={'prbName': 'training',
         'ctrlType': CTRL_ENTITY_TYPE.PREBATTLE}), scope=EVENT_BUS_SCOPE.LOBBY)

    def startTraining(self):
        self.__closeWindows()
        self.__doStartTraining()

    @process
    def __updateTrainingRoom(self, event):
        settings = event.ctx.get('settings', None)
        if settings and settings.areSettingsChanged(self.prbFunctional.getSettings()):
            settings.setWaitingID('prebattle/change_settings')
            result = yield g_prbLoader.getDispatcher().sendPrbRequest(settings)
            if not result:
                self.__showActionErrorMessage()
        return

    @process
    def __doStartTraining(self):
        result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.SetTeamStateCtx(1, True))
        if result:
            result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.SetTeamStateCtx(2, True))
            if not result:
                yield self.prbDispatcher.sendPrbRequest(prb_ctx.SetTeamStateCtx(1, False))
        if not result:
            self.__showActionErrorMessage()
            self.as_disableControlsS(False)
            self.__updateStartButton(self.prbFunctional)

    def onTeamStatesReceived(self, functional, team1State, team2State):
        team, assigned = decodeRoster(functional.getRosterKey())
        if team1State.isInQueue() and team2State.isInQueue() and assigned:
            self.as_disableControlsS(True)
        elif assigned is False:
            self.as_enabledCloseButtonS(True)

    @process
    def closeTrainingRoom(self):
        result = yield self.prbDispatcher.leave(prb_ctx.LeavePrbCtx(waitingID='prebattle/leave', flags=FUNCTIONAL_FLAG.SWITCH))
        if not result:
            self.__showActionErrorMessage()

    def __showActionErrorMessage(self):
        SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.TRAINING_ERROR_DOACTION), type=SystemMessages.SM_TYPE.Error)

    @process
    def changeTeam(self, accID, slot):
        roster = int(slot)
        if not slot:
            roster = self.prbFunctional.getRosterKey(accID)
            if not roster & PREBATTLE_ROSTER.UNASSIGNED:
                roster |= PREBATTLE_ROSTER.UNASSIGNED
        result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.AssignPrbCtx(accID, roster, waitingID='prebattle/assign'))
        if not result:
            self.__showActionErrorMessage()

    @process
    def swapTeams(self):
        result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.SwapTeamsCtx(waitingID='prebattle/swap'))
        if not result:
            self.__showActionErrorMessage()

    @process
    def selectObserver(self, isObserver):
        result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.SetPlayerObserverStateCtx(isObserver, True, waitingID='prebattle/change_user_status'))
        if not result:
            self.as_setObserverS(False)
            self.__showActionErrorMessage()

    @process
    def selectCommonVoiceChat(self, index):
        result = yield self.prbDispatcher.sendPrbRequest(prb_ctx.ChangeArenaVoipCtx(index, waitingID='prebattle/change_arena_voip'))
        if not result:
            settings = self.prbFunctional.getSettings()
            self.as_setArenaVoipChannelsS(settings[PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS])
            self.__showActionErrorMessage()

    def onPrbFunctionalFinished(self):
        self.__closeWindows()

    def onSettingUpdated(self, functional, settingName, settingValue):
        if settingName == PREBATTLE_SETTING_NAME.ARENA_TYPE_ID:
            arenaType = ArenaType.g_cache.get(settingValue)
            self.as_updateMapS(settingValue, arenaType.maxPlayersInTeam * 2, arenaType.name, formatters.getTrainingRoomTitle(arenaType), formatters.getArenaSubTypeString(settingValue), arenaType.description)
        elif settingName == PREBATTLE_SETTING_NAME.ROUND_LENGTH:
            self.as_updateTimeoutS(formatters.getRoundLenString(settingValue))
        elif settingName == PREBATTLE_SETTING_NAME.COMMENT:
            self.as_updateCommentS(settingValue)
        elif settingName == PREBATTLE_SETTING_NAME.ARENA_VOIP_CHANNELS:
            self.as_setArenaVoipChannelsS(settingValue)
        self.__updateStartButton(functional)

    def onRostersChanged(self, functional, rosters, full):
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            self.as_setTeam1S(self.__makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1], MENU.TRAINING_INFO_TEAM1LABEL))
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
            self.as_setTeam2S(self.__makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2], MENU.TRAINING_INFO_TEAM2LABEL))
        if PREBATTLE_ROSTER.UNASSIGNED in rosters:
            self.as_setOtherS(self.__makeAccountsData(rosters[PREBATTLE_ROSTER.UNASSIGNED], MENU.TRAINING_INFO_OTHERLABEL))
        self.__updateStartButton(functional)

    def onPlayerStateChanged(self, functional, roster, accountInfo):
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
            self.__showSettings(functional)
        self.__updateStartButton(functional)

    def onPlayerTeamNumberChanged(self, functional, team):
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

    def __showSettings(self, functional):
        settings = functional.getSettings()
        if settings is None:
            return
        else:
            isCreator = functional.isCreator()
            permissions = functional.getPermissions()
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
                creatorRegion = g_lobbyContext.getRegionCode(creator.dbID)
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
        rosters = self.prbFunctional.getRosters()
        for key, roster in rosters.iteritems():
            for account in roster:
                if account.isCreator:
                    return account

        return None

    def __isObserverModeEnabled(self):
        minCount = self.prbFunctional.getSettings().getTeamLimits(1)['minCount']
        return GUI_SETTINGS.trainingObserverModeEnabled and minCount > 0

    def __showRosters(self, functional, rosters):
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]
        self.as_setTeam1S(self.__makeAccountsData(accounts, MENU.TRAINING_INFO_TEAM1LABEL))
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2]
        self.as_setTeam2S(self.__makeAccountsData(accounts, MENU.TRAINING_INFO_TEAM2LABEL))
        accounts = rosters[PREBATTLE_ROSTER.UNASSIGNED]
        self.as_setOtherS(self.__makeAccountsData(accounts, MENU.TRAINING_INFO_OTHERLABEL))
        self.__updateStartButton(functional)

    def __updateStartButton(self, functional):
        if functional.getPermissions().canStartBattle():
            isInRange, state = functional.getLimits().isTeamsValid()
            self.as_disableStartButtonS(not isInRange)
            if state == '' and isInRange:
                self.as_enabledCloseButtonS(True)
        else:
            self.as_disableStartButtonS(True)

    def __swapTeamsInMinimap(self, team):
        if VIEW_ALIAS.MINIMAP_LOBBY in self.components:
            self.components[VIEW_ALIAS.MINIMAP_LOBBY].swapTeams(team)

    def __makeAccountsData(self, accounts, label = None):
        listData = []
        isPlayerSpeaking = self.app.voiceChatManager.isPlayerSpeaking
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
             'region': g_lobbyContext.getRegionCode(account.dbID),
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
        playerInfo = self.prbFunctional.getPlayerInfoByDbID(dbID)
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
