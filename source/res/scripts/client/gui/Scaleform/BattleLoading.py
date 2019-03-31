# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/BattleLoading.py
# Compiled at: 2019-03-27 03:52:54
import BigWorld, constants, ArenaType
from helpers.tips import getTip
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.Waiting import Waiting
from account_helpers.AccountPrebattle import AccountPrebattle
from messenger.gui import MessengerDispatcher
from gui.Scaleform.utils.functions import getBattleSubTypeWinText, getArenaSubTypeName
from helpers.i18n import makeString
from gui.Scaleform import ColorSchemeManager
from gui.Scaleform import VehicleActions, VoiceChatInterface
_MAP_BG_SOURCE = '../maps/icons/map/screen/%s.dds'
_CONTOUR_ICONS_MASK = '../maps/icons/vehicle/contour/%(unicName)s.tga'

class BattleLoading(UIInterface):

    def __init__(self):
        self.onLoaded = None
        self.callbackId = None
        self.__arena = getattr(BigWorld.player(), 'arena', None)
        self.__progress = 0
        self.__winTextInit = False
        UIInterface.__init__(self)
        return

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        if self.__arena:
            self.__arena.onNewVehicleListReceived += self.__updatePlayers
            self.__arena.onNewStatisticsReceived += self.__updatePlayers
            self.__arena.onVehicleAdded += self.__updatePlayers
            self.__arena.onVehicleStatisticsUpdate += self.__updatePlayers
            self.__arena.onVehicleKilled += self.__updatePlayers
            self.__arena.onAvatarReady += self.__updatePlayers
            self.__arena.onVehicleUpdated += self.__updatePlayers
            MessengerDispatcher.g_instance.users.onUsersRosterReceived += self.__updatePlayers
        self.uiHolder.addExternalCallbacks({'loading.getData': self.__populateData})
        self.colorManager = ColorSchemeManager._ColorSchemeManager()
        self.colorManager.populateUI(proxy)
        self.uiHolder.movie.backgroundAlpha = 1.0
        self.__populateData()
        self.isSpaceLoaded()
        Waiting.hide('loadPage')
        Waiting.close()

    def dispossessUI(self):
        if self.callbackId is not None:
            BigWorld.cancelCallback(self.callbackId)
            self.callbackId = None
        if self.__arena:
            self.__arena.onNewVehicleListReceived -= self.__updatePlayers
            self.__arena.onNewStatisticsReceived -= self.__updatePlayers
            self.__arena.onVehicleAdded -= self.__updatePlayers
            self.__arena.onVehicleStatisticsUpdate -= self.__updatePlayers
            self.__arena.onVehicleKilled -= self.__updatePlayers
            self.__arena.onAvatarReady -= self.__updatePlayers
            self.__arena.onVehicleUpdated -= self.__updatePlayers
            MessengerDispatcher.g_instance.users.onUsersRosterReceived -= self.__updatePlayers
        if self.colorManager:
            self.colorManager.dispossessUI()
        self.uiHolder.removeExternalCallbacks('loading.getData')
        self.__arena = None
        UIInterface.dispossessUI(self)
        return

    def isSpaceLoaded(self):
        self.callbackId = None
        status = BigWorld.spaceLoadStatus()
        if status > self.__progress:
            self.__progress = status
            self.__setProgress(status)
        if status < 1.0:
            self.callbackId = BigWorld.callback(0.5, self.isSpaceLoaded)
            BigWorld.SetDrawInflux(False)
            return
        else:
            BigWorld.SetDrawInflux(True)
            BigWorld.player().onSpaceLoaded()
            self.isLoaded()
            return

    def isLoaded(self):
        self.callbackId = None
        if not BigWorld.worldDrawEnabled():
            self.callbackId = BigWorld.callback(0.5, self.isLoaded)
            return
        else:
            from gui.WindowsManager import g_windowsManager
            BigWorld.callback(0.1, g_windowsManager.showBattle)
            return

    def __setProgress(self, value):
        self.call('loading.setProgress', [value])

    def __populateData(self, callbackID=None):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena:
            self.call('loading.setMap', [arena.typeDescriptor.name])
            self.call('loading.setMapBG', [_MAP_BG_SOURCE % arena.typeDescriptor.typeName])
            descExtra = AccountPrebattle.getPrebattleDescription(arena.extraData or {})
            arenaSubType = getArenaSubTypeName(BigWorld.player().arenaTypeID)
            if descExtra:
                self.call('loading.setBattleType', [arena.guiType + 1, descExtra])
            elif arena.guiType == constants.ARENA_GUI_TYPE.RANDOM:
                self.call('loading.setBattleType', [arenaSubType, '#arenas:type/%s/name' % arenaSubType])
            else:
                self.call('loading.setBattleType', [arena.guiType + 1, '#menu:loading/battleTypes/%d' % arena.guiType])
            winText = getBattleSubTypeWinText(BigWorld.player().arenaTypeID)
            if arenaSubType != ArenaType._GAMEPLAY_TYPE_TO_NAME[constants.ARENA_GAMEPLAY_TYPE.TYPE_2]:
                self.call('loading.setWinText', [winText])
                self.__winTextInit = True
        self.call('loading.setTip', [getTip()])
        self.__updatePlayers()
        return

    def __updatePlayers(self, *args):
        stat = {1: [],
         2: []}
        squads = {1: {},
         2: {}}
        player = BigWorld.player()
        if player is None:
            return
        elif self.__arena is None:
            return
        else:
            vehicles = self.__arena.vehicles
            for vId, vData in vehicles.items():
                team = vData['team']
                name = vData['name'] if vData['name'] is not None else makeString('#ingame_gui:players_panel/unknown_name')
                if vData['clanAbbrev']:
                    name = name + '[%s]' % vData['clanAbbrev']
                if vData['vehicleType'] is not None:
                    vShortName = vData['vehicleType'].type.shortUserString
                    vName = vData['vehicleType'].type.userString
                    vIcon = _CONTOUR_ICONS_MASK % {'unicName': vData['vehicleType'].type.name.replace(':', '-')}
                    balanceWeight = vData['vehicleType'].balanceWeight
                else:
                    vName = vShortName = makeString('#ingame_gui:players_panel/unknown_vehicle')
                    vIcon = _CONTOUR_ICONS_MASK % {'unicName': 'unknown'}
                    balanceWeight = 0.0
                if vData['isAlive']:
                    isAlive = vData['isAvatarReady']
                    vehActions = VehicleActions.getBitMask(vData.get('actions', {}))
                    if vData['prebattleID'] != 0:
                        squads[team][vData['prebattleID']] = vData['prebattleID'] not in squads[team].keys() and 1
                    else:
                        squads[team][vData['prebattleID']] += 1
                user = MessengerDispatcher.g_instance.users.getUser(vData['accountDBID'], name)
                stat[team].append([name,
                 vIcon,
                 vShortName,
                 not isAlive,
                 vId,
                 vData['prebattleID'],
                 balanceWeight,
                 vName,
                 not vData['isAlive'],
                 vData['name'],
                 vData['accountDBID'],
                 user.isMuted(),
                 vehActions,
                 VoiceChatInterface.g_instance.isPlayerSpeaking(vData['accountDBID'])])

            squadsSorted = {}
            squadsSorted[1] = sorted(squads[1].iteritems(), cmp=lambda x, y: cmp(x[0], y[0]))
            squadsSorted[2] = sorted(squads[2].iteritems(), cmp=lambda x, y: cmp(x[0], y[0]))
            squadsFiltered = {}
            squadsFiltered[1] = [ id for id, num in squadsSorted[1] if 1 < num < 4 and self.__arena.guiType == constants.ARENA_GUI_TYPE.RANDOM ]
            squadsFiltered[2] = [ id for id, num in squadsSorted[2] if 1 < num < 4 and self.__arena.guiType == constants.ARENA_GUI_TYPE.RANDOM ]
            for team in (1, 2):
                playerVehicleID = None
                if hasattr(player, 'playerVehicleID'):
                    playerVehicleID = player.playerVehicleID
                value = ['team2', -1, -1]
                data = sorted(stat[team], cmp=_playerComparator)
                for item in data:
                    item[5] = squadsFiltered[team].index(item[5]) + 1 if item[5] in squadsFiltered[team] else 0
                    if item[9] == player.name and value[1] == -1 or item[4] == playerVehicleID:
                        value[1] = item[4]
                        if item[5] > 0:
                            value[2] = item[5]
                        value[0] = 'team1'
                        self.setTeams(team)
                        if not self.__winTextInit:
                            self.__winTextInit = True
                            winText = getBattleSubTypeWinText(BigWorld.player().arenaTypeID)
                            self.call('loading.setWinText', [winText + '%d' % team])
                    value.extend(item[:-6])
                    value.append(item[10])
                    value.append(item[11])
                    value.append(item[12])
                    value.append(item[13])

                self.call('loading.setTeam', value)

            return

    def setTeams(self, myTeam):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena:
            extraData = arena.extraData or {}
            team1 = extraData.get('opponents', {}).get('%s' % myTeam, {}).get('name', '#menu:loading/team1')
            team2 = extraData.get('opponents', {}).get('2' if myTeam == 1 else '1', {}).get('name', '#menu:loading/team2')
            self.call('loading.setTeams', [team1, team2])
        return


def _playerComparator(x1, x2):
    if x1[8] < x2[8]:
        return -1
    if x1[8] > x2[8]:
        return 1
    if x1[6] < x2[6]:
        return 1
    if x1[6] > x2[6]:
        return -1
    if x1[2] < x2[2]:
        return -1
    if x1[2] > x2[2]:
        return 1
    if x1[9] < x2[9]:
        return -1
    if x1[9] > x2[9]:
        return 1
