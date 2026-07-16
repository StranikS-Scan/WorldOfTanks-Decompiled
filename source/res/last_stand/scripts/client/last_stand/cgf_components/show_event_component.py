# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/cgf_components/show_event_component.py
from __future__ import absolute_import
import CGF
from cgf_components.hover_component import SelectionComponent
from cgf_script.registration import registerComponent
from GenericComponents import DynamicModelComponent
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IHangarLoadingController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_sound_controller import ILSSoundController

@registerComponent
class LSShowEventComponent(object):
    domain = CGF.Domain.Client
    editorTitle = 'LS Show Event Component'
    group = 'Last Stand'
    lsCtrl = dependency.descriptor(ILSController)
    lsSoundCtrl = dependency.descriptor(ILSSoundController)

    def showEvent(self):
        if self.lsCtrl.isAvailable():
            self.lsSoundCtrl.playSoundEvent('ev_last_stand_3d_main_enter')
            self.lsCtrl.selectBattle()


@registerComponent
class LSShowEventRewardComponent(object):
    domain = CGF.Domain.Client
    editorTitle = 'LS Show Event Reward Component'
    group = 'Last Stand'


class LSShowEventSystem(CGF.System, IGlobalListener):
    lsCtrl = dependency.descriptor(ILSController)
    hangarLoadingController = dependency.descriptor(IHangarLoadingController)
    ShowEventModelsActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(LSShowEventComponent), CGF.ReactRo(DynamicModelComponent))
    ShowEventActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(LSShowEventComponent))
    ShowEventRewardActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(LSShowEventRewardComponent))
    SelectionActivated = CGF.ActivateReaction(CGF.ReactRw(SelectionComponent), CGF.Ro(LSShowEventComponent))
    SelectionDeactivated = CGF.DeactivateReaction(CGF.ReactRw(SelectionComponent), CGF.Rw(LSShowEventComponent))
    ShowEventIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Ro(LSShowEventComponent), CGF.Ro(DynamicModelComponent))
    SelectionAccess = CGF.AccessReaction(CGF.Ro(SelectionComponent))
    Reactions = CGF.Reactions(ShowEventModelsActivated, ShowEventActivated, ShowEventRewardActivated, SelectionActivated, SelectionDeactivated, ShowEventIterate, SelectionAccess)

    def __init__(self):
        super(LSShowEventSystem, self).__init__()
        self._is3dPointVisible = None
        self._is3dPointRewardVisible = None
        self._allGOs = []
        self._rewardGoIDs = set()
        return

    def update(self):
        for selectionComponent, showEventComponent in self.reaction(self.SelectionDeactivated):
            self.onSelectionRemoved(showEventComponent, selectionComponent)

        q = CGF.CommandQueue(self.gom)
        selectionAccess = self.reaction(self.SelectionAccess)
        for gameObject, _, _ in self.reaction(self.ShowEventModelsActivated):
            self.onShowEventAdded(gameObject, q, selectionAccess)

        for selectionComponent, showEventComponent in self.reaction(self.SelectionActivated):
            self.onSelectionAdded(showEventComponent, selectionComponent)

        for gameObject, _ in self.reaction(self.ShowEventRewardActivated):
            self.onAddedRewardComponent(gameObject)

        for gameObject, _ in self.reaction(self.ShowEventActivated):
            self._allGOs.append(gameObject)

    def onShowEventAdded(self, go, q, selectionAccess):
        if self.prbDispatcher and not self.prbDispatcher.hasListener(self):
            self.startGlobalListening()
        if self.prbEntity is not None:
            self._updateGameObjectComponent(go, q, selectionAccess)
        return

    def onSelectionAdded(self, showEventComponent, selectionComponent):
        selectionComponent.onClickAction += showEventComponent.showEvent

    def onAddedRewardComponent(self, go):
        self._rewardGoIDs.add(go.id)

    def onSelectionRemoved(self, showEventComponent, selectionComponent):
        selectionComponent.onClickAction -= showEventComponent.showEvent

    def onMappingLoaded(self):
        self.lsCtrl.onSettingsUpdate += self._onSettingsUpdate
        self.hangarLoadingController.onHangarLoadedAfterLogin += self._updateVisibility
        self._updateVisibility()

    def onMappingUnloaded(self):
        self._allGOs = []
        self._rewardGoIDs.clear()
        if self.prbDispatcher and self.prbDispatcher.hasListener(self):
            self.stopGlobalListening()
        self.lsCtrl.onSettingsUpdate -= self._onSettingsUpdate
        self.hangarLoadingController.onHangarLoadedAfterLogin -= self._updateVisibility

    def onPrbEntitySwitched(self):
        if self.prbEntity is None or not self.prbDispatcher or not self.prbDispatcher.hasListener(self):
            return
        else:
            q = CGF.CommandQueue(self.gom)
            selectionAccess = self.reaction(self.SelectionAccess)
            for eventGameObject, _, _ in self.reaction(self.ShowEventIterate):
                self._updateGameObjectComponent(eventGameObject, q, selectionAccess)

            return

    def _updateGameObjectComponent(self, eventGameObject, queue, selectionAccess):
        if self.lsCtrl.isEventPrb():
            if selectionAccess.find(eventGameObject) is not None:
                queue.removeComponent(eventGameObject, SelectionComponent)
        elif selectionAccess.find(eventGameObject) is None:
            queue.createComponent(eventGameObject, SelectionComponent)
        return

    def _onSettingsUpdate(self):
        config3dPointVisible = self.lsCtrl.isHangar3dPointVisible()
        config3dPointRewardVisible = self.lsCtrl.isHangar3dPointRewardVisible()
        if self._is3dPointVisible == config3dPointVisible and self._is3dPointRewardVisible == config3dPointRewardVisible:
            return
        self._updateVisibility()
        self._is3dPointVisible = config3dPointVisible
        self._is3dPointRewardVisible = config3dPointRewardVisible

    def _updateVisibility(self):
        config3dPointVisible = self.lsCtrl.isHangar3dPointVisible()
        config3dPointRewardVisible = self.lsCtrl.isHangar3dPointRewardVisible()
        queue = CGF.CommandQueue(self.gom)
        for go in self._allGOs:
            if not go.valid:
                continue
            if not config3dPointVisible or go.id in self._rewardGoIDs and not config3dPointRewardVisible:
                queue.deactivateGameObject(go)
            queue.activateGameObject(go)
