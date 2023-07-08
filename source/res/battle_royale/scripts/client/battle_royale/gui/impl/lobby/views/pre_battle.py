# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/pre_battle.py
import BigWorld
import ArenaType
from BattleRoyaleTournament import MAX_PLAYERS_IN_SQUAD
from battle_royale.gui.impl.gen.view_models.views.lobby.views.pre_battle_view_model import PreBattleViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.team_model import TeamModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.user_extended_model import UserExtendedModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.user_model import UserModel
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from wg_async import wg_async, wg_await
from constants import IS_DEVELOPMENT
from frameworks.wulf import ViewFlags, ViewSettings, Array
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import LobbyHeaderMenuEvent
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.dialogs.builders import WarningDialogBuilder
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.dialogs import dialogs
from gui.impl.gen.view_models.ui_kit.gf_drop_down_item import GfDropDownItem
from gui.impl.pub import ViewImpl
from gui.prb_control import prbEntityProperty
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from skeletons.gui.game_control import IBattleRoyaleController, IBattleRoyaleTournamentController
from skeletons.gui.shared import IItemsCache

class PreBattleView(ViewImpl, LobbySubView):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __battleRoyaleTournamentController = dependency.descriptor(IBattleRoyaleTournamentController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = PreBattleViewModel()
        super(PreBattleView, self).__init__(settings)
        self.__isObserver = False
        self.__canStartBattle = False
        self.__isSolo = True
        self.__countOfReady = 0
        self.__maps = []
        Waiting.show('loadPage')

    @prbEntityProperty
    def prbEntity(self):
        return None

    @property
    def viewModel(self):
        return super(PreBattleView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onBattleClick += self.__onBattleClick
        self.viewModel.onClose += self.__onClose
        self.__battleRoyaleTournamentController.onUpdatedParticipants += self.__updateParticipants
        super(PreBattleView, self)._initialize(*args, **kwargs)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), scope=EVENT_BUS_SCOPE.LOBBY)
        Waiting.hide('loadPage')

    def _finalize(self):
        self.viewModel.onBattleClick -= self.__onBattleClick
        self.viewModel.onClose -= self.__onClose
        self.__battleRoyaleTournamentController.onUpdatedParticipants -= self.__updateParticipants
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), scope=EVENT_BUS_SCOPE.LOBBY)
        super(PreBattleView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(PreBattleView, self)._onLoading(*args, **kwargs)
        token = self.__battleRoyaleTournamentController.getSelectedToken()
        if token.isValid:
            self.__isObserver = token.isObserver
            self.__canStartBattle = token.isObserver or IS_DEVELOPMENT and BigWorld.player().name.endswith('admin')
            self.__isSolo = token.isSolo
        self.__initModel()

    def _onLoaded(self, *args, **kwargs):
        self.__updateParticipants()

    def __onClose(self):
        self.prbEntity.exitFromQueue()

    def __onBattleClick(self, args=None):
        if args is None:
            return
        else:
            mapId = args.get('mapId', '0')
            if self.__canStartBattle and not self.__allPlayersIsReady():
                self.__showConfirmation(mapId)
                return
            BigWorld.player().AccountBattleRoyaleTournamentComponent.tournamentForceStart(int(mapId))
            return

    @wg_async
    def __showConfirmation(self, mapId):
        texts = R.strings.dialogs.battleRoyale.preBattle
        builder = WarningDialogBuilder()
        builder.setTitle(texts.title())
        builder.setMessagesAndButtons(message=texts, buttons=texts, focused=DialogButtons.CANCEL)
        result = yield wg_await(dialogs.showSimple(builder.build(self)))
        if result:
            BigWorld.player().AccountBattleRoyaleTournamentComponent.tournamentForceStart(int(mapId))

    def __getMaps(self):
        mapsModel = Array()
        for _name, _id in self.__maps:
            mapModel = GfDropDownItem()
            mapModel.setLabel(_name)
            mapModel.setId(str(_id))
            mapsModel.addViewModel(mapModel)

        return mapsModel

    def __initModel(self):
        teamsRange = 20 if self.__isSolo else 10
        playersRange = 1 if self.__isSolo else MAX_PLAYERS_IN_SQUAD
        self.__initMaps()
        with self.viewModel.transaction() as model:
            model.setTitle(R.strings.battle_royale.preBattle.title())
            model.setIsSpectator(self.__canStartBattle)
            self.__setCurrentTeam(model, [])
            if self.__canStartBattle:
                mapsModel = self.__getMaps()
                model.setMaps(mapsModel)
            teamsModel = Array()
            for idx in range(teamsRange):
                team = TeamModel()
                team.setId(idx + 1)
                users = Array()
                for _ in range(playersRange):
                    userModel = UserModel()
                    self.__userClearData(userModel)
                    users.addViewModel(userModel)

                team.setUsers(users)
                teamsModel.addViewModel(team)

            model.setTeams(teamsModel)

    def __updateParticipants(self):
        participants = self.__battleRoyaleTournamentController.getParticipants()
        players = self.__convertToPlayers(participants)
        with self.viewModel.transaction() as model:
            if not self.__isObserver:
                databaseID = BigWorld.player().databaseID
                teamID = next((p.teamID for p in participants if p.databaseID == databaseID and p.teamID in players), None)
                if teamID:
                    self.__setCurrentTeam(model, players[teamID])
            teamsModel = model.getTeams()
            for team in teamsModel:
                users = team.getUsers()
                teamId = team.getId()
                if teamId in players:
                    teamPlayers = iter(players[teamId])
                    for user in users:
                        player = next(teamPlayers, None)
                        if player:
                            user.setName(player['name'])
                            user.setIsReady(player['typeCD'] != 0)
                            user.setIsCurrentUser(BigWorld.player().name == player['name'])
                        self.__userClearData(user)

                for user in users:
                    self.__userClearData(user)

        return

    def __convertToPlayers(self, participants):
        self.__countOfReady = 0
        teams = {}
        for p in participants:
            teamID = p['teamID']
            if p['typeCD'] != 0:
                self.__countOfReady += 1
            if teamID not in teams:
                teams[teamID] = []
            teams[teamID].append(p)

        for p in teams.itervalues():
            p.sort(key=lambda x: (-x['role'], x['name']))

        return teams

    def __setCurrentTeam(self, model, players):
        players = iter(players)
        currentTeam = model.getCurrentTeam()
        currentTeam.clear()
        for _ in range(1 if self.__isSolo else MAX_PLAYERS_IN_SQUAD):
            player = next(players, None)
            userModel = UserExtendedModel()
            if player:
                userModel.setIsCurrentUser(BigWorld.player().name == player['name'])
                userModel.setIsReady(player['typeCD'] != 0)
                userModel.setName(player['name'])
                vehicle = self.__itemsCache.items.getItemByCD(player['typeCD'])
                if vehicle:
                    userModel.setVehicleType(vehicle.type)
                    userModel.setVehicleName(vehicle.shortUserName)
            else:
                self.__userClearData(userModel)
            currentTeam.addViewModel(userModel)

        currentTeam.invalidate()
        return

    def __userClearData(self, user):
        user.setName('')
        user.setIsCurrentUser(False)
        user.setIsReady(False)

    def __initMaps(self):
        self.__maps.append((backport.text(R.strings.battle_royale.preBattle.mapRandom()), 0))
        self.__maps.append((ArenaType.g_cache[86].name, 86))
        self.__maps.append((ArenaType.g_cache[97].name, 97))
        self.__maps.append((ArenaType.g_cache[98].name, 98))

    def __allPlayersIsReady(self):
        return self.__countOfReady == 20
