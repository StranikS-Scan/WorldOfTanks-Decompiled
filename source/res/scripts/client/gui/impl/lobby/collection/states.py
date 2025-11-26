# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collection/states.py
from typing import Optional
from frameworks.wulf import ViewStatus
from gui.shared.event_dispatcher import showHangar
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.lobby_state_machine.states import StateFlags, SFViewLobbyState, SubScopeSubLayerState
from helpers import dependency
from skeletons.gui.game_control import ICollectionsSystemController

def registerStates(machine):
    machine.addState(CollectionState())


def registerTransitions(machine):
    collection = machine.getStateByCls(CollectionState)
    machine.addNavigationTransitionFromParent(collection)


@SubScopeSubLayerState.parentOf
class CollectionState(SFViewLobbyState):
    STATE_ID = VIEW_ALIAS.COLLECTIONS_PAGE
    VIEW_KEY = ViewKey(VIEW_ALIAS.COLLECTIONS_PAGE)
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(CollectionState, self).__init__(flags)
        self.__cachedParams = {}

    @classmethod
    def goTo(cls, collectionId, page):
        super(CollectionState, cls).goTo(ctx={'collectionId': collectionId,
         'page': page})

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState), record=True)

    def serializeParams(self):
        view = self.getMachine().getRelatedView(self)
        ctx = self.__cachedParams['ctx']
        if view and view.viewStatus == ViewStatus.LOADED:
            ctx.update(view.getContext())
        return {'ctx': ctx}

    def _onEntered(self, event):
        super(CollectionState, self)._onEntered(event)
        if not self.__collectionsSystem.isEnabled():
            showHangar()
            return
        self.__cachedParams = event.params
