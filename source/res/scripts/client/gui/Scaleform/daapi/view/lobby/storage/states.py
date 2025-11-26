# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/states.py
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_view import StorageView
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState, LobbyStateDescription
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

def registerStates(machine):
    machine.addState(StorageState())


def registerTransitions(machine):
    storage = machine.getStateByCls(StorageState)
    machine.addNavigationTransitionFromParent(storage)


@SubScopeSubLayerState.parentOf
class StorageState(SFViewLobbyState):
    STATE_ID = VIEW_ALIAS.LOBBY_STORAGE
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_STORAGE)
    __appLoader = dependency.descriptor(IAppLoader)

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub import OverviewState
        from gui.Scaleform.daapi.view.lobby.techtree.states import BlueprintState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(BlueprintState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState), record=True)

    def _getViewLoadCtx(self, event):
        return {'ctx': {'defaultSection': event.params.get('defaultSection', STORAGE_CONSTANTS.FOR_SELL),
                 'defaultTab': event.params.get('defaultTab', None)}}

    def serializeParams(self):
        storageView = self.__appLoader.getApp().containerManager.getViewByKey(self.getViewKey())
        section, tab = storageView.findActiveSectionAndTabId()
        return {'defaultSection': section,
         'defaultTab': tab}

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.depot()))
