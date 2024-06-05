# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/equipments_items.py
import typing
from AvatarInputHandler import MapCaseMode
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.shared.system_factory import registerEquipmentItem
_SMN_ARCADE_ARTILLERY_ITEMS = ('arcade_artillery_smn_battleship_lvl1', 'arcade_artillery_smn_battleship_lvl1_hard', 'arcade_artillery_smn_battleship_lvl2', 'arcade_artillery_smn_battleship_lvl2_hard', 'arcade_artillery_smn_battleship_lvl3', 'arcade_artillery_smn_battleship_lvl3_hard')

class _SmnArcadeArtilleryItem(equipment_ctrl._ArcadeArtilleryItem):

    def getAimingControlMode(self):
        return MapCaseMode.AracdeMinefieldControleMode


class _SmnReplayArcadeArtilleryItem(equipment_ctrl._ReplayArcadeArtilleryItem):

    def getAimingControlMode(self):
        return MapCaseMode.AracdeMinefieldControleMode


def register():
    for name in _SMN_ARCADE_ARTILLERY_ITEMS:
        registerEquipmentItem(name, _SmnArcadeArtilleryItem, _SmnReplayArcadeArtilleryItem)
