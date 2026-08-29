# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/BattleRoyalePersonality.py
from __future__ import absolute_import
from battle_royale.gui.battle_control.controllers.repository import registerBRBattleRepo
from battle_royale.gui.Scaleform import registerBRBattlePackages, registerBRLobbyPackages, registerBRTooltipsBuilders, registerCustomSwf, registerBRBattleQueueProvider, registerBRHangarPresetGetter
from battle_royale.gui.battle_control.controllers.equipment_items import registerBREquipmentsItems
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.hangar_quest_flags import registerQuestFlags
from battle_royale.gui.Scaleform.daapi.view.lobby import hangar_constants
from battle_royale.gui.prb_control import registerBRPrebattles
from battle_royale.gui.battle_results import registerBRBattleResultsComposer
import gui.customization
from battle_royale.gui.game_control import registerBRGameControllers
from gui.prb_control.prb_utils import initHangarGuiConsts
from battle_royale.gui.game_control.br_season_provider import registerBRSeasonProviderHandler
from battle_royale import initProgression
from battle_royale.input_profiles import initBRInput, finiBRInput
import BigWorld
from constants import ARENA_BONUS_TYPE, HAS_DEV_RESOURCES
from PlayerEvents import g_playerEvents

def _onAvatarReadyBR():
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None and arena.bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE:
        initBRInput()
    return


def preInit():
    initHangarGuiConsts(hangar_constants, __name__)
    registerBRBattleRepo()
    registerBRBattlePackages()
    registerBRLobbyPackages()
    registerBRBattleQueueProvider()
    registerBRTooltipsBuilders()
    registerBRGameControllers()
    registerBREquipmentsItems()
    registerBRPrebattles()
    registerCustomSwf()
    registerQuestFlags()
    registerBRSeasonProviderHandler()
    registerBRBattleResultsComposer()
    registerBRHangarPresetGetter()
    initProgression()


def init():
    if HAS_DEV_RESOURCES:
        g_playerEvents.onAvatarReady += _onAvatarReadyBR
        g_playerEvents.onAvatarBecomeNonPlayer += finiBRInput


def start():
    pass


def fini():
    if HAS_DEV_RESOURCES:
        g_playerEvents.onAvatarReady -= _onAvatarReadyBR
        g_playerEvents.onAvatarBecomeNonPlayer -= finiBRInput
