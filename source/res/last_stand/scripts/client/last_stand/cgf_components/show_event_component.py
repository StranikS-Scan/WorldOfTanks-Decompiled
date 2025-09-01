# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/cgf_components/show_event_component.py
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


class LSShowEventComponentManager(CGF.ComponentManager, IGlobalListener):
    lsCtrl = dependency.descriptor(ILSController)

    @onAddedQuery(CGF.GameObject, LSShowEventComponent)
    def onShowEventAdded(self, gameObject, _):
        if self.prbDispatcher and not self.prbDispatcher.hasListener(self):
            self.startGlobalListening()
        if self.prbEntity is not None:
            self._updateGameObjectComponent(gameObject)
        return

    @onAddedQuery(LSShowEventComponent, SelectionComponent)
    def onSelectionAdded(self, showEventComponent, selectionComponent):
        selectionComponent.onClickAction += showEventComponent.showEvent

    @onRemovedQuery(LSShowEventComponent, SelectionComponent)
    def onSelectionRemoved(self, showEventComponent, selectionComponent):
        selectionComponent.onClickAction -= showEventComponent.showEvent

    def deactivate(self):
        if self.prbDispatcher and self.prbDispatcher.hasListener(self):
            self.stopGlobalListening()

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


@registerRule
class LSShowEventRule(Rule):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'LS Show Event Rule'
    category = 'Last Stand'

    @registerManager(LSShowEventComponentManager)
    def reg1(self):
        return None
