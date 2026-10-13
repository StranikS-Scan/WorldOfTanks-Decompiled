# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/states.py
from __future__ import absolute_import
import typing
from fort_rush.gui.impl.lobby.fort_rush_progression_view import FortRushProgressionView
from fort_rush.gui.scaleform.genConsts.FORT_RUSH_HANGAR_ALIASES import FORT_RUSH_HANGAR_ALIASES
from fort_rush.gui.shared.event_dispatcher import showFortRushInfoPage
from fort_rush_common.fort_rush_constants import QUEUE_TYPE
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from WeakMethod import WeakMethodProxy
from frameworks_common.state_machine import StateFlags
from frameworks_common.state_machine.transitions import TransitionType
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.battle_results.service import PostBattleResultsStateMixin
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.base.proto_states import generateBasicHangarStateClasses, generateBasicLoadoutStateClasses, _LoadoutConfirmStatePrototype
from gui.impl.lobby.hangar.playlists_states import generateVehiclePlayListClasses
from gui.impl.lobby.hangar.states import HangarState, EasyTankEquipState
from gui.lobby_state_machine.states import SubScopeSubLayerState, SubScopeTopLayerState, GuiImplViewLobbyState, SFViewLobbyState, LobbyStateDescription, LobbyState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared.utils.functions import getViewName
from helpers import dependency
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine

class FortRushStateIDs(object):
    HANGAR = 'fortRushHangar'
    LOADOUT_LEAVE = 'fortRushLoadoutConfirmLeave'
    PBS = 'fortRushPBS'
    OVERVIEW = 'overview'
    TEAM_SCORE = 'teamScore'
    PROGRESSION = 'progression'


def registerStates(machine):
    machine.addState(FortRushHangarState())
    machine.addState(FortRushEditVehiclePlaylistsState())
    machine.addState(FortRushLoadoutState())
    machine.addState(FortRushPostBattleResultState())
    machine.addState(FortRushProgressionState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(FortRushHangarState), transitionType=TransitionType.EXTERNAL)
    machine.addNavigationTransitionFromParent(machine.getStateByCls(FortRushPostBattleResultState), transitionType=TransitionType.EXTERNAL)
    machine.addNavigationTransitionFromParent(machine.getStateByCls(FortRushProgressionState), transitionType=TransitionType.EXTERNAL)


def _isInPrb(event):
    dispatcher = g_prbLoader.getDispatcher()
    if not dispatcher:
        return False
    else:
        prbEntity = dispatcher.getEntity()
        return False if prbEntity is None else prbEntity.getQueueType() == QUEUE_TYPE.FORT_RUSH and not prbEntity.isInQueue()


class _HangarStateProto(SFViewLobbyState):
    STATE_ID = FortRushStateIDs.HANGAR
    VIEW_KEY = ViewKey(FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_HANGAR_WITH_AMMUNITION)
    _fortRushCtrl = dependency.descriptor(IFortRushBattleController)

    def registerTransitions(self):
        lsm = self.getMachine()
        fortRushEasyTankEquip = lsm.getStateByCls(FortRushEasyTankEquipState)
        hijackCondition = WeakMethodProxy(self._hijackTransitionCondition)
        self.getParent().addTransition(HijackTransition(HangarState, hijackCondition), self)
        self.getParent().addTransition(HijackTransition(EasyTankEquipState, hijackCondition), fortRushEasyTankEquip)

    def _hijackTransitionCondition(self, _):
        return self._fortRushCtrl.isEnabled() and self._fortRushCtrl.isEventPrbActive()


class _LoadoutConfirmStateProto(_LoadoutConfirmStatePrototype):
    STATE_ID = FortRushStateIDs.LOADOUT_LEAVE


FortRushHangarState, FortRushRootHangarState, FortRushAllVehiclesState, FortRushEasyTankEquipState = generateBasicHangarStateClasses(SubScopeSubLayerState, R.invalid, hangarPrototypeCls=_HangarStateProto)
FortRushEditVehiclePlaylistsState = generateVehiclePlayListClasses(parentStateCls=FortRushHangarState, parentAllVehicleStateCls=FortRushAllVehiclesState)
FortRushLoadoutState, _, _, FortRushShellsLoadoutState, _, _, _ = generateBasicLoadoutStateClasses(FortRushHangarState, R.invalid, confirmStatePrototypeCls=_LoadoutConfirmStateProto)

@SubScopeTopLayerState.parentOf
class FortRushProgressionState(GuiImplViewLobbyState):
    STATE_ID = FortRushStateIDs.PROGRESSION
    VIEW_KEY = ViewKey(R.views.fort_rush.mono.lobby.progression_view())

    def __init__(self):
        super(FortRushProgressionState, self).__init__(FortRushProgressionView, ScopeTemplates.LOBBY_TOP_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.fort_rush.progressionView.stateHeader()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showFortRushInfoPage, tooltipHeader=backport.text(R.strings.fort_rush.progression.info_button.header()), tooltipBody=backport.text(R.strings.fort_rush.progression.info_button.body())),))


@SubScopeSubLayerState.parentOf
class FortRushPostBattleResultState(SFViewLobbyState, PostBattleResultsStateMixin):
    STATE_ID = FortRushStateIDs.PBS
    VIEW_KEY = ViewKey(FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_BATTLE_RESULTS)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FortRushPostBattleResultState, self).__init__(flags=flags)
        self.__cachedArenaId = None
        return

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.menu.headerButtons.battle.types.fortRush()))

    def registerTransitions(self):
        lsm = self.getMachine()
        for child in self.getChildrenStates():
            lsm.addNavigationTransitionFromParent(child)

    @classmethod
    def goTo(cls, arenaUniqueID):
        super(FortRushPostBattleResultState, cls).goTo(arenaUniqueID=arenaUniqueID)

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(_OverviewTab(StateFlags.INITIAL))
        lsm.addState(_TeamScoreTab())

    def _onEntered(self, event):
        self.__cachedArenaId = event.params['arenaUniqueID']
        super(FortRushPostBattleResultState, self)._onEntered(event)

    def _onExited(self):
        super(FortRushPostBattleResultState, self)._onExited()
        self.__cachedArenaId = None
        return

    def getViewKey(self, params=None):
        arenaUniqueID = self.__cachedArenaId
        alias = super(FortRushPostBattleResultState, self).getViewKey().alias
        return ViewKey(alias, getViewName(alias, arenaUniqueID))


class PostBattleTab(LobbyState):

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PostBattleTab, self).__init__(flags=flags)
        self.__cachedParams = None
        return

    def serializeParams(self):
        return self.__cachedParams

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.fort_rush_post_battle_results.state.title()))

    def _onEntered(self, event):
        super(PostBattleTab, self)._onEntered(event)
        self.__cachedParams = event.params


@FortRushPostBattleResultState.parentOf
class _OverviewTab(PostBattleTab):
    STATE_ID = FortRushStateIDs.OVERVIEW


@FortRushPostBattleResultState.parentOf
class _TeamScoreTab(PostBattleTab):
    STATE_ID = FortRushStateIDs.TEAM_SCORE
