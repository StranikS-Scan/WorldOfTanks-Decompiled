# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/input_profiles.py
from __future__ import absolute_import
import Input
import BigWorld
from functools import partial
from Input import TriggerEvent
from constants import HAS_DEV_RESOURCES
_profile0 = 'BATTLE_ROYALE_DEV_INPUT_PROFILE'

def _devPredicate():
    return HAS_DEV_RESOURCES


def _pausedDeathZones():
    BigWorld.player().base.setDevelopmentFeature(0, 'paused_death_zones', 0, '')


def _pausedAirdropLoot():
    BigWorld.player().base.setDevelopmentFeature(0, 'paused_airdrop_loot', 0, '')


def _spawnBot(botName):
    BigWorld.player().vehicle.cell.brCheats.spawnBot(botName)


def initBRInput():
    _actions = [('ACTION_PLAYER_PAUSED_DEATH_ZONE', _pausedDeathZones),
     ('ACTION_PLAYER_PAUSED_AIRDROP_LOOT', _pausedAirdropLoot),
     ('ACTION_PLAYER_SPAWN_BOT_WOLF', partial(_spawnBot, 'wolf')),
     ('ACTION_PLAYER_SPAWN_BOT_HARE', partial(_spawnBot, 'hare')),
     ('ACTION_PLAYER_SPAWN_BOT_BEAR', partial(_spawnBot, 'bear'))]
    for actionName, handler in _actions:
        action = Input.inputSystem().findAction(_profile0, actionName)
        if action:
            action.setPredicate(_devPredicate)
            action.bindEventReaction(TriggerEvent.Triggered, handler)

    Input.inputSystem().activateProfile(_profile0)


def finiBRInput():
    if Input.inputSystem().hasProfile(_profile0):
        Input.inputSystem().deactivateProfile(_profile0, unbindAllReactions=True)
