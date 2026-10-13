# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/cgf/show_event_component.py
from __future__ import absolute_import
import CGF
from cgf_components.hover_component import SelectionComponent
from cgf_script.registration import registerComponent, registerModule
from fort_rush.gui.sounds import play2DSound
from fort_rush.gui.sounds.sound_constants import HangarSounds
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from fort_rush_common.configs.fort_rush_battles_config import fortRushBattlesConfigGameParamsSchema
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from PlayerEvents import g_playerEvents

@registerComponent
class FortRushShowEventComponent(object):
    domain = CGF.Domain.Client
    editorTitle = 'Fort Rush Show Event Component'
    group = 'Fort Rush'
    _fortRushCtrl = dependency.descriptor(IFortRushBattleController)

    def showEvent(self):
        if self._fortRushCtrl.isAvailable():
            play2DSound(HangarSounds.ENTRY_POINT_CLICK)
            self._fortRushCtrl.selectBattle()


class FortRushShowEventSystem(CGF.System, IGlobalListener):
    _fortRushCtrl = dependency.descriptor(IFortRushBattleController)
    ShowEventActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(FortRushShowEventComponent))
    SelectionActivated = CGF.ActivateReaction(CGF.ReactRw(SelectionComponent), CGF.Ro(FortRushShowEventComponent))
    SelectionDeactivated = CGF.DeactivateReaction(CGF.ReactRw(SelectionComponent), CGF.Rw(FortRushShowEventComponent))
    ShowEventIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Ro(FortRushShowEventComponent))
    SelectionAccess = CGF.AccessReaction(CGF.Ro(SelectionComponent))
    Reactions = CGF.Reactions(ShowEventActivated, SelectionActivated, SelectionDeactivated, ShowEventIterate, SelectionAccess)

    def __init__(self):
        super(FortRushShowEventSystem, self).__init__()
        self._allGOs = []

    def update(self):
        for selectionComponent, showEventComponent in self.reaction(self.SelectionDeactivated):
            self.onSelectionRemoved(showEventComponent, selectionComponent)

        q = CGF.CommandQueue(self.gom)
        selectionAccess = self.reaction(self.SelectionAccess)
        for gameObject, _ in self.reaction(self.ShowEventActivated):
            self._allGOs.append(gameObject)
            self.onShowEventAdded(gameObject, q, selectionAccess)

        for selectionComponent, showEventComponent in self.reaction(self.SelectionActivated):
            self.onSelectionAdded(showEventComponent, selectionComponent)

    def onMappingLoaded(self):
        g_playerEvents.onConfigModelUpdated += self.__onConfigModelUpdated

    def onMappingUnloaded(self):
        self._allGOs = []
        if self.prbDispatcher and self.prbDispatcher.hasListener(self):
            self.stopGlobalListening()
        g_playerEvents.onConfigModelUpdated -= self.__onConfigModelUpdated

    def onShowEventAdded(self, gameObject, queue, selectionAccess):
        if self.prbDispatcher and not self.prbDispatcher.hasListener(self):
            self.startGlobalListening()
        if not self._fortRushCtrl.isAvailable():
            queue.deactivateGameObject(gameObject)
            return
        else:
            if self.prbEntity is not None:
                self._updateGameObjectComponent(gameObject, queue, selectionAccess)
            return

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

    def __onConfigModelUpdated(self, gpKey):
        if fortRushBattlesConfigGameParamsSchema.gpKey == gpKey:
            self._updateVisibility()

    def _updateVisibility(self):
        isAvailable = self._fortRushCtrl.isAvailable()
        queue = CGF.CommandQueue(self.gom)
        for go in self._allGOs:
            if not go.valid:
                continue
            if isAvailable:
                queue.activateGameObject(go)
            queue.deactivateGameObject(go)

    def _updateGameObjectComponent(self, eventGameObject, queue, selectionAccess):
        if self._fortRushCtrl.isEventPrbActive():
            if selectionAccess.find(eventGameObject) is not None:
                queue.removeComponent(eventGameObject, SelectionComponent)
        elif selectionAccess.find(eventGameObject) is None:
            queue.createComponent(eventGameObject, SelectionComponent)
        return


@registerModule
class FortRushShowEventModule(object):
    domain = CGF.Domain.Client
    editorTitle = 'Fort Rush Show Event Module'
    group = 'Fort Rush Hangar'
    systems = [CGF.RegisterSystem(FortRushShowEventSystem, domain=CGF.Domain.Client)]
    components = [FortRushShowEventComponent]
