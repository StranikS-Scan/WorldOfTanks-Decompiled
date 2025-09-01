# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/states.py
import typing
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.lobby.crew.barracks_view import BarracksView
from gui.impl.lobby.crew.container_vews.quick_training.quick_training_view import QuickTrainingView
from gui.impl.lobby.crew.member_change_view import MemberChangeView
from gui.impl.lobby.crew.tank_change_view import TankChangeView
from gui.impl.lobby.crew.tankman_container_view import TankmanContainerView
from gui.lobby_state_machine.events import _BackNavigationGeneratedNavigationEvent
from gui.lobby_state_machine.states import GuiImplViewLobbyState, LobbyStateDescription, SubScopeSubLayerState, SubScopeTopLayerState
from gui.impl.gen import R
from gui.shared.event_dispatcher import showCrewAboutView
from gui.shared.gui_items.Tankman import NO_SLOT, NO_TANKMAN
from helpers import dependency
from skeletons.gui.game_control import ICrewController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache

def registerStates(machine):
    machine.addState(BarracksState())
    machine.addState(PersonalCaseState())
    machine.addState(MemberChangeState())
    machine.addState(TankChangeState())
    machine.addState(QuickTrainingState())
    machine.addHistoryRemovableStateSelector(machine.getStateByCls(PersonalCaseState).canBeRemovedFromHistory)
    machine.addHistoryRemovableStateSelector(machine.getStateByCls(TankChangeState).canBeRemovedFromHistory)
    machine.addHistoryRemovableStateSelector(machine.getStateByCls(QuickTrainingState).canBeRemovedFromHistory)


def registerTransitions(_):
    pass


class _RemovableFromHistoryMixin(object):

    def canBeRemovedFromHistory(self, state, params):
        if state is not self:
            return False
        else:
            tankmanInvID = params.get('tankmanInvID', None)
            if not tankmanInvID:
                return False
            itemsCache = dependency.instance(IItemsCache)
            tankman = itemsCache.items.getTankman(tankmanInvID)
            return tankman is None


@SubScopeSubLayerState.parentOf
class BarracksState(GuiImplViewLobbyState):
    STATE_ID = 'barracks'
    VIEW_KEY = ViewKey(R.views.lobby.crew.BarracksView())

    def __init__(self):
        super(BarracksState, self).__init__(BarracksView, ScopeTemplates.LOBBY_SUB_SCOPE)

    def registerTransitions(self):
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.barracks()))


@SubScopeTopLayerState.parentOf
class PersonalCaseState(GuiImplViewLobbyState, _RemovableFromHistoryMixin):
    __crewController = dependency.descriptor(ICrewController)
    STATE_ID = 'personalCase'
    VIEW_KEY = ViewKey(R.views.lobby.crew.TankmanContainerView())

    def __init__(self):
        super(PersonalCaseState, self).__init__(TankmanContainerView, ScopeTemplates.LOBBY_SUB_SCOPE)
        self.__cachedParams = {}

    def registerTransitions(self):
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.crewPersonalCase()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showCrewAboutView),))

    def serializeParams(self):
        return self.__cachedParams

    def compareParams(self, params, otherParams):
        return True

    def _onEntered(self, event):
        self.__cachedParams = event.params
        isTransitioningByBackNavigation = isinstance(event, _BackNavigationGeneratedNavigationEvent)
        if isTransitioningByBackNavigation:
            uiLoader = dependency.instance(IGuiLoader)
            view = uiLoader.windowsManager.getViewByLayoutID(self.VIEW_KEY.alias)
            _, tankmanInvID = self.__crewController.getWidgetData()
            if view is None and tankmanInvID == NO_TANKMAN:
                self.goBack()
                return
        super(PersonalCaseState, self)._onEntered(event)
        return

    def _onExited(self):
        super(PersonalCaseState, self)._onExited()
        self.__crewController.setWidgetData(self.VIEW_KEY.alias)
        self.__cachedParams = {}

    def _focusView(self, view, event):
        super(PersonalCaseState, self)._focusView(view, event)
        tankmanInvID = event.params.get('tankmanInvID')
        isTransitioningByBackNavigation = isinstance(event, _BackNavigationGeneratedNavigationEvent)
        if tankmanInvID:
            if not isTransitioningByBackNavigation:
                view.updateTankmanId(tankmanInvID)
            else:
                _, tankmanInvID = self.__crewController.getWidgetData()
                self.__cachedParams['tankmanInvID'] = tankmanInvID
                view.widgetAutoSelectSlot(tankmanInvId=tankmanInvID)
        tabId = event.params.get('currentViewID')
        if tabId:
            view.updateTabId(tabId)


@SubScopeTopLayerState.parentOf
class TankChangeState(GuiImplViewLobbyState, _RemovableFromHistoryMixin):
    __crewController = dependency.descriptor(ICrewController)
    STATE_ID = 'tankChange'
    VIEW_KEY = ViewKey(R.views.lobby.crew.TankChangeView())

    def __init__(self):
        super(TankChangeState, self).__init__(TankChangeView, ScopeTemplates.LOBBY_SUB_SCOPE)
        self.__cachedParams = {}

    def registerTransitions(self):
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.crewTankChange()))

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(TankChangeState, self)._onEntered(event)

    def _onExited(self):
        super(TankChangeState, self)._onExited()
        self.__crewController.setWidgetData(self.VIEW_KEY.alias)
        self.__cachedParams = {}

    def _focusView(self, view, event):
        tankmanInvID = event.params.get('tankmanInvID')
        slotIDX = event.params.get('slotIDX')
        isTransitioningByBackNavigation = isinstance(event, _BackNavigationGeneratedNavigationEvent)
        if tankmanInvID and slotIDX:
            if isTransitioningByBackNavigation:
                slotIDX, tankmanInvID = self.__crewController.getWidgetData()
                self.__cachedParams['slotIDX'] = slotIDX
                self.__cachedParams['tankmanInvID'] = tankmanInvID
            view.widgetAutoSelectSlot(tankmanInvId=tankmanInvID, slotIDX=slotIDX)
        super(TankChangeState, self)._focusView(view, event)


@SubScopeTopLayerState.parentOf
class MemberChangeState(GuiImplViewLobbyState):
    __crewController = dependency.descriptor(ICrewController)
    STATE_ID = 'memberChange'
    VIEW_KEY = ViewKey(R.views.lobby.crew.MemberChangeView())

    def __init__(self):
        super(MemberChangeState, self).__init__(MemberChangeView, ScopeTemplates.LOBBY_SUB_SCOPE)
        self.__cachedParams = {}

    def registerTransitions(self):
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.crewMemberChange()))

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(MemberChangeState, self)._onEntered(event)

    def _onExited(self):
        super(MemberChangeState, self)._onExited()
        self.__crewController.setWidgetData(self.VIEW_KEY.alias)
        self.__cachedParams = {}

    def _focusView(self, view, event):
        slotIdx = event.params.get('slotIdx')
        isTransitioningByBackNavigation = isinstance(event, _BackNavigationGeneratedNavigationEvent)
        if slotIdx != NO_SLOT:
            if isTransitioningByBackNavigation:
                slotIdx, _ = self.__crewController.getWidgetData()
                self.__cachedParams['slotIdx'] = slotIdx
            view.selectSlot(slotIdx)
        super(MemberChangeState, self)._focusView(view, event)


@SubScopeTopLayerState.parentOf
class QuickTrainingState(GuiImplViewLobbyState, _RemovableFromHistoryMixin):
    __crewController = dependency.descriptor(ICrewController)
    STATE_ID = 'quickTraining'
    VIEW_KEY = ViewKey(R.views.lobby.crew.QuickTrainingView())

    def __init__(self):
        super(QuickTrainingState, self).__init__(QuickTrainingView, ScopeTemplates.LOBBY_SUB_SCOPE)
        self.__cachedParams = {}

    def registerTransitions(self):
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.crewQuickTraining()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showCrewAboutView),))

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(QuickTrainingState, self)._onEntered(event)

    def _onExited(self):
        super(QuickTrainingState, self)._onExited()
        self.__crewController.setWidgetData(self.VIEW_KEY.alias)
        self.__cachedParams = {}

    def compareParams(self, params, otherParams):
        return True

    def _focusView(self, view, event):
        super(QuickTrainingState, self)._focusView(view, event)
        tankmanInvId = event.params.get('tankmanInvID')
        isTransitioningByBackNavigation = isinstance(event, _BackNavigationGeneratedNavigationEvent)
        if tankmanInvId:
            if isTransitioningByBackNavigation:
                _, tankmanInvId = self.__crewController.getWidgetData()
                self.__cachedParams['tankmanInvID'] = tankmanInvId
            view.widgetAutoSelectSlot(tankmanInvId=tankmanInvId, slotIDX=NO_SLOT if tankmanInvId != NO_TANKMAN else 0)
