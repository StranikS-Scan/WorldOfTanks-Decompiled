# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/cgf_components/show_event_component.py
from __future__ import absolute_import
import CGF
from cgf_components.hover_component import SelectionComponent
from cgf_script.registration import registerComponent, registerModule
from gui.prb_control.entities.listener import IGlobalListener
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.skeletons.halloween_sound_controller import IHalloweenSoundController
from halloween.uilogging.logging_constants import HWLogKeys
from helpers import dependency

@registerComponent
class HWShowEventComponent(object):
    domain = CGF.Domain.Client
    editorTitle = 'HW Show Event Component'
    group = 'Halloween'
    halloweenCtrl = dependency.descriptor(IHalloweenController)
    hwSoundCtrl = dependency.descriptor(IHalloweenSoundController)

    def showEvent(self):
        if self.halloweenCtrl.isAvailable():
            self.hwSoundCtrl.playSoundEvent('ev_hw_main_3D_enter')
            self.halloweenCtrl.selectBattle(source=HWLogKeys.HANGAR_3D_OBJECT)


class HWShowEventSystem(CGF.System, IGlobalListener):
    halloweenCtrl = dependency.descriptor(IHalloweenController)
    ShowEventActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(HWShowEventComponent))
    SelectionActivated = CGF.ActivateReaction(CGF.ReactRw(SelectionComponent), CGF.Ro(HWShowEventComponent))
    ShowEventDeactivated = CGF.DeactivateReaction(CGF.ReactRo(HWShowEventComponent))
    SelectionDeactivated = CGF.DeactivateReaction(CGF.ReactRw(SelectionComponent), CGF.Rw(HWShowEventComponent))
    ShowEventIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Ro(HWShowEventComponent))
    SelectionAccess = CGF.AccessReaction(CGF.Ro(SelectionComponent))
    Reactions = CGF.Reactions(ShowEventActivated, SelectionActivated, ShowEventDeactivated, SelectionDeactivated, ShowEventIterate, SelectionAccess)

    def update(self):
        showEventIterate = self.reaction(self.ShowEventIterate)
        for _ in self.reaction(self.ShowEventDeactivated):
            self.onShowEventRemoved(showEventIterate)

        for selectionComponent, showEventComponent in self.reaction(self.SelectionDeactivated):
            self.onSelectionRemoved(showEventComponent, selectionComponent)

        q = CGF.CommandQueue(self.gom)
        selectionAccess = self.reaction(self.SelectionAccess)
        for gameObject, _ in self.reaction(self.ShowEventActivated):
            self.onShowEventAdded(gameObject, q, selectionAccess)

        for selectionComponent, showEventComponent in self.reaction(self.SelectionActivated):
            self.onSelectionAdded(showEventComponent, selectionComponent)

    def onShowEventAdded(self, gameObject, queue, selectionAccess):
        if self.prbDispatcher and not self.prbDispatcher.hasListener(self):
            self.startGlobalListening()
        if self.prbEntity is not None:
            self._updateGameObjectComponent(gameObject, queue, selectionAccess)
        return

    def onShowEventRemoved(self, showEventIterate):
        if self.prbDispatcher and self.prbDispatcher.hasListener(self):
            hasEntries = False
            for _, _ in showEventIterate:
                hasEntries = True
                break

            if not hasEntries:
                self.stopGlobalListening()

    def onSelectionAdded(self, showEventComponent, selectionComponent):
        selectionComponent.onClickAction += showEventComponent.showEvent

    def onSelectionRemoved(self, showEventComponent, selectionComponent):
        selectionComponent.onClickAction -= showEventComponent.showEvent

    def onPrbEntitySwitched(self):
        if self.prbEntity is None or not self.prbDispatcher or not self.prbDispatcher.hasListener(self):
            return
        else:
            q = CGF.CommandQueue(self.gom)
            selectionAccess = self.reaction(self.SelectionAccess)
            for eventGameObject, _ in self.reaction(self.ShowEventIterate):
                self._updateGameObjectComponent(eventGameObject, q, selectionAccess)

            return

    def _updateGameObjectComponent(self, eventGameObject, queue, selectionAccess):
        if self.halloweenCtrl.isEventPrb():
            if selectionAccess.find(eventGameObject) is not None:
                queue.removeComponent(eventGameObject, SelectionComponent)
        elif selectionAccess.find(eventGameObject) is None:
            queue.createComponent(eventGameObject, SelectionComponent)
        return


@registerModule
class HWShowEventModule(object):
    domain = CGF.Domain.Client
    editorTitle = 'HW Show Event Module'
    group = 'Halloween'
    systems = [CGF.RegisterSystem(HWShowEventSystem, domain=CGF.Domain.Client)]
    components = [HWShowEventComponent]
