# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/event_battle_component_assembler.py
from arena_component_system.client_arena_component_assembler import ClientArenaComponentAssembler
from arena_components.player_type_specific_components import getPlayerTypeSpecificComponentsForEventBattle

class EventBattleComponentAssembler(ClientArenaComponentAssembler):

    @staticmethod
    def assembleComponents(componentSystem):
        ClientArenaComponentAssembler._assembleBonusCapsComponents(componentSystem)
        ClientArenaComponentAssembler._addArenaComponents(componentSystem, getPlayerTypeSpecificComponentsForEventBattle())
