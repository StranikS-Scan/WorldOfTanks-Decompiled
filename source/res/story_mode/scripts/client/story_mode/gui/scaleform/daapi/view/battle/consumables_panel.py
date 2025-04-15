# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/consumables_panel.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from story_mode.gui.battle_control.controllers.equipments_items import SMStrategicAbilityItem
from story_mode_common.configs.story_mode_missions import missionsSchema
from story_mode_common.story_mode_constants import EQUIPMENT_STAGES as STAGES, MissionsDifficulty

class SMConsumablesPanel(ConsumablesPanel):

    def _getActiveItemGlowType(self, item):
        if isinstance(item, SMStrategicAbilityItem) and self._isNormalDifficultyMission() and item.getPrevStage() == STAGES.STARTUP_COOLDOWN and item.getStage() == STAGES.READY:
            glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_ESPECIAL_LARGE
        else:
            glowType = super(SMConsumablesPanel, self)._getActiveItemGlowType(item)
        return glowType

    def _isNormalDifficultyMission(self):
        currectMissionId = self.sessionProvider.arenaVisitor.extra.getValue('missionId')
        missionsModel = missionsSchema.getModel()
        if missionsModel is not None:
            for m in missionsModel.missions:
                if m.missionId == currectMissionId:
                    return m.difficulty in [MissionsDifficulty.UNDEFINED, MissionsDifficulty.NORMAL]

        return False
