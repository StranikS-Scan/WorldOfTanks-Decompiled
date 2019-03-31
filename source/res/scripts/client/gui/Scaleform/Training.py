# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Training.py
# Compiled at: 2018-11-29 14:33:44
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers.AccountPrebattle import AccountPrebattle
from adisp import process
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform import VoiceChatInterface
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.utils.functions import getArenaSubTypeName
from gui.Scaleform.utils.gui_items import Vehicle
from gui.Scaleform.windows import UIInterface
from helpers import int2roman
from helpers.i18n import makeString
from messenger import passCensor
from messenger.gui import MessengerDispatcher
from messenger.gui.Scalefrom.search_interfaces import PrebattleSearchUsersInterface
from messenger.gui.Scalefrom.users_interfaces import PrebattleUsersRosterInterface
import ArenaType
import BigWorld
import MusicController
import constants
from MinimapLobby import MinimapLobby
_ICONS_MASK = '../maps/icons/map/%(subtype)s%(unicName)s.tga'
_UPDATE_LIST_TIMEOUT = 5
_ROOM_LIFETIME = 60 * 60

class Training(UIInterface):

    def __init__(self):
        UIInterface.__init__(self)
        self.__searchUsers = PrebattleSearchUsersInterface(prefix='Prebattle.Training.SearchUsers')
        self.__contacts = PrebattleUsersRosterInterface(prefix='Prebattle.Training')
        self.__roomsList = TrainingRooms()
        self.__createRoom = CreateTrainingRoom()
        self.__roomInfo = TrainingRoom()
        self.__selectedRoom = None
        return

    def __del__(self):
        LOG_DEBUG('TrainingHandler deleted')

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.__searchUsers.populateUI(proxy)
        self.__contacts.populateUI(proxy)
        self.__roomsList.populateUI(proxy)
        self.__roomInfo.populateUI(proxy)
        self.__createRoom.populateUI(proxy)
        g_playerEvents.onPrebattleJoined += self.__onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure += self.__joinPrebattleError
        g_playerEvents.onPrebattleLeft += self.__onKickedFromRoom
        g_playerEvents.onKickedFromPrebattle += self.__onKickedFromRoom
        g_playerEvents.onArenaCreated += self.__startArena
        g_playerEvents.onArenaJoinFailure += self.__joinArenaError
        g_playerEvents.onKickedFromArena += self.__kickArenaError
        forseClose = True
        if AccountPrebattle.isTraining():
            forseClose = False
            self.__onRoomJoin()
        else:
            self.__roomsList.show()
        self.uiHolder.movie.backgroundAlpha = 0.0
        self.uiHolder.movie.wg_inputKeyMode = 1
        self.uiHolder.addExternalCallbacks({'training.join': self.__joinRoom,
         'training.start': self.__startRoom,
         'training.close': self.__closeRoom})
        if not self.uiHolder.commandsBinded:
            self.uiHolder.bindCommands()
        self.uiHolder.updateAccountInfo()
        Waiting.hide('loadPage')
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)

    def dispossessUI(self):
        self.__searchUsers.dispossessUI()
        self.__contacts.dispossessUI()
        self.__roomsList.dispossessUI()
        self.__createRoom.dispossessUI()
        self.__roomInfo.dispossessUI()
        self.uiHolder.removeExternalCallbacks('training.join', 'training.start', 'training.close')
        UIInterface.dispossessUI(self)
        g_playerEvents.onPrebattleJoined -= self.__onPrebattleJoined
        g_playerEvents.onPrebattleJoinFailure -= self.__joinPrebattleError
        g_playerEvents.onPrebattleLeft -= self.__onKickedFromRoom
        g_playerEvents.onKickedFromPrebattle -= self.__onKickedFromRoom
        g_playerEvents.onArenaCreated -= self.__startArena
        g_playerEvents.onArenaJoinFailure -= self.__joinArenaError
        g_playerEvents.onKickedFromArena -= self.__kickArenaError
        self.__suspend()

    def __joinRoom(self, callbackId, roomId):
        """
        Join to room with current vehicle
        """
        if self.__selectedRoom != roomId:

            def joinFunc():
                Waiting.show('trainingJoin')
                BigWorld.player().prb_join(roomId)

            if self.uiHolder.captcha.isCaptchaRequired():
                self.uiHolder.captcha.showCaptcha(joinFunc)
            else:
                joinFunc()
            self.__selectedRoom = roomId

    def __startRoom(self, callbackId):
        """
        Start room
        """
        if self.uiHolder.captcha.isCaptchaRequired():
            self.uiHolder.captcha.showCaptcha(self.__setTeamReady)
        else:
            self.__setTeamReady()

    def __setTeamReady(self):
        BigWorld.player().prb_teamReady(1, True, lambda code: None)
        BigWorld.player().prb_teamReady(2, True, lambda code: None)
        self.call('training.disableStart', [True])

    def __startArena(self):
        pass

    def __kickArenaError(self, code):
        self.__errorArena(code, 'kick')

    def __joinPrebattleError(self, code):
        Waiting.hide('trainingCreateMap')
        Waiting.hide('trainingJoin')

    def __joinArenaError(self, code, errorStr=''):
        Waiting.hide('trainingCreateMap')
        Waiting.hide('trainingJoin')
        self.__errorArena(code, 'join')

    def __errorArena(self, errorCode, messageType):
        self.__onKickedFromRoom()
        error = constants.JOIN_FAILURE_NAMES[errorCode] if messageType == 'join' else constants.KICK_REASON_NAMES[errorCode]
        message = '#system_messages:arena_start_errors/%s/%s' % (messageType, error)
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Error)

    def __closeRoom(self, callbackId):
        """
        Exit from room. If player is owner close room.
        """
        BigWorld.player().prb_leave(lambda *args: None)
        self.__selectedRoom = None
        return

    def __onPrebattleJoined(self):
        BigWorld.player().prebattle.onSettingsReceived += self.__onPrebattleSettingsReceived
        BigWorld.player().prebattle.onRosterReceived += self.__onPrebattleRosterReceived

    def __onPrebattleSettingsReceived(self):
        BigWorld.player().prebattle.onSettingsReceived -= self.__onPrebattleSettingsReceived
        if AccountPrebattle.isTraining():
            self.__onRoomJoin()

    def __onPrebattleRosterReceived(self):
        BigWorld.player().prebattle.onRosterReceived -= self.__onPrebattleRosterReceived
        if AccountPrebattle.isTraining():
            self.__onRoomJoin()

    def __onRoomJoin(self):
        if AccountPrebattle.get().settings and AccountPrebattle.get().rosters:
            if not AccountPrebattle.isTraining():
                self.uiHolder.movie.invoke(('loadHangar',))
                return
            if not AccountPrebattle.isMemberReady():
                if not g_currentVehicle.isReadyToFight():
                    message = '#system_messages:arena_start_errors/join/no_readyVehicle'
                    SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Error)
                    self.uiHolder.movie.invoke(('loadHangar',))
                    return
                if self.uiHolder.captcha.isCaptchaRequired():
                    self.uiHolder.captcha.showCaptcha(lambda : BigWorld.player().prb_ready(g_currentVehicle.vehicle.inventoryId, self.__onReady))
                else:
                    BigWorld.player().prb_ready(g_currentVehicle.vehicle.inventoryId, self.__onReady)
                return
            self.__onReady()

    def __onReady(self, code=None):
        self.__roomsList.hide()
        self.__createRoom.hide()
        Waiting.hide('trainingCreateMap')
        Waiting.hide('trainingJoin')
        self.__roomInfo.show()
        self.__selectedRoom = None
        return

    def __onKickedFromRoom(self, *args):
        """
        Player was kicked from room or leave it themself.
        """
        self.__selectedRoom = None
        self.__roomsList.show()
        self.__roomInfo.hide()
        return

    def __suspend(self):
        if AccountPrebattle.isTraining():
            BigWorld.player().prb_notReady(constants.PREBATTLE_ACCOUNT_STATE.NOT_READY, lambda code: None)


class TrainingRooms(UIInterface):

    def __init__(self):
        self.__callbackId = None
        UIInterface.__init__(self)
        return

    def __del__(self):
        LOG_DEBUG('TrainingRoomsHandler deleted')

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        g_playerEvents.onPrebattlesListReceived += self.__update

    def dispossessUI(self):
        g_playerEvents.onPrebattlesListReceived -= self.__update
        self.hide()
        UIInterface.dispossessUI(self)

    def show(self):
        self.uiHolder.call('training.showList', [])
        self.__request()

    def hide(self):
        self.__stopRequest()

    def __stopRequest(self):
        if self.__callbackId:
            BigWorld.cancelCallback(self.__callbackId)
            self.__callbackId = None
        return

    def __request(self):
        """
        Trainings list requests from server
        """
        if hasattr(BigWorld.player(), 'requestPrebattles'):
            self.__callbackId = BigWorld.callback(_UPDATE_LIST_TIMEOUT, self.__request)
            BigWorld.player().requestPrebattles(constants.PREBATTLE_TYPE.TRAINING, constants.PREBATTLE_CACHE_KEY.CREATE_TIME, False, 0, 50)

    def __update(self, type, count, trainings):
        """
        Populate list of rooms recived from server
        If player was suspended and room exists autojoin to room
        Owner always autojoin ot room (check by name)
        """
        if type == constants.PREBATTLE_TYPE.TRAINING:
            list = []
            for time, id, info in trainings:
                list.append(id)
                list.append(passCensor(info.get(constants.PREBATTLE_CACHE_KEY.COMMENT, '')))
                list.append(info[constants.PREBATTLE_CACHE_KEY.ROUND_LENGTH] / 60)
                arena = ArenaType.g_cache.get(info[constants.PREBATTLE_CACHE_KEY.ARENA_TYPE_ID])
                list.append(arena.name)
                list.append(info[constants.PREBATTLE_CACHE_KEY.PLAYER_COUNT])
                list.append(arena.maxPlayersInTeam)
                clan = info.get(constants.PREBATTLE_CACHE_KEY.CREATOR_CLAN_ABBREV, '')
                creator = info.get(constants.PREBATTLE_CACHE_KEY.CREATOR, '')
                if clan:
                    creator += '[%s]' % clan
                list.append(creator)
                list.append(_ICONS_MASK % {'subtype': 'small/',
                 'unicName': arena.typeName})
                list.append(not info[constants.PREBATTLE_CACHE_KEY.IS_OPENED])

            self.uiHolder.call('training.updateList', list)


class TrainingRoom(UIInterface):

    def __init__(self):
        self.__trainingInfo = {}
        self.minimap = None
        UIInterface.__init__(self)
        return

    def __del__(self):
        LOG_DEBUG('TrainingRoomHandler deleted')

    @property
    def prebattle(self):
        if hasattr(BigWorld.player(), 'prebattle'):
            return BigWorld.player().prebattle
        else:
            return None

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'training.populateInfo': self.__updateInfo,
         'training.populateSettings': self.__updateSettings,
         'training.changeTeam': self.__changeTeam,
         'training.selectUseCommonVoiceChat': self.__selectUseCommonVoiceChat,
         'Prebattle.Training.Invitations.Send': self.__sendInvitation,
         'Prebattle.Training.Invitations.ShowError': self.__showInvitationError})
        self.minimap = MinimapLobby(proxy)
        self.minimap.start()
        MessengerDispatcher.g_instance.users.onUsersRosterUpdate += self.onUsersRosterUpdated
        MessengerDispatcher.g_instance.users.onUsersRosterReceived += self.__updatePlayersList

    def dispossessUI(self):
        MessengerDispatcher.g_instance.users.onUsersRosterReceived -= self.__updatePlayersList
        MessengerDispatcher.g_instance.users.onUsersRosterUpdate -= self.onUsersRosterUpdated
        self.minimap.destroy()
        self.minimap = None
        self.uiHolder.removeExternalCallbacks('training.populateInfo', 'training.populateSettings', 'training.changeTeam', 'training.selectUseCommonVoiceChat', 'Prebattle.Training.Invitations.Send', 'Prebattle.Training.Invitations.ShowError')
        self.hide()
        UIInterface.dispossessUI(self)
        return

    def onUsersRosterUpdated(self, action, user):
        self.__updatePlayersList()

    def show(self):
        if self.prebattle:
            self.prebattle.onSettingsReceived += self.__reciveSettingsInfo
            self.prebattle.onSettingUpdated += self.__reciveSettingsInfo
            self.prebattle.onRosterReceived += self.__recivePlayersList
            self.prebattle.onPlayerAdded += self.__recivePlayersList
            self.prebattle.onPlayerRemoved += self.__recivePlayersList
            self.prebattle.onPlayerStateChanged += self.__recivePlayersList
            self.prebattle.onPlayerRosterChanged += self.__recivePlayersList
            if self.prebattle.settings and self.uiHolder:
                self.__reciveInfo()

    def hide(self):
        if self.uiHolder is not None:
            self.uiHolder.call('Prebattle.Training.Invitations.CloseWindow')
        self.__trainingInfo = {}
        if self.prebattle:
            self.prebattle.onSettingsReceived -= self.__reciveSettingsInfo
            self.prebattle.onSettingUpdated -= self.__reciveSettingsInfo
            self.prebattle.onRosterReceived -= self.__recivePlayersList
            self.prebattle.onPlayerAdded -= self.__recivePlayersList
            self.prebattle.onPlayerRemoved -= self.__recivePlayersList
            self.prebattle.onPlayerStateChanged -= self.__recivePlayersList
            self.prebattle.onPlayerRosterChanged -= self.__recivePlayersList
        return

    def __reciveSettingsInfo(self, itemName=None):
        if self.uiHolder:
            self.__reciveInfo()

    def __reciveInfo(self):
        s = self.prebattle.settings
        isCreator = False
        if s['creator'] == BigWorld.player().name:
            self.uiHolder.call('training.showOwnerInfo', [])
            isCreator = True
        else:
            self.uiHolder.call('training.showInfo', [])
        arena = ArenaType.g_cache.get(s['arenaTypeID'])
        self.__trainingInfo.update({'owner': s['creator'],
         'arena': arena.name,
         'defaultTeam': s['defaultRoster'],
         'description': arena.description,
         'arenaId': s['arenaTypeID'],
         'maxPlayers': arena.maxPlayersInTeam,
         'roundLength': s['roundLength'] / 60,
         'privacy': not s['isOpened'],
         'comment': s['comment'] if isCreator else passCensor(s['comment']),
         'arenaIcon': _ICONS_MASK % {'subtype': '',
                       'unicName': ArenaType.g_list[s['arenaTypeID']]},
         'minPlayersInTeam': arena.minPlayersInTeam})
        accInfo = AccountPrebattle.getMember(BigWorld.player().id)
        if s is not None and accInfo is not None:
            useArenaVoip = s.get('arenaVoipChannels', 0)
            roles = s.get('roles', {}).get(accInfo.get('dbID', -1), 0)
            canChangeArenaVOIP = roles & constants.PREBATTLE_ROLE.CHANGE_ARENA_VOIP != 0
            self.__trainingInfo.update({'useArenaVoip': useArenaVoip,
             'canChangeArenaVOIP': canChangeArenaVOIP})
        self.__updateInfo()
        return

    def __updateInfo(self, callBackId=None):
        data = list()
        data.append(self.__trainingInfo.get('comment', ''))
        data.append(self.__trainingInfo.get('roundLength', ''))
        data.append(self.__trainingInfo.get('maxPlayers', ''))
        data.append(self.__trainingInfo.get('arena', ''))
        data.append(self.__trainingInfo.get('owner', ''))
        data.append(self.__trainingInfo.get('arenaId', ''))
        data.append(bool(self.__trainingInfo.get('privacy', 0)))
        data.append(self.__trainingInfo.get('description', ''))
        data.append(self.__trainingInfo.get('canChangeArenaVOIP', False))
        data.append(self.__trainingInfo.get('useArenaVoip', 0))
        self.uiHolder.call('training.updateInfo', data)
        if callBackId:
            self.__updatePlayersList()

    def __updateSettings(self, callbackId):
        if self.__trainingInfo:
            data = list()
            data.append(self.__trainingInfo.get('comment', ''))
            data.append(self.__trainingInfo.get('roundLength', ''))
            data.append(self.__trainingInfo.get('arenaId', ''))
            data.append(self.__trainingInfo.get('privacy', 0))
            self.uiHolder.call('training.updateSettings', data)

    def __recivePlayersList(self, *args):
        if self.uiHolder:
            self.__updatePlayersList()

    def __updatePlayersList(self):
        activeUsers = [0, 0, 0]
        hasInBattle = False
        data = [BigWorld.player().id]
        groups = [{}, {}, {}]
        groups[0].update(self.prebattle.rosters.get(17, {}))
        groups[0].update(self.prebattle.rosters.get(18, {}))
        groups[1].update(self.prebattle.rosters.get(1, {}))
        groups[2].update(self.prebattle.rosters.get(2, {}))
        for groupId, roster in enumerate(groups):
            data.append(len(roster))
            for id, player in roster.items():
                data.append(id)
                data.append(player['dbID'])
                data.append(player['name'])
                if player['clanAbbrev']:
                    data.append(player['name'] + '[%s]' % player['clanAbbrev'])
                else:
                    data.append(player['name'])
                if player['state'] in (constants.PREBATTLE_ACCOUNT_STATE.READY, constants.PREBATTLE_ACCOUNT_STATE.IN_BATTLE):
                    vehicle = Vehicle(player['vehCompDescr'])
                    data.append(vehicle.iconContour)
                    data.append(vehicle.shortName)
                    data.append(int2roman(vehicle.level))
                else:
                    data.append('')
                    data.append('')
                    data.append('')
                data.append(player['state'])
                user = MessengerDispatcher.g_instance.users.getUser(player['dbID'], player['name'])
                data.append(user.roster if user is not None else 0)
                data.append(VoiceChatInterface.g_instance.isPlayerSpeaking(player['dbID']))
                if player['state'] == constants.PREBATTLE_ACCOUNT_STATE.READY:
                    activeUsers[groupId] = +1
                elif player['state'] == constants.PREBATTLE_ACCOUNT_STATE.IN_BATTLE:
                    hasInBattle = True

        self.uiHolder.call('training.updateInfoList', data)
        if hasInBattle:
            self.uiHolder.call('training.disableStart', [True])
        else:
            minPlayers = self.__trainingInfo.get('minPlayersInTeam', 1)
            activeUsers.pop(0)
            minActive = min(activeUsers)
            self.uiHolder.call('training.disableStart', [minActive < minPlayers])
        return

    def __changeTeam(self, callBackId, id, team):

        def logTeamChange(code):
            if code < 0:
                LOG_ERROR('Server return error for training_assignToTeam request: responseCode=%s' % code)
            Waiting.hide('trainingAssigning')

        if id is None or not hasattr(BigWorld.player(), 'prb_assign'):
            return
        else:
            Waiting.show('trainingAssigning')
            if team == 0:
                team = self.__trainingInfo.get('defaultTeam', 17)
            BigWorld.player().prb_assign(id, team, logTeamChange)
            return

    def __selectUseCommonVoiceChat(self, responseId, selected):
        respondArgs = [responseId, 5.0]
        if self.__trainingInfo.get('useArenaVoip', 0) != selected:
            BigWorld.player().prb_changeArenaVoip(int(selected), lambda resultID: self.__onChangeArenaVoip(selected, resultID))
        self.uiHolder.respond(respondArgs)

    def __onChangeArenaVoip(self, useArenaVoip, resultID):
        if resultID < 0:
            LOG_ERROR('Server return error for prb_changeUseArenaVoip request:resultID=%s' % resultID)
            self.uiHolder.call('training.changeUseArenaVoipFailed', [self.__trainingInfo.get('useArenaVoip', 0)])

    def __sendInvitation(self, responseId, *args):
        prebattleID = BigWorld.player().prebattle.id
        if AccountPrebattle.isCreator() and prebattleID:
            invitesManager = MessengerDispatcher.g_instance.invites
            invitesManager.sendInvites(list(args[1:]), args[0])
            self.uiHolder.respond([responseId, constants.REQUEST_COOLDOWN.PREBATTLE_INVITES])
        else:
            LOG_WARNING('Can not send invites: isCreator = %r, prebattleRoomId = %d' % (AccountPrebattle.isCreator(), prebattleID))

    def __showInvitationError(self, _, message):
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Error)


class CreateTrainingRoom(UIInterface):

    def __init__(self):
        UIInterface.__init__(self)
        self.minimap = None
        self.arenasCache = None
        return

    def __del__(self):
        LOG_DEBUG('CreateTrainingRoomHandler deleted')

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'training.populateMaps': self.__populateMaps,
         'training.create': self.__create,
         'training.updateSettings': self.__update,
         'training.updateMap': self.__updateMap})
        self.minimap = MinimapLobby(proxy)
        self.minimap.start()

    def dispossessUI(self):
        self.minimap.destroy()
        self.minimap = None
        self.uiHolder.removeExternalCallbacks('training.populateMaps', 'training.create', 'training.updateSettings', 'training.updateMap')
        UIInterface.dispossessUI(self)
        return

    def __create(self, callbackId, arena, roundLength, isPrivate, comment):
        """
        Try to create training room
        """

        def createFunc():
            Waiting.show('trainingCreateMap')
            BigWorld.player().prb_createTraining(arena, roundLength * 60, not isPrivate, comment)

        if self.uiHolder.captcha.isCaptchaRequired():
            self.uiHolder.captcha.showCaptcha(createFunc)
        else:
            createFunc()

    def hide(self):
        self.uiHolder.call('training.closeCreate', [])

    def __update(self, callbackId, arena, roundLength, isPrivate, comment):
        """
        Change training room info
        """

        def logChangeError(code, type):
            if code < 0:
                LOG_ERROR('Server return error for training change %s request: responseCode=%s' % (type, code))

        BigWorld.player().prb_changeRoundLength(roundLength * 60, lambda code: logChangeError(code, 'settings'))
        BigWorld.player().prb_changeOpenStatus(not isPrivate, lambda code: logChangeError(code, 'isOpen'))
        BigWorld.player().prb_changeComment(comment, lambda code: logChangeError(code, 'comment'))
        BigWorld.player().prb_changeArena(arena, lambda code: logChangeError(code, 'arena'))
        self.uiHolder.call('training.coolDownSetting', [5])

    def __updateMap(self, callbackId, arenaTypeID):
        self.minimap.setArena(arenaTypeID)

    def __populateMaps(self, callbackId):
        """
        Arena properties window call this to populate maps list
        """
        maps = [callbackId]
        if self.arenasCache is None:
            self.buildCache()
        for arena in self.arenasCache:
            maps.extend(arena)

        self.uiHolder.respond(maps)
        return

    def buildCache(self):

        def areanaComparator(x, y):
            return cmp(x[0].lower(), y[0].lower())

        arenaCache = ArenaType.g_cache
        self.arenasCache = []
        for arenaTypeID, arenaTypeName in ArenaType.g_list.iteritems():
            arenaType = arenaCache.get(arenaTypeID)
            for arenaTypeID in arenaType.subtypeIDs:
                subTypeName = getArenaSubTypeName(arenaTypeID)
                nameSuffix = '' if subTypeName == ArenaType._GAMEPLAY_TYPE_TO_NAME[constants.ARENA_GAMEPLAY_TYPE.STANDARD] else ' - ' + makeString('#arenas:type/%s/name' % subTypeName)
                self.arenasCache.append((arenaType.name + nameSuffix,
                 arenaTypeID,
                 arenaType.maxPlayersInTeam,
                 arenaType.roundLength / 60,
                 '',
                 _ICONS_MASK % {'subtype': '',
                  'unicName': arenaTypeName}))

        self.arenasCache = sorted(self.arenasCache, cmp=areanaComparator)
