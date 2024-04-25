# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/player_type_specific_components.py
from arena_components.epic_battle_player_data_component import EpicBattlePlayerDataComponent
from player_data_component import PlayerDataComponent
from advanced_chat_component import AdvancedChatComponent
from arena_component_system.epic_sector_warning_component import EpicSectorWarningComponent
from arena_component_system.arena_equipment_component import ArenaEquipmentComponent
from arena_component_system.overtime_component import OvertimeComponent
from arena_components.effects_list_cache import EffectsListCacheComponent

def getPlayerTypeSpecificComponentsForEpicRandom():
    return {'playerDataComponent': PlayerDataComponent}


def getPlayerTypeSpecificComponentsForEpicBattle():
    return {'playerDataComponent': EpicBattlePlayerDataComponent,
     'sectorWarningComponent': EpicSectorWarningComponent,
     'overtimeComponent': OvertimeComponent}


def getDefaultComponents():
    return {'arenaEquipmentComponent': ArenaEquipmentComponent,
     'advancedChatComponent': AdvancedChatComponent}


def getPlayerTypeSpecificComponentsForEventBattle():
    return {'effectsListCache': EffectsListCacheComponent}
