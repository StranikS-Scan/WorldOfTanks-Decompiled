# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/BattleRoyalePersonality.py
from battle_royale.gui.battle_control.controllers.repository import registerBRBattleRepo
from battle_royale.gui.Scaleform import registerBRBattlePackages, registerBRLobbyPackages, registerBRTooltipsBuilders, registerCustomSwf, registerBRBattleQueueProvider
from battle_royale.gui.impl import registerBRViews
from battle_royale.gui.battle_control.controllers.equipment_items import registerBREquipmentsItems
from battle_royale.gui.hangar_presets import registerBattleRoyaleHangarPresets
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.hangar_quest_flags import registerQuestFlags
from battle_royale.gui.Scaleform.daapi.view.lobby import hangar_constants
from battle_royale.gui.prb_control import registerBRPrebattles
from battle_royale.gui.battle_results import registerBRBattleResultsComposer
import gui.customization
from battle_royale.gui.game_control import registerBRGameControllers
from gui.prb_control.prb_utils import initHangarGuiConsts
from battle_royale.gui.game_control.br_season_provider import registerBRSeasonProviderHandler

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
    registerBattleRoyaleHangarPresets()
    registerCustomSwf()
    registerBRViews()
    registerQuestFlags()
    registerBRSeasonProviderHandler()
    registerBRBattleResultsComposer()


def init():
    pass


def start():
    pass


def fini():
    pass
