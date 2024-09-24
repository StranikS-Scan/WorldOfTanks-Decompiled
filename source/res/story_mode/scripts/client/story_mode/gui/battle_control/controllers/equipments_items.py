# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/equipments_items.py
import typing
import SoundGroups
from AvatarInputHandler import MapCaseMode
from constants import EQUIPMENT_STAGES
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.shared.system_factory import registerEquipmentItem
_SMN_ARCADE_ARTILLERY_ITEMS = ('arcade_artillery_smn_battleship_lvl1', 'arcade_artillery_smn_battleship_lvl1_hard', 'arcade_artillery_smn_battleship_lvl2', 'arcade_artillery_smn_battleship_lvl2_hard', 'arcade_artillery_smn_battleship_lvl3', 'arcade_artillery_smn_battleship_lvl3_hard')
_SMN_ARCADE_ARTILLERY_DESTROYER_ITEMS = {'arcade_artillery_smn_destroyer', 'arcade_artillery_smn_destroyer_hard'}
_SMN_ARCADE_ARTILLERY_ACTIVATE_SOUND = 'sm_gp_dday_ability_active'
_SMN_ARCADE_ARTILLERY_DEACTIVATE_SOUND = 'sm_gp_dday_ability_deactive'
_SMN_ARCADE_ARTILLERY_SET_SOUND = 'sm_gp_dday_ability_set'
_SMN_ARCADE_ARTILLERY_STATE_GROUP = 'STATE_BR_death_zone_red'
_SMN_ARCADE_ARTILLERY_STATE_IN = 'STATE_BR_death_zone_red_in'
_SMN_ARCADE_ARTILLERY_STATE_OUT = 'STATE_BR_death_zone_red_out'
_SMN_ARCADE_ARTILLERY_DESTROYER_SOUND = 'eb_ability_inspiration_apply'
_EQUIPMENT_STAGE_DESTROYER_SHOOTING = -1

class _SmnRefillEquipmentItem(equipment_ctrl._RefillEquipmentItem):

    def __init__(self, *args, **kwargs):
        self._mapCaseModeActive = False
        super(_SmnRefillEquipmentItem, self).__init__(*args, **kwargs)

    def getAimingControlMode(self):
        return MapCaseMode.AracdeMinefieldControleMode

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_SmnRefillEquipmentItem, self).update(quantity, stage, timeRemaining, totalTime)
        if self._mapCaseModeActive:
            if stage == EQUIPMENT_STAGES.COOLDOWN:
                SoundGroups.g_instance.playSound2D(_SMN_ARCADE_ARTILLERY_SET_SOUND)
            SoundGroups.g_instance.playSound2D(_SMN_ARCADE_ARTILLERY_DEACTIVATE_SOUND)
            SoundGroups.g_instance.setState(_SMN_ARCADE_ARTILLERY_STATE_GROUP, _SMN_ARCADE_ARTILLERY_STATE_OUT)
            self._mapCaseModeActive = False
        elif stage == EQUIPMENT_STAGES.PREPARING:
            SoundGroups.g_instance.playSound2D(_SMN_ARCADE_ARTILLERY_ACTIVATE_SOUND)
            SoundGroups.g_instance.setState(_SMN_ARCADE_ARTILLERY_STATE_GROUP, _SMN_ARCADE_ARTILLERY_STATE_IN)
            self._mapCaseModeActive = True


class _SmnArcadeArtilleryItem(_SmnRefillEquipmentItem, equipment_ctrl._ArcadeArtilleryItem):
    pass


class _SmnReplayArcadeArtilleryItem(_SmnRefillEquipmentItem, equipment_ctrl._ReplayArcadeArtilleryItem):
    pass


class _SmnArcadeArtilleryBaseItem(object):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_SmnArcadeArtilleryBaseItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == _EQUIPMENT_STAGE_DESTROYER_SHOOTING:
            SoundGroups.g_instance.playSound2D(_SMN_ARCADE_ARTILLERY_DESTROYER_SOUND)


class _SmnArcadeArtilleryDestroyerItem(_SmnArcadeArtilleryBaseItem, equipment_ctrl._ArcadeArtilleryItem):
    pass


class _SmnReplayArcadeArtilleryDestroyerItem(_SmnArcadeArtilleryBaseItem, equipment_ctrl._ReplayArcadeArtilleryItem):
    pass


def register():
    for name in _SMN_ARCADE_ARTILLERY_ITEMS:
        registerEquipmentItem(name, _SmnArcadeArtilleryItem, _SmnReplayArcadeArtilleryItem)

    for name in _SMN_ARCADE_ARTILLERY_DESTROYER_ITEMS:
        registerEquipmentItem(name, _SmnArcadeArtilleryDestroyerItem, _SmnReplayArcadeArtilleryDestroyerItem)
