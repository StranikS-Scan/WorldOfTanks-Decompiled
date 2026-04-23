# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/cgf_components/show_event_component.py
from __future__ import absolute_import
import CGF
from cgf_components.hover_component import SelectionComponent
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, registerRule, Rule, registerManager
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_sound_controller import ILSSoundController

@registerComponent
class LSShowEventComponent(object):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'LS Show Event Component'
    category = 'Last Stand'
    lsCtrl = dependency.descriptor(ILSController)
    lsSoundCtrl = dependency.descriptor(ILSSoundController)

    def showEvent(self):
        if self.lsCtrl.isAvailable():
            self.lsSoundCtrl.playSoundEvent('ev_last_stand_3d_main_enter')
            self.lsCtrl.selectBattle()


@registerComponent
class LSShowEventRewardComponent(object):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'LS Show Event Reward Component'
    category = 'Last Stand'


class LSShowEventComponentManager(CGF.ComponentManager, IGlobalListener):
    lsCtrl = dependency.descriptor(ILSController)

    def __init__(self):
        super(LSShowEventComponentManager, self).__init__()
        self._is3dPointVisible = None
        self._is3dPointRewardVisible = None
        self._allGOs = []
        self._rewardGoIDs = set()
        return

    def activate(self):
        self.lsCtrl.onSettingsUpdate += self._updateVisibility
        self._updateVisibility()

    def deactivate(self):
        self._allGOs = []
        self._rewardGoIDs.clear()
        if self.prbDispatcher and self.prbDispatcher.hasListener(self):
            self.stopGlobalListening()
        self.lsCtrl.onSettingsUpdate -= self._updateVisibility

    @onAddedQuery(CGF.GameObject, LSShowEventComponent)
    def onShowEventAdded(self, go, _):
        if self.prbDispatcher and not self.prbDispatcher.hasListener(self):
            self.startGlobalListening()
        if self.prbEntity is not None:
            self._updateGameObjectComponent(go)
        self._allGOs.append(go)
        return

    @onAddedQuery(LSShowEventComponent, SelectionComponent)
    def onSelectionAdded(self, showEventComponent, selectionComponent):
        selectionComponent.onClickAction += showEventComponent.showEvent

    @onAddedQuery(CGF.GameObject, LSShowEventRewardComponent)
    def onAddedRewardComponent(self, go, _):
        self._rewardGoIDs.add(go.id)

    @onRemovedQuery(LSShowEventComponent, SelectionComponent)
    def onSelectionRemoved(self, showEventComponent, selectionComponent):
        selectionComponent.onClickAction -= showEventComponent.showEvent

    def onPrbEntitySwitched(self):
        if self.prbEntity is None or not self.prbDispatcher or not self.prbDispatcher.hasListener(self):
            return
        else:
            eventGameObjectsQuery = CGF.Query(self.spaceID, (CGF.GameObject, LSShowEventComponent))
            for eventGameObject, _ in eventGameObjectsQuery:
                self._updateGameObjectComponent(eventGameObject)

            return

    def _updateGameObjectComponent(self, eventGameObject):
        if self.lsCtrl.isEventPrb():
            if eventGameObject.findComponentByType(SelectionComponent) is not None:
                eventGameObject.removeComponentByType(SelectionComponent)
        elif eventGameObject.findComponentByType(SelectionComponent) is None:
            eventGameObject.createComponent(SelectionComponent)
        return

    def _updateVisibility(self):
        config3dPointVisible = self.lsCtrl.isHangar3dPointVisible()
        config3dPointRewardVisible = self.lsCtrl.isHangar3dPointRewardVisible()
        if self._is3dPointVisible == config3dPointVisible and self._is3dPointRewardVisible == config3dPointRewardVisible:
            return
        for go in self._allGOs:
            if not go.isValid():
                continue
            if not config3dPointVisible or go.id in self._rewardGoIDs and not config3dPointRewardVisible:
                go.deactivate()
            go.activate()

        self._is3dPointVisible = config3dPointVisible
        self._is3dPointRewardVisible = config3dPointRewardVisible


@registerRule
class LSShowEventRule(Rule):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'LS Show Event Rule'
    category = 'Last Stand'

    @registerManager(LSShowEventComponentManager)
    def reg1(self):
        return None
