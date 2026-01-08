# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/states.py
import typing
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from frontline.constants.aliases import FrontlineHangarAliases
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineConst
from frontline.gui.impl.gen.view_models.views.lobby.views.info_page_scroll_to_section import InfoPageScrollToSection
from frontline.gui.impl.lobby.progression_screen_view import ProgressionScreenView
from gui import SystemMessages
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.base.proto_states import _LoadoutConfirmStatePrototype, generateBasicLoadoutStateClasses
from gui.impl.lobby.hangar.states import HangarState
from gui.lobby_state_machine.states import GuiImplViewLobbyState, LobbyState, LobbyStateDescription, LobbyStateFlags, SFViewLobbyState, SubScopeSubLayerState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.prb_control import prbDispatcherProperty
from gui.shared.event_dispatcher import showFrontlineInfoWindow
from gui.shared.lock_overlays import lockNotificationManager
from gui.shared.utils.functions import getViewName
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.game_control import ILoadoutController
from frontline.gui.frontline_helpers import becomeNonPlayerState
import gui.impl.lobby.hangar.playlists_states as playlists
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from frontline.gui.impl.lobby.hangar_view import FrontlineHangar

def registerStates(machine):
    machine.addState(FrontlineModeState())


def registerTransitions(machine):
    frontlineMode = machine.getStateByCls(FrontlineModeState)
    machine.addNavigationTransitionFromParent(frontlineMode)


class FrontlineStateIDs(object):
    FRONTLINE = 'frontline'
    HANGAR = 'hangar'
    ROOT = '{root}'
    LOADOUT_CONFIRM_LEAVE = 'frontline/loadoutConfirmLeave'
    ALL_VEHICLES = 'allVehicles'
    PROGRESSION_SCREEN = 'frontlineProgressionScreen'
    BATTLE_ABILITIES = FrontlineConst.BATTLE_ABILITIES
    BATTLE_RESULTS = 'fl_battleResults'
    OVERVIEW = 'overview'
    TEAM_SCORE = 'teamScore'
    FINANCIAL_REPORT = 'financialReport'


@SubScopeSubLayerState.parentOf
class FrontlineModeState(LobbyState):
    STATE_ID = FrontlineStateIDs.FRONTLINE
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(FrontlineHangarState(StateFlags.INITIAL))
        lsm.addState(FrontlineLoadoutState())
        lsm.addState(FrontlineAllVehiclesState())
        lsm.addState(ProgressionScreenState())
        lsm.addState(FrontlinePostBattleResultsState())
        lsm.addState(EditFrontlinePlaylistsState())

    def registerTransitions(self):
        lsm = self.getMachine()
        frontlineHangar = lsm.getStateByCls(FrontlineRootHangarState)
        allVehicle = lsm.getStateByCls(FrontlineAllVehiclesState)
        editFrontlinePlaylist = lsm.getStateByCls(EditFrontlinePlaylistsState)
        for cls in (FrontlineAllVehiclesState, ProgressionScreenState):
            state = lsm.getStateByCls(cls)
            frontlineHangar.addNavigationTransition(state)

        transitionCondition = WeakMethodProxy(self._hijackTransitionCondition)
        allVehicle.addTransition(HijackTransition(playlists.EditVehiclePlaylistsState, transitionCondition, record=True), editFrontlinePlaylist)
        parentTransitionList = [(HijackTransition(HangarState, transitionCondition), frontlineHangar), (HijackTransition(playlists.EditVehiclePlaylistsState, transitionCondition), editFrontlinePlaylist)]
        parent = self.getParent()
        for condition, transition in parentTransitionList:
            parent.addTransition(condition, transition)

        parentNavigationList = [frontlineHangar, lsm.getStateByCls(ProgressionScreenState), lsm.getStateByCls(FrontlinePostBattleResultsState)]
        for transition in parentNavigationList:
            parent.addNavigationTransition(transition)

    def _hijackTransitionCondition(self, _):
        return self.__epicController.isEnabled() and self.__epicController.isEpicPrbActive()


@FrontlineModeState.parentOf
class FrontlineHangarState(SFViewLobbyState):
    STATE_ID = FrontlineStateIDs.HANGAR
    VIEW_KEY = ViewKey(FrontlineHangarAliases.FRONTLINE_LOBBY_HANGAR)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FrontlineHangarState, self).__init__(flags | LobbyStateFlags.HANGAR)
        self.__hangarObserver = None
        return

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(FrontlineRootHangarState(flags=StateFlags.INITIAL))

    def __getView(self):
        app = self.__appLoader.getApp()
        view = app.containerManager.getViewByKey(self.getViewKey())
        return view.getParentWindow().content


@FrontlineHangarState.parentOf
class FrontlineRootHangarState(LobbyState):
    STATE_ID = FrontlineStateIDs.ROOT

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FrontlineRootHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)

    def _onEntered(self, event):
        super(FrontlineRootHangarState, self)._onEntered(event)
        lsm = self.getMachine()
        lsm.getRelatedView(self).blur.disable()


class _FlLoadoutConfirmStatePrototype(_LoadoutConfirmStatePrototype):
    STATE_ID = FrontlineStateIDs.LOADOUT_CONFIRM_LEAVE


@FrontlineHangarState.parentOf
class FrontlineAllVehiclesState(LobbyState):
    STATE_ID = FrontlineStateIDs.ALL_VEHICLES

    def _onEntered(self, event):
        super(FrontlineAllVehiclesState, self)._onEntered(event)
        lsm = self.getMachine()
        lsm.getRelatedView(self).blur.enable()

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.allVehicles()))


EditFrontlinePlaylistsState = playlists.generateVehiclePlayListClasses(parentStateCls=FrontlineHangarState, parentAllVehicleStateCls=FrontlineAllVehiclesState)

@FrontlineModeState.parentOf
class ProgressionScreenState(GuiImplViewLobbyState):
    STATE_ID = FrontlineStateIDs.PROGRESSION_SCREEN
    VIEW_KEY = ViewKey(R.views.frontline.mono.lobby.progression_screen())

    def __init__(self):
        super(ProgressionScreenState, self).__init__(ProgressionScreenView, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.fl_progression_screen.title()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, tooltipHeader=backport.text(R.strings.fl_tooltips.infoButton.header()), tooltipBody=backport.text(R.strings.fl_tooltips.infoButton.body()), onMoreInfoRequested=self.__openInfoView),))

    def __openInfoView(self):
        showFrontlineInfoWindow()


FrontlineLoadoutStateBase, _, FrontlineLoadoutSectionState, FrontlineShellsLoadoutState, _, _, _ = generateBasicLoadoutStateClasses(FrontlineHangarState, R.invalid, confirmStatePrototypeCls=_FlLoadoutConfirmStatePrototype)

class _BattleAbilitiesLoadoutStatePrototype(LobbyState):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.fl_battle_abilities_setup.header.title()), infos=(LobbyStateDescription.Info(tooltipHeader=backport.text(R.strings.fl_tooltips.infoButton.header()), tooltipBody=backport.text(R.strings.fl_tooltips.infoButton.body()), onMoreInfoRequested=self.__openInfoView),))

    @staticmethod
    def __openInfoView(*_):
        showFrontlineInfoWindow(autoscrollSection=InfoPageScrollToSection.BATTLE_SCENARIOS)


@FrontlineLoadoutStateBase.parentOf
class FrontlineBattleAbilitiesLoadoutState(FrontlineLoadoutSectionState, _BattleAbilitiesLoadoutStatePrototype):
    STATE_ID = _BattleAbilitiesLoadoutStatePrototype.STATE_ID or FrontlineStateIDs.BATTLE_ABILITIES


class FrontlineLoadoutState(FrontlineLoadoutStateBase):
    __loadoutController = dependency.descriptor(ILoadoutController)

    def registerStates(self):
        super(FrontlineLoadoutState, self).registerStates()
        lsm = self.getMachine()
        lsm.addState(FrontlineBattleAbilitiesLoadoutState())

    def _onExited(self):
        if not becomeNonPlayerState():
            super(FrontlineLoadoutState, self)._onExited()

    def registerTransitions(self):
        super(FrontlineLoadoutState, self).registerTransitions()
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)
        generatedClasses = [lsm.getStateByCls(FrontlineBattleAbilitiesLoadoutState)]
        parent = self.getParent()
        for state in generatedClasses:
            parent.addNavigationTransition(state)
            lsm.addNavigationTransitionFromParent(state, transitionType=TransitionType.EXTERNAL)
            state.addNavigationTransition(state, transitionType=TransitionType.EXTERNAL)


@FrontlineModeState.parentOf
class FrontlinePostBattleResultsState(SFViewLobbyState):
    STATE_ID = FrontlineStateIDs.BATTLE_RESULTS
    VIEW_KEY = ViewKey(FrontlineHangarAliases.FRONTLINE_BATTLE_RESULTS)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FrontlinePostBattleResultsState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.fl_post_battle_results.state.title()))

    def registerTransitions(self):
        lsm = self.getMachine()
        for child in self.getChildrenStates():
            lsm.addNavigationTransitionFromParent(child)
            child.addGuardTransition(child, self.__preventNavigationOutside)

    @classmethod
    def goTo(cls, arenaUniqueID):
        super(FrontlinePostBattleResultsState, cls).goTo(arenaUniqueID=arenaUniqueID)

    def _onEntered(self, event):
        lockNotificationManager(True, source=self.STATE_ID)
        self.__cachedParams = dict(event.params)
        super(FrontlinePostBattleResultsState, self)._onEntered(event)
        lockNotificationManager(False, source=self.STATE_ID, releasePostponed=True)

    def _onExited(self):
        super(FrontlinePostBattleResultsState, self)._onExited()
        self.__cachedParams = {}

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(_OverviewTab(StateFlags.INITIAL))
        lsm.addState(_TeamScoreTab())
        lsm.addState(_FinancialReportTab())

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def __preventNavigationOutside(self, event):
        from gui.Scaleform.daapi.view.lobby.battle_queue.states import BattleQueueContainerState
        prbDispatcher = self.prbDispatcher
        if prbDispatcher is None or not prbDispatcher.getFunctionalState().isNavigationDisabled():
            return False
        else:
            targetID = event.targetStateID
            lsm = self.getMachine()
            target = lsm.getStateByID(targetID)
            parentDescendants = self.getParent().getRecursiveChildrenStates()
            battleQueueDescendants = lsm.getStateByCls(BattleQueueContainerState).getRecursiveChildrenStates()
            eventTargetingOutside = target != self.getParent() and target not in parentDescendants and target not in battleQueueDescendants
            if eventTargetingOutside:
                SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')
            return eventTargetingOutside

    def getViewKey(self, params=None):
        arenaUniqueID = self.__cachedParams.get('arenaUniqueID', '')
        alias = super(FrontlinePostBattleResultsState, self).getViewKey().alias
        return ViewKey(alias, getViewName(alias, arenaUniqueID))

    def __getView(self):
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        view = app.containerManager.getViewByKey(self.getViewKey())
        return view.content

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params}


class PostBattleTab(LobbyState):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PostBattleTab, self).__init__(flags=flags)
        self.__cachedParams = None
        return

    def serializeParams(self):
        return self.__cachedParams

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.fl_post_battle_results.state.title()))

    def _onEntered(self, event):
        super(PostBattleTab, self)._onEntered(event)
        self.__cachedParams = event.params


@FrontlinePostBattleResultsState.parentOf
class _OverviewTab(PostBattleTab):
    STATE_ID = FrontlineStateIDs.OVERVIEW


@FrontlinePostBattleResultsState.parentOf
class _TeamScoreTab(PostBattleTab):
    STATE_ID = FrontlineStateIDs.TEAM_SCORE


@FrontlinePostBattleResultsState.parentOf
class _FinancialReportTab(PostBattleTab):
    STATE_ID = FrontlineStateIDs.FINANCIAL_REPORT
