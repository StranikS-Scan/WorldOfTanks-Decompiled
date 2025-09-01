# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/states.py
import typing
from WeakMethod import WeakMethodProxy
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl import backport
from gui.impl.lobby.dog_tags.animated_dog_tags_view import AnimatedDogTagsView
from gui.impl.lobby.dog_tags.dog_tags_view import DogTagsView
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SubScopeTopLayerState, LobbyStateDescription, LobbyState, TopScopeTopLayerState, SubScopeSubLayerState
from gui.impl.gen import R
from gui.shared.event_dispatcher import showDogTagCustomizationConfirmDialog
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from wg_async import wg_async, wg_await
from account_helpers.dog_tags import DogTags as DogTagsAccountHelper

def registerStates(machine):
    machine.addState(DogTagState())
    machine.addState(AnimatedDogTagState())


def registerTransitions(machine):
    dogTags = machine.getStateByCls(DogTagState)
    machine.addNavigationTransitionFromParent(dogTags)
    animatedDogTags = machine.getStateByCls(AnimatedDogTagState)
    machine.addNavigationTransitionFromParent(animatedDogTags)


@TopScopeTopLayerState.parentOf
class DogTagConfirmState(LobbyState):
    STATE_ID = 'dogTagConfirmLeave'

    def getNavigationDescription(self):
        return None

    @wg_async
    def _onEntered(self, event):
        lsm = getLobbyStateMachine()
        dogTagState = lsm.getStateByCls(DogTagState)
        result = yield wg_await(showDogTagCustomizationConfirmDialog(dogTagState.selectedBackground, dogTagState.selectedEngraving))
        proceed, resultData = result.result
        if not proceed:
            TopScopeTopLayerState.goTo()
        elif resultData.get('saveChanges'):
            self.__equipDogTag(dogTagState.selectedBackground, dogTagState.selectedEngraving)
            self.getMachine().post(event)
        else:
            self.getMachine().post(event)

    @staticmethod
    def __equipDogTag(selectedBackground, selectedEngraving):
        DogTagsAccountHelper.equipDT(selectedBackground, selectedEngraving)


@SubScopeTopLayerState.parentOf
class DogTagState(GuiImplViewLobbyState):
    STATE_ID = 'dogTags'
    VIEW_KEY = ViewKey(R.views.lobby.dog_tags.DogTagsView())
    __uiLoader = dependency.instance(IGuiLoader)

    def __init__(self):
        super(DogTagState, self).__init__(DogTagsView, ScopeTemplates.LOBBY_SUB_SCOPE)

    @property
    def selectedBackground(self):
        view = self.getMachine().getRelatedView(self)
        return view.selectedBackground if view is not None else None

    @property
    def selectedEngraving(self):
        view = self.getMachine().getRelatedView(self)
        return view.selectedEngraving if view is not None else None

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(DogTagConfirmState())

    def registerTransitions(self):
        lsm = self.getMachine()
        subScopeSubLayer = lsm.getStateByCls(SubScopeSubLayerState)
        subScopeSubLayer.addGuardTransition(lsm.getStateByCls(DogTagConfirmState), WeakMethodProxy(self._dogTagConfirm))
        self.addGuardTransition(lsm.getStateByCls(DogTagConfirmState), WeakMethodProxy(self._dogTagConfirm))
        self.addNavigationTransition(self, TransitionType.EXTERNAL)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.dog_tags()))

    def _getViewLoadCtx(self, event):
        return {'highlightedComponentId': event.params.get('highlightedComponentId', -1),
         'makeTopView': event.params.get('makeTopView', True)}

    def _dogTagConfirm(self, event):
        dogTagsEntered = self.isEntered()
        confirmationEntered = self.getMachine().isStateEntered(DogTagConfirmState.STATE_ID)
        dogTagSelected = self.selectedEngraving or self.selectedBackground
        if event.targetStateID == self.STATE_ID or confirmationEntered or not dogTagsEntered or not dogTagSelected:
            return False
        view = self.getMachine().getRelatedView(self)
        if not view:
            return False
        currentEngraving, currentBackground = view.getCurrentDogTag()
        return not (currentBackground == self.selectedBackground and currentEngraving == self.selectedEngraving)


@SubScopeTopLayerState.parentOf
class AnimatedDogTagState(GuiImplViewLobbyState):
    STATE_ID = 'animatedDogTags'
    VIEW_KEY = ViewKey(R.views.lobby.dog_tags.AnimatedDogTagsView())

    def __init__(self):
        super(AnimatedDogTagState, self).__init__(AnimatedDogTagsView, ScopeTemplates.LOBBY_SUB_SCOPE)

    def _getViewLoadCtx(self, event):
        return {'initBackgroundId': event.params.get('initBackgroundId', None),
         'initEngravingId': event.params.get('initEngravingId', None)}

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.animated_dog_tags()))
