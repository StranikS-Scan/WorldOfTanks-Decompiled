# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/SMDistractionAbilityEntityComponent.py
import AnimationSequence
import BigWorld
import Math
from Event import Event
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from story_mode_common.story_mode_constants import DISTRACTION_ABILITY

class SMDistractionAbilityEntityComponent(DynamicScriptComponent):
    _SEQUENCE_RADIUS = 200.0
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    onSMDistractionAbilityActivated = Event()

    def __init__(self):
        super(SMDistractionAbilityEntityComponent, self).__init__()
        self._animator = None
        self._addEffect()
        return

    def set_spottedVehiclesIDs(self, _):
        spottedVehicles = [ BigWorld.entities.get(vID) for vID in self.spottedVehiclesIDs ]
        self.onSMDistractionAbilityActivated(spottedVehicles)

    def onDestroy(self):
        if self._animator is not None:
            self._animator.stop()
            self._animator = None
        super(SMDistractionAbilityEntityComponent, self).onDestroy()
        return

    def _addEffect(self):
        distractionItem = self.guiSessionProvider.shared.equipments.getEquipmentByName(DISTRACTION_ABILITY)
        itemDescriptor = distractionItem.getDescriptor()
        if itemDescriptor.detectSequence:
            entity = BigWorld.player().vehicle if itemDescriptor.detectFromVehicle else self.entity
            matrix = Math.Matrix()
            scale = itemDescriptor.directVisionRadius / self._SEQUENCE_RADIUS
            matrix.setScale(Math.Vector3(scale, scale, scale))
            matrix.translation = entity.position
            loader = AnimationSequence.Loader(itemDescriptor.detectSequence, entity.spaceID)
            animator = loader.loadSync()
            animator.bindToWorld(matrix)
            animator.speed = 1
            animator.loopCount = 1
            animator.start()
            self._animator = animator
