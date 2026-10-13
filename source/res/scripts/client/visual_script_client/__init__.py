# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/__init__.py
from __future__ import absolute_import
from constants import IS_UE_EDITOR, IS_VS_EDITOR
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from visual_script_client.contexts.sound_notifications_context import SoundNotificationsContext
from visual_script_client.contexts.ability_context import AbilityContextClient
from visual_script_client.contexts.entity_context import EntityContextClient
from visual_script_client.contexts.vehicle_context import VehicleContextClient
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.HANGAR)

def registerContext():
    g_blockRegistrar.regContext(SoundNotificationsContext)
    g_blockRegistrar.regContext(AbilityContextClient)


def registerForGeneral():
    registerContext()
    from visual_script_client import arena_blocks, vehicle_blocks, scene_blocks, event_platform_blocks, triggers_blocks, player_blocks, sound_blocks, game_settings_blocks, camera_blocks, battle_hud_block, bitmask_blocks, cgf_blocks, pve_battle_hud_blocks, battle_hints_blocks, vehicle_mechanics_blocks, platoon_blocks, pet_system_blocks, gameplay_logic_blocks
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
    g_blockRegistrar.regBlocksFromModule(camera_blocks)
    g_blockRegistrar.regBlocksFromModule(pve_battle_hud_blocks)
    g_blockRegistrar.regBlocksFromModule(vehicle_mechanics_blocks)
    g_blockRegistrar.regBlocksFromModule(platoon_blocks)
    g_blockRegistrar.regType(player_blocks.PlayerControlMode)
    g_blockRegistrar.regType(vehicle_blocks.OverturnWarningLevelEnum)
    g_blockRegistrar.regType(vehicle_blocks.DrownWarningLevelEnum)
    g_blockRegistrar.regTypesFromModule(pet_system_blocks)
    g_blockRegistrar.regBlocksFromModule(pet_system_blocks)
    g_blockRegistrar.regTypesFromModule(gameplay_logic_blocks)
    g_blockRegistrar.regBlocksFromModule(gameplay_logic_blocks)
    g_blockRegistrar.regContext(EntityContextClient)
    g_blockRegistrar.regContext(VehicleContextClient)
    g_blockRegistrar.regType(vehicle_mechanics_blocks.RechargeableNitroStateEnum)


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
