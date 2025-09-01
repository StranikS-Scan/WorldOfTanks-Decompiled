# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/consumables_panel.py
from typing import TYPE_CHECKING
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from story_mode.gui.battle_control.controllers.equipments_items import DistractionAbilityItem, ReconAbilityItem
from story_mode_common.configs.story_mode_missions import missionsSchema
from story_mode_common.story_mode_constants import EQUIPMENT_STAGES as STAGES, MissionsDifficulty
if TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.equipment_ctrl import _EquipmentItem

class SMConsumablesPanel(ConsumablesPanel):

    def _getActiveItemGlowType(self, item):
        return CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_ESPECIAL_LARGE if isinstance(item, (DistractionAbilityItem, ReconAbilityItem)) and self._isNormalDifficultyMission() and item.getPrevStage() == STAGES.STARTUP_COOLDOWN and item.getStage() == STAGES.READY else CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_ESPECIAL

    def _isNormalDifficultyMission(self):
        currectMissionId = self.sessionProvider.arenaVisitor.extra.getValue('missionId')
        missionsModel = missionsSchema.getModel()
        if missionsModel is not None:
            for m in missionsModel.missions:
                if m.missionId == currectMissionId:
                    return m.difficulty in [MissionsDifficulty.UNDEFINED, MissionsDifficulty.NORMAL]

        return False

    def _updateEquipmentGlow(self, idx, item):
        if self._isAvatarEquipment(item):
            if item.getStage() != STAGES.PREPARING:
                if self._canApplyingGlowEquipment(item):
                    self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE)
                elif item.wasPreparationCanceled:
                    self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_ESPECIAL_NO_ANIM)
                elif item.becomeReady or item.alreadyReady:
                    self.as_setGlowS(idx, self._getActiveItemGlowType(item))
                elif item.getStage() == STAGES.ACTIVE:
                    self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_USAGE)
                elif item.isInCooldown():
                    self.as_hideGlowS(idx)
            else:
                self.as_hideGlowS(idx)
        else:
            super(SMConsumablesPanel, self)._updateEquipmentGlow(idx, item)
