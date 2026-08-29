# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/group_repair/managers.py
import CGF
import BigWorld
from Sound import Sound3DComponent
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery, onRemovedQuery
from white_tiger.client_cgf.group_repair.components import WTRegenerationSoundComponent, WTRegenerationComponent
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import WtEquipmentSound
from white_tiger_common.common_cgf.cgf_helpers import registerWTManager
from events_core_common.events_core_cgf.helpers import getVehicleFromGO

@registerWTManager(CGF.DomainOption.DomainClient)
class WTGroupRepairRegenerationManager(CGF.ComponentManager):

    def __init__(self):
        super(WTGroupRepairRegenerationManager, self).__init__()
        self._isInterrupted = False

    @onAddedQuery(CGF.GameObject, WTRegenerationSoundComponent)
    def onRegenerationAdded(self, go, regenerationSound):
        player = BigWorld.player()
        vehicle = getVehicleFromGO(go, self.spaceID)
        if vehicle is None or player is None:
            return
        else:
            if vehicle.avatarID == player.id:
                go.createComponent(WTRegenerationComponent)
                self.__subscribe(vehicle)
            return

    @onRemovedQuery(CGF.GameObject, WTRegenerationComponent, WTRegenerationSoundComponent)
    def onRegenerationRemoved(self, go, _, regenerationSound):
        vehicle = getVehicleFromGO(go, self.spaceID)
        if vehicle is None:
            return
        else:
            if self._isInterrupted:
                WtEquipmentSound.playSound3D(regenerationSound.interruptEvent, vehicle.position)
            else:
                WtEquipmentSound.playSound3D(regenerationSound.completeEvent, vehicle.position)
            self.__unsubscribe(vehicle)
            self._isInterrupted = False
            return

    @onProcessQuery(CGF.GameObject, WTRegenerationComponent, WTRegenerationSoundComponent, period=1.0)
    def playImpulseSound(self, go, _, regenerationSound):
        self.__resetSound(go, regenerationSound.impulsEvent)

    def __subscribe(self, entity):
        ctrl = entity.guiSessionProvider.shared.feedback
        if ctrl is None:
            return
        else:
            ctrl.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
            return

    def __unsubscribe(self, entity):
        ctrl = entity.guiSessionProvider.shared.feedback
        if ctrl is None:
            return
        else:
            ctrl.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
            return

    def __resetSound(self, go, event):
        sound = go.findComponentByType(Sound3DComponent)
        if sound:
            go.removeComponent(sound)
        go.createComponent(Sound3DComponent, 'RegenerationSound', event, True)

    def __onPlayerFeedbackReceived(self, events):
        for e in events:
            if e.getType() == FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER:
                self._isInterrupted = True
                break
