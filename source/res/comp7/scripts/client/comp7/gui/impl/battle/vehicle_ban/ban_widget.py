# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/battle/vehicle_ban/ban_widget.py
import BigWorld
import BattleReplay
from PlayerEvents import g_playerEvents
from ReplayEvents import g_replayEvents
from comp7.gui.impl.battle.vehicle_ban.ban_helpers import fillComp7VehicleModel, getOwnDatabaseID
from comp7.gui.impl.gen.view_models.views.battle.ban_widget_model import BanWidgetModel
from comp7.gui.impl.gen.view_models.views.battle.banned_vehicle_model import BannedVehicleModel
from comp7.gui.impl.gen.view_models.views.battle.enums import BanState, CandidateState
from comp7.gui.shared.event_dispatcher import showComp7VehicleBanWindow
from comp7_core.gui.comp7_core_constants import BATTLE_CTRL_ID
from comp7_core_constants import ArenaPrebattlePhase
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
BAN_STATES_MAPPING = {ArenaPrebattlePhase.NONE: BanState.NONE,
 ArenaPrebattlePhase.PREPICK: BanState.PREPICK,
 ArenaPrebattlePhase.VOTING: BanState.VOTING,
 ArenaPrebattlePhase.PICK: BanState.FINISHED}

class BanWidgetView(ViewImpl):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __itemsCache = dependency.descriptor(IItemsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        settings = ViewSettings(R.views.comp7.mono.battle.ban_widget())
        settings.model = BanWidgetModel()
        super(BanWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BanWidgetView, self).getViewModel()

    def _onLoading(self, *_, **__):
        super(BanWidgetView, self)._onLoading()
        self.__addListeners()
        self.__updateData()

    def _finalize(self):
        self.__removeListeners()
        super(BanWidgetView, self)._finalize()

    def __addListeners(self):
        self.viewModel.onOpen += self.__onOpen
        self.__comp7Controller.onModeConfigChanged += self.__onConfigChanged
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if vehicleBanCtrl is not None:
            vehicleBanCtrl.onVehicleBanStateUpdated += self.__updateData
            vehicleBanCtrl.onCandidatesForBanUpdated += self.__updateData
            vehicleBanCtrl.onBanPhaseUpdated += self.__onBanPhaseUpdated
        g_playerEvents.onAvatarObserverVehicleChanged += self.__onAvatarObserverVehicleChanged
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpFinish += self.__onReplayTimeWarpFinish
        return

    def __removeListeners(self):
        self.viewModel.onOpen -= self.__onOpen
        self.__comp7Controller.onModeConfigChanged -= self.__onConfigChanged
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if vehicleBanCtrl is not None:
            vehicleBanCtrl.onVehicleBanStateUpdated -= self.__updateData
            vehicleBanCtrl.onCandidatesForBanUpdated -= self.__updateData
            vehicleBanCtrl.onBanPhaseUpdated -= self.__onBanPhaseUpdated
        g_playerEvents.onAvatarObserverVehicleChanged -= self.__onAvatarObserverVehicleChanged
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpFinish -= self.__onReplayTimeWarpFinish
        return

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        arenaDP = self.__sessionProvider.getArenaDP()
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if arenaDP is None or vehicleBanCtrl is None:
            self.__setDefaultData(model)
        elif vehicleBanCtrl.getArenaPrebattlePhase() != ArenaPrebattlePhase.PICK:
            self.__setCandidates(model)
        else:
            self.__setResults(model)
        return

    def __setDefaultData(self, model):
        model.setBanState(BanState.NONE)
        model.setCandidateState(CandidateState.NOSELECTED)

    def __setCandidates(self, model):
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        banPhase = vehicleBanCtrl.getArenaPrebattlePhase()
        model.setBanState(BAN_STATES_MAPPING[banPhase])
        vehicleCDToBan, isConfirmed = vehicleBanCtrl.getPlayerChoiceForBan(getOwnDatabaseID())
        fillComp7VehicleModel(model.vehicleToBan, vehicleCDToBan)
        model.setConfirmedChoice(isConfirmed)
        candidates = vehicleBanCtrl.candidatesForBan.get('candidates')
        if not candidates:
            model.setCandidateState(CandidateState.NOSELECTED)
            return
        if len(candidates) > 1:
            model.setCandidateState(CandidateState.MULTIPLECANDIDATES)
        elif candidates[0]:
            model.setCandidateState(CandidateState.SINGLECANDIDATE)
        else:
            model.setCandidateState(CandidateState.DONTBANSELECTED)
        votesNumber = vehicleBanCtrl.candidatesForBan.get('maxTotalVotes')
        candidatesArray = model.getBannedByAlliesVehicles()
        candidatesArray.clear()
        for vehicleCDToBan in candidates:
            candidateModel = BannedVehicleModel()
            fillComp7VehicleModel(candidateModel, vehicleCDToBan)
            candidateModel.setCount(votesNumber)
            candidatesArray.addViewModel(candidateModel)

        candidatesArray.invalidate()

    def __setResults(self, model):
        arenaDP = self.__sessionProvider.getArenaDP()
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        model.setBanState(BanState.FINISHED)
        ownVehicleID = arenaDP.getVehIDByAccDBID(getOwnDatabaseID())
        ownTeam = arenaDP.getVehicleInfo(ownVehicleID).team
        for teamID, banVehicleInfo in vehicleBanCtrl.bannedVehicles.iteritems():
            bannedVehicleCD = banVehicleInfo['vehicleCD']
            isRandomlySelected = banVehicleInfo['isRandomlySelected']
            totalVotes = banVehicleInfo['totalVotes']
            if teamID == ownTeam:
                fillComp7VehicleModel(model.bannedByAlliesVehicle, bannedVehicleCD)
                model.setIsAlliesRandomlySelected(isRandomlySelected)
                model.setAlliesVotes(totalVotes)
            fillComp7VehicleModel(model.bannedByEnemiesVehicle, bannedVehicleCD)
            model.setIsEnemyRandomlySelected(isRandomlySelected)
            model.setEnemyVotes(totalVotes)

    def __onOpen(self):
        if not self.__isVehicleBanEnabled():
            return
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if vehicleBanCtrl.getArenaPrebattlePhase() in (ArenaPrebattlePhase.PREPICK, ArenaPrebattlePhase.VOTING):
            showComp7VehicleBanWindow()

    def __onBanPhaseUpdated(self):
        if not self.__isVehicleBanEnabled():
            return
        self.__updateData()
        if BigWorld.player().isObserver():
            return
        if self.__getVehicleBanCtrl().getArenaPrebattlePhase() == ArenaPrebattlePhase.VOTING:
            showComp7VehicleBanWindow()

    def __onAvatarObserverVehicleChanged(self, *_):
        if self.__isVehicleBanEnabled():
            self.__updateData()

    def __onConfigChanged(self):
        if self.viewModel is not None:
            self.__updateData()
        return

    def __getVehicleBanCtrl(self):
        return self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.COMP7_VEHICLE_BAN_CTRL)

    def __isVehicleBanEnabled(self):
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        return vehicleBanCtrl is not None and vehicleBanCtrl.isVehicleBanEnabled

    def __onReplayTimeWarpFinish(self):
        self.__onBanPhaseUpdated()
