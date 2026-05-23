# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/battle/vehicle_ban/ban_view.py
import typing
import BattleReplay
import SoundGroups
from ReplayEvents import g_replayEvents
from comp7.gui.battle_control.arena_info.arena_vos import Comp7Keys
from comp7.gui.battle_control.arena_info.vos_collections import Comp7SortKey
from comp7.gui.impl.battle.tooltips.ban_show_tooltip import BanShowTooltip
from comp7.gui.impl.battle.vehicle_ban.ban_helpers import convertVehicleCD, fillComp7VehicleModel, fillBanProgressionModel, getOwnDatabaseID
from comp7.gui.impl.gen.view_models.views.battle.ban_view_model import BanViewModel
from comp7.gui.impl.gen.view_models.views.battle.comp7_vehicle_model import Comp7VehicleModel
from comp7.gui.impl.gen.view_models.views.battle.constants import Constants
from comp7.gui.impl.gen.view_models.views.battle.player_model import PlayerModel
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, Rank, SeasonName
from comp7_core.gui.battle_control.controllers.sound_ctrls.comp7_battle_sounds import BAN_VIEW_SOUND_SPACE
from comp7_core.gui.comp7_core_constants import BATTLE_CTRL_ID
from comp7_core.gui.impl.lobby.comp7_core_helpers import comp7_core_model_helpers
from comp7_core_constants import ArenaPrebattlePhase
from constants import REQUEST_COOLDOWN
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import GUI_NATIONS
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.impl.pub.window_impl import WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from messenger.m_constants import USER_ACTION_ID, UserEntityScope
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple
    from frameworks.wulf import Array
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
    from messenger.proto.entities import UserEntity
    from messenger.storage.UsersStorage import UsersStorage
SOUND_NAME = 'comp_7_bans_choice_confirm'

class BanView(ViewImpl, BattleGUIKeyHandler):
    __slots__ = ('__selectionTimer',)
    _COMMON_SOUND_SPACE = BAN_VIEW_SOUND_SPACE
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __appLoader = dependency.descriptor(IAppLoader)
    __muteActions = {USER_ACTION_ID.MUTE_SET,
     USER_ACTION_ID.MUTE_UNSET,
     USER_ACTION_ID.IGNORED_ADDED,
     USER_ACTION_ID.IGNORED_REMOVED,
     USER_ACTION_ID.TMP_IGNORED_ADDED,
     USER_ACTION_ID.TMP_IGNORED_REMOVED}

    def __init__(self):
        settings = ViewSettings(R.views.comp7.mono.battle.ban_view())
        settings.model = BanViewModel()
        self.__selectionTimer = CallbackDelayer()
        self.__usersStorage = storage_getter('users')()
        super(BanView, self).__init__(settings)

    def handleEscKey(self, isDown):
        return isDown

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.comp7.mono.battle.tooltips.ban_show_tooltip():
            params = {'longName': event.getArgument('longName', ''),
             'type': event.getArgument('type', ''),
             'isPremium': event.getArgument('isPremium', False),
             'confirmedChoice': event.getArgument('confirmedChoice', False),
             'vehicleCD': event.getArgument('vehicleCD', False),
             'roleKey': event.getArgument('roleKey', False)}
            return BanShowTooltip(params=params)
        return super(BanView, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def viewModel(self):
        return super(BanView, self).getViewModel()

    @property
    def _battleApp(self):
        return self.__appLoader.getApp(APP_NAME_SPACE.SF_BATTLE)

    def _initialize(self):
        battleApp = self._battleApp
        if battleApp:
            battleApp.registerGuiKeyHandler(self)
            battleApp.enterGuiControlMode(self.uniqueID)
            contextMenuMgr = battleApp.contextMenuManager
            if contextMenuMgr is not None:
                contextMenuMgr.as_hideS()
        return

    def _onLoading(self, *args, **kwargs):
        super(BanView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateData()

    def _finalize(self):
        self.__selectionTimer.clearCallbacks()
        self.__selectionTimer = None
        self.__removeListeners()
        super(BanView, self)._finalize()
        battleApp = self._battleApp
        if battleApp:
            battleApp.unregisterGuiKeyHandler(self)
            battleApp.leaveGuiControlMode(self.uniqueID)
        return

    def __addListeners(self):
        self.viewModel.onClose += self.__onClose
        self.viewModel.banProgression.pollServerTime += self.__onPollServerTime
        self.viewModel.onSelect += self.__onSelect
        self.viewModel.onConfirm += self.__onConfirm
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated
        self.__comp7Controller.onModeConfigChanged += self.__onConfigChanged
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if vehicleBanCtrl is not None:
            vehicleBanCtrl.onVehicleBanStateUpdated += self.__updateData
            vehicleBanCtrl.onBanPhaseUpdated += self.__onBanPhaseUpdated
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onAvatarReady += self.__updateData
            arena.onVehicleUpdated += self.__updateData
        g_messengerEvents.voip.onPlayerSpeaking += self.__onPlayerSpeaking
        g_messengerEvents.users.onUserActionReceived += self.__onUserActionReceived
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarp
        return

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.banProgression.pollServerTime -= self.__onPollServerTime
        self.viewModel.onSelect -= self.__onSelect
        self.viewModel.onConfirm -= self.__onConfirm
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated
        self.__comp7Controller.onModeConfigChanged -= self.__onConfigChanged
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if vehicleBanCtrl is not None:
            vehicleBanCtrl.onVehicleBanStateUpdated -= self.__updateData
            vehicleBanCtrl.onBanPhaseUpdated -= self.__onBanPhaseUpdated
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onAvatarReady -= self.__updateData
            arena.onVehicleUpdated -= self.__updateData
        g_messengerEvents.voip.onPlayerSpeaking -= self.__onPlayerSpeaking
        g_messengerEvents.users.onUserActionReceived -= self.__onUserActionReceived
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarp
        return

    def __updateData(self, *_):
        with self.viewModel.transaction() as vm:
            self.__updatePhaseData(model=vm)
            self.__setVehicles(vm)
            self.__setPlayers(vm)

    @replaceNoneKwargsModel
    def __updatePhaseData(self, model=None):
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        fillBanProgressionModel(model.banProgression, vehicleBanCtrl)

    def __setVehicles(self, viewModel):
        nationsOrder = viewModel.getNationsOrder()
        nationsOrder.clear()
        for nation in GUI_NATIONS:
            nationsOrder.addString(nation)

        nationsOrder.invalidate()
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        vehiclesListForBan = vehicleBanCtrl.vehiclesListForBan if vehicleBanCtrl is not None else []
        vehiclesArray = viewModel.getVehicles()
        vehiclesListShown = set((vehicleModel.getVehicleCD() for vehicleModel in vehiclesArray))
        if vehiclesListShown == set(vehiclesListForBan):
            return
        else:
            vehiclesArray.clear()
            for vehicleCD in vehiclesListForBan:
                vehicleModel = Comp7VehicleModel()
                fillComp7VehicleModel(vehicleModel, vehicleCD)
                vehiclesArray.addViewModel(vehicleModel)

            vehiclesArray.invalidate()
            return

    def __fillPlayerModel(self, vehicleInfo, vehicleCDToBan, isConfirmed, playerModel=None):
        playerModel = playerModel if playerModel is not None else PlayerModel()
        vehicleCD = vehicleInfo.vehicleType.compactDescr
        fillComp7VehicleModel(playerModel.vehicle, vehicleCD)
        playerModel.setSelectedVehicleToBan(vehicleCDToBan is not None)
        fillComp7VehicleModel(playerModel.vehicleToBan, vehicleCDToBan)
        playerModel.setId(vehicleInfo.player.accountDBID)
        playerModel.setUserName(vehicleInfo.player.name)
        playerModel.setClanTag(vehicleInfo.player.clanAbbrev)
        playerModel.setBadgeID(vehicleInfo.selectedBadge)
        playerModel.setSuffixBadgeID(vehicleInfo.selectedSuffixBadge)
        playerModel.setConfirmedChoice(isConfirmed)
        playerModel.setIsLoaded(vehicleInfo.isReady())
        user = self.__usersStorage.getUser(vehicleInfo.player.avatarSessionID, scope=UserEntityScope.BATTLE)
        if user:
            playerModel.setIsChatEnabled(not user.isIgnored())
            playerModel.setIsVoiceEnabled(not user.isMuted())
        rank, division = vehicleInfo.gameModeSpecific.getValue(Comp7Keys.RANK, default=(0, 0))
        isQualification = rank == 0
        playerModel.setIsQualification(isQualification)
        if not isQualification:
            playerModel.setRank(Rank(rank))
            playerModel.setDivision(Division(division))
        seasonName = comp7_core_model_helpers.getSeasonNameEnum(self.__comp7Controller, SeasonName)
        playerModel.setSeasonName(seasonName)
        return playerModel

    def __setPlayers(self, viewModel):
        arenaDP = self.__sessionProvider.getArenaDP()
        if arenaDP is None:
            return
        else:
            ownDatabaseID = getOwnDatabaseID()
            viewModel.setOwnId(ownDatabaseID)
            playersArray = viewModel.getPlayers()
            playersArray.clear()
            allyTeamVOs = sorted(arenaDP.getAllyVehiclesInfoIterator(), key=Comp7SortKey)
            for vehicleInfo in allyTeamVOs:
                if vehicleInfo.isObserver():
                    continue
                playerDatabaseID = vehicleInfo.player.accountDBID
                vehicleCDToBan, isConfirmed = self.__getPlayerBanState(playerDatabaseID)
                if playerDatabaseID == ownDatabaseID:
                    viewModel.setSelectedVehicleCD(convertVehicleCD(vehicleCDToBan))
                playerModel = self.__fillPlayerModel(vehicleInfo, vehicleCDToBan, isConfirmed)
                playersArray.addViewModel(playerModel)

            playersArray.invalidate()
            return

    def __onPlayerSpeaking(self, accountDBID, isSpeaking):
        for player in self.viewModel.getPlayers():
            if player.getId() == accountDBID:
                player.setIsVoiceActive(isSpeaking)
                self.viewModel.getPlayers().invalidate()
                return

    def __onUserActionReceived(self, actionID, user, shadowMode):
        if actionID in self.__muteActions:
            self.__onChatAction(user.getID(), user.isMuted(), user.isIgnored())

    def __onChatAction(self, playerDBID, isMuted, isIgnored):
        players = self.viewModel.getPlayers()
        for playerModel in players:
            if playerModel.getId() == playerDBID:
                playerModel.setIsVoiceEnabled(not isMuted)
                playerModel.setIsChatEnabled(not isIgnored)
                players.invalidate()
                return

    def __onClose(self):
        self.destroyWindow()

    @args2params(int)
    def __onSelect(self, vehicleCD):
        arenaDP = self.__sessionProvider.getArenaDP()
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if arenaDP is None or vehicleBanCtrl is None:
            return
        else:
            isObserver = arenaDP.getVehicleInfo().isObserver()
            if isObserver:
                return
            vehicleCD = vehicleCD if vehicleCD != Constants.NO_SELECTED_VEHICLE_CD else 0
            vehicleBanCtrl.chooseVehicleForBan(vehicleCD)
            self.viewModel.setIsSelectionAvailable(False)
            self.__selectionTimer.delayCallback(REQUEST_COOLDOWN.VEHICLE_BAN_SELECTION, self.__setSelectionAvailable)
            return

    @args2params(int)
    def __onConfirm(self, vehicleCD):
        arenaDP = self.__sessionProvider.getArenaDP()
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if arenaDP is None or vehicleBanCtrl is None:
            return
        else:
            isObserver = arenaDP.getVehicleInfo().isObserver()
            if isObserver:
                return
            vehicleBanCtrl.confirmBanVehicle()
            self.__destroyWindow()
            return

    def __onPollServerTime(self):
        self.__updatePhaseData()

    def __onBanPhaseUpdated(self):
        if self.__getVehicleBanCtrl().getArenaPrebattlePhase() != ArenaPrebattlePhase.PICK:
            self.__updatePhaseData()
        else:
            self.__destroyWindow()

    def __onStatusUpdated(self, status):
        if comp7_core_model_helpers.isModeForcedDisabled(status, self.__comp7Controller):
            self.destroyWindow()
        else:
            self.__updateData()

    def __onConfigChanged(self):
        if self.viewModel is not None:
            self.__updateData()
        return

    def __getVehicleBanCtrl(self):
        return self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.COMP7_VEHICLE_BAN_CTRL)

    def __getPlayerBanState(self, playerDatabaseID):
        vehicleCDToBan, isConfirmed = None, False
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if vehicleBanCtrl is not None:
            vehicleCDToBan, isConfirmed = vehicleBanCtrl.getPlayerChoiceForBan(playerDatabaseID)
        return (vehicleCDToBan, isConfirmed)

    def __setSelectionAvailable(self):
        self.viewModel.setIsSelectionAvailable(True)

    def __onReplayTimeWarp(self):
        self.__destroyWindow()

    @staticmethod
    def __playSound():
        SoundGroups.g_instance.playSound2D(SOUND_NAME)

    def __destroyWindow(self):
        self.__playSound()
        self.destroyWindow()


class BanViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(BanViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=BanView(), parent=parent)
