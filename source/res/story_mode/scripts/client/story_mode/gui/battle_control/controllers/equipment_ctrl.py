# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/equipment_ctrl.py
import SoundGroups
from typing import Tuple, Optional, TYPE_CHECKING
from constants import ARENA_BONUS_TYPE
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentsReplayPlayer
from story_mode.gui.story_mode_gui_constants import ABILITY_ON_COOLDOWN_ACTIVATION_ERROR_KEY
from story_mode.gui.sound_constants import ABILITY_CANT_ACTIVATE_SOUND, ABILITY_ON_COOLDOWN_SOUND
from story_mode_common.story_mode_constants import RECON_ABILITY, EQUIPMENT_STAGES as STAGES
if TYPE_CHECKING:
    from Avatar import Avatar

class StoryModeEquipmentsController(equipment_ctrl.EquipmentsController):

    def _doChangeSetting(self, item, entityName=None, avatar=None):
        if avatar_getter.isPlayerOnArena(avatar):
            reconItem = self.getEquipmentByName(RECON_ABILITY)
            if reconItem:
                isReconAbility = reconItem.getEquipmentID() == item.getEquipmentID()
                if isReconAbility and reconItem.getStage() in (STAGES.PREPARING, STAGES.ACTIVE):
                    reconItem.deactivate()
                    return (True, None)
                if item.isAvatar() and reconItem.getStage() in (STAGES.ACTIVATING, STAGES.ACTIVE, STAGES.DEACTIVATING):
                    SoundGroups.g_instance.playSound2D(ABILITY_CANT_ACTIVATE_SOUND)
                    error = equipment_ctrl._ActivationError('ability_unable_other_ability', {'name': reconItem.getDescriptor().userString})
                    return (False, error)
        result, error = super(StoryModeEquipmentsController, self)._doChangeSetting(item, entityName, avatar)
        if error and error.key == ABILITY_ON_COOLDOWN_ACTIVATION_ERROR_KEY:
            SoundGroups.g_instance.playSound2D(ABILITY_ON_COOLDOWN_SOUND)
        return (result, error)


class StoryModeReplayEquipmentsController(EquipmentsReplayPlayer, StoryModeEquipmentsController):
    pass


def register():
    from gui.battle_control.controllers.consumables import extendEquipmentController
    extendEquipmentController({ARENA_BONUS_TYPE.STORY_MODE_REGULAR: StoryModeEquipmentsController}, {ARENA_BONUS_TYPE.STORY_MODE_REGULAR: StoryModeReplayEquipmentsController})
