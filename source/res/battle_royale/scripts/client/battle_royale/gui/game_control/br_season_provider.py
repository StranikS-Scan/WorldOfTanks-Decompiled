# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/game_control/br_season_provider.py
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from constants import GameSeasonType
from gui.shared.system_factory import registerSeasonProviderHandler

def registerBRSeasonProviderHandler():
    registerSeasonProviderHandler(GameSeasonType.BATTLE_ROYALE, lambda *args, **kwargs: dependency.instance(IBattleRoyaleController))
