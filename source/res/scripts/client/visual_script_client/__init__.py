# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/__init__.py
from constants import IS_UE_EDITOR, IS_VS_EDITOR
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from contexts.sound_notifications_context import SoundNotificationsContext
from contexts.ability_context import AbilityContextClient
from contexts.entity_context import EntityContextClient
from contexts.vehicle_context import VehicleContextClient
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.HANGAR)

def registerContext():
    g_blockRegistrar.regContext(SoundNotificationsContext)
    g_blockRegistrar.regContext(AbilityContextClient)


def registerForGeneral():
    registerContext()
    import arena_blocks
    import vehicle_blocks
    import scene_blocks
    import event_platform_blocks
    import triggers_blocks
    import player_blocks
    import sound_blocks
    import game_settings_blocks
    import camera_blocks
    import battle_hud_block
    import bitmask_blocks
    import cgf_blocks
    import pve_battle_hud_blocks
    import battle_hints_blocks
    g_blockRegistrar.regBlocksFromModule(event_platform_blocks)
    g_blockRegistrar.regBlocksFromModule(arena_blocks)
    g_blockRegistrar.regBlocksFromModule(vehicle_blocks)
    g_blockRegistrar.regBlocksFromModule(scene_blocks)
    g_blockRegistrar.regBlocksFromModule(triggers_blocks)
    g_blockRegistrar.regBlocksFromModule(player_blocks)
    g_blockRegistrar.regBlocksFromModule(sound_blocks)
    g_blockRegistrar.regBlocksFromModule(game_settings_blocks)
    g_blockRegistrar.regBlocksFromModule(battle_hud_block)
    g_blockRegistrar.regBlocksFromModule(bitmask_blocks)
    g_blockRegistrar.regBlocksFromModule(cgf_blocks)
    g_blockRegistrar.regBlocksFromModule(battle_hints_blocks)
    g_blockRegistrar.regType(player_blocks.PlayerControlMode)
    g_blockRegistrar.regBlocksFromModule(camera_blocks)
    g_blockRegistrar.regBlocksFromModule(pve_battle_hud_blocks)
    g_blockRegistrar.regContext(EntityContextClient)
    g_blockRegistrar.regContext(VehicleContextClient)


def registerForUEEditor():
    registerContext()


def registerForVSEditor():
    registerForGeneral()


def registerForClient():
    registerForGeneral()


if IS_UE_EDITOR:
    registerForUEEditor()
elif IS_VS_EDITOR:
    registerForVSEditor()
else:
    registerForClient()
