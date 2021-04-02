# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_royale/pre_battle.py
import BigWorld
import ArenaType
from helpers import dependency
from async import async, await
from frameworks.wulf import ViewFlags, ViewSettings, Array
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.dialogs.builders import WarningDialogBuilder
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.dialogs import dialogs
from gui.impl.gen.view_models.ui_kit.gf_drop_down_item import GfDropDownItem
from gui.impl.gen.view_models.views.lobby.battle_royale.pre_battle_view_model import PreBattleViewModel
from gui.impl.gen.view_models.views.lobby.battle_royale.team_model import TeamModel
from gui.impl.gen.view_models.views.lobby.battle_royale.user_extended_model import UserExtendedModel
from gui.impl.gen.view_models.views.lobby.battle_royale.user_model import UserModel
from gui.impl.pub import ViewImpl
from gui.prb_control import prbEntityProperty
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.Scaleform.daapi import LobbySubView
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
        self.__isSolo = True
        self.__countOfReady = 0
        self.__teamID = 0
        self.__maps = []

    @prbEntityProperty
    def prbEntity(self):
        return None

    @property
    def viewModel(self):
        return super(PreBattleView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onBattleClick += self.__onBattleClick
        self.viewModel.onClose += self.__onClose
        self.__battleRoyaleTournamentController.onUpdatedParticipants += self.__updateParticipants
        super(PreBattleView, self)._initialize(*args, **kwargs)

    def _finalize(self):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onBattleClick -= self.__onBattleClick
        self.viewModel.onClose -= self.__onClose
        self.__battleRoyaleTournamentController.onUpdatedParticipants -= self.__updateParticipants
        super(PreBattleView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(PreBattleView, self)._onLoading(*args, **kwargs)
        token = self.__battleRoyaleTournamentController.getSelectedToken()
        if token.isValid:
            self.__isObserver = token.isObserver
            self.__isSolo = token.isSolo
            self.__teamID = token.teamID
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
            if self.__isObserver and not self.__allPlayersIsReady():
                self.__showConfirmation(mapId)
                return
            BigWorld.player().AccountBattleRoyaleTournamentComponent.tournamentForceStart(int(mapId))
            return

    @async
    def __showConfirmation(self, mapId):
        texts = R.strings.dialogs.battleRoyale.preBattle
        builder = WarningDialogBuilder()
        builder.setTitle(texts.title())
        builder.setMessagesAndButtons(message=texts, buttons=texts, focused=DialogButtons.CANCEL)
        result = yield await(dialogs.showSimple(builder.build(self)))
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
        playersRange = 1 if self.__isSolo else 3
        self.__initMaps()
        with self.viewModel.transaction() as model:
            model.setTitle(R.strings.battle_royale.preBattle.title())
            model.setIsSpectator(self.__isObserver)
            self.__setCurrentTeam(model, [])
            if self.__isObserver:
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
            if not self.__isObserver and self.__teamID in players:
                self.__setCurrentTeam(model, players[self.__teamID])
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
        for _ in range(1 if self.__isSolo else 3):
            player = next(players, None)
            userModel = UserExtendedModel()
            if player:
                userModel.setIsCurrentUser(BigWorld.player().name == player['name'])
                userModel.setIsReady(player['typeCD'] != 0)
                userModel.setName(player['name'])
                vehicle = self.__itemsCache.items.getItemByCD(player['typeCD'])
                if vehicle:
                    userModel.setNation(vehicle.nationName)
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

    def __allPlayersIsReady(self):
        return self.__countOfReady == 20 if self.__isSolo else self.__countOfReady == 30
