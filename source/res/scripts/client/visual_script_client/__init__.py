# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/__init__.py
from constants import IS_UE_EDITOR, IS_VS_EDITOR
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from contexts.sound_notifications_context import SoundNotificationsContext
from contexts.cgf_context import CGFGameObjectContext
from contexts.ability_context import AbilityContextClient
from contexts.entity_context import EntityContextClient
from contexts.vehicle_context import VehicleContextClient
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.HANGAR)

def registerContext():
    g_blockRegistrar.regContext(SoundNotificationsContext)
    g_blockRegistrar.regContext(CGFGameObjectContext)


def registerForGeneral():
    g_blockRegistrar.regContext(SoundNotificationsContext)
    g_blockRegistrar.regContext(CGFGameObjectContext)
    registerContext()
    import arena_blocks
    import vehicle_blocks
    import scene_blocks
    import event_platform_blocks
    import triggers_blocks
    import animated_hints_blocks
    import player_blocks
    import sound_blocks
    import game_settings_blocks
    import camera_blocks
    import battle_hud_block
    import cgf_blocks
    import bitmask_blocks
    import web_blocks
    import armory_yard_blocks
    g_blockRegistrar.regBlocksFromModule(event_platform_blocks)
    g_blockRegistrar.regBlocksFromModule(arena_blocks)
    g_blockRegistrar.regBlocksFromModule(vehicle_blocks)
    g_blockRegistrar.regBlocksFromModule(scene_blocks)
    g_blockRegistrar.regBlocksFromModule(triggers_blocks)
    g_blockRegistrar.regBlocksFromModule(player_blocks)
    g_blockRegistrar.regBlocksFromModule(sound_blocks)
    g_blockRegistrar.regBlocksFromModule(game_settings_blocks)
    g_blockRegistrar.regBlocksFromModule(battle_hud_block)
    g_blockRegistrar.regBlocksFromModule(cgf_blocks)
    g_blockRegistrar.regBlocksFromModule(bitmask_blocks)
    g_blockRegistrar.regBlocksFromModule(web_blocks)
    g_blockRegistrar.regBlocksFromModule(armory_yard_blocks)
    g_blockRegistrar.regBlocksFromModule(camera_blocks)
    animated_hints_blocks.regBlocks(g_blockRegistrar)
    g_blockRegistrar.regContext(AbilityContextClient)
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
