# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/states.py
from __future__ import absolute_import
import typing
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_view import StorageView
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.lobby_state_machine.states import SubScopeSubLayerState, LobbyStateDescription, ViewLobbyState
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

def registerStates(machine):
    machine.addState(StorageState())
    machine.addState(OfferGiftsState())


def registerTransitions(machine):
    storage = machine.getStateByCls(StorageState)
    machine.addNavigationTransitionFromParent(storage)


@SubScopeSubLayerState.parentOf
class StorageState(ViewLobbyState):
    STATE_ID = VIEW_ALIAS.LOBBY_STORAGE
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_STORAGE)
    __appLoader = dependency.descriptor(IAppLoader)

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub import OverviewState
        from gui.impl.lobby.blueprints.states import BlueprintState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(BlueprintState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(OfferGiftsState), record=True)

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


@SubScopeSubLayerState.parentOf
class OfferGiftsState(ViewLobbyState):
    STATE_ID = VIEW_ALIAS.OFFER_GIFT_VIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.OFFER_GIFT_VIEW)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(OfferGiftsState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import OfferGiftVehiclePreviewState
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)
        self.addNavigationTransition(lsm.getStateByCls(OfferGiftVehiclePreviewState), record=True)

    def serializeParams(self):
        return self.__cachedParams

    @classmethod
    def goTo(cls, offerID=None, overrideSuccessCallback=None, overrideOnBackCallback=None):
        super(OfferGiftsState, cls).goTo(offerID=offerID, overrideSuccessCallback=overrideSuccessCallback, overrideOnBackCallback=overrideOnBackCallback)

    def _onEntered(self, event):
        super(OfferGiftsState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        super(OfferGiftsState, self)._onExited()
        self.__cachedParams = {}

    def _getViewLoadCtx(self, event):
        return {'offerID': event.params.get('offerID', None),
         'overrideSuccessCallback': event.params.get('overrideSuccessCallback', None),
         'overrideOnBackCallback': event.params.get('overrideOnBackCallback', None)}
