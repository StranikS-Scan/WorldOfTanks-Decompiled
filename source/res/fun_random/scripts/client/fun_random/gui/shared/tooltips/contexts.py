# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/shared/tooltips/contexts.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import ARENA_BONUS_TYPE
from gui.shared.tooltips.contexts import CarouselContext
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class FunRandomCarouselContext(CarouselContext):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def getStatsConfiguration(self, item):
        value = super(FunRandomCarouselContext, self).getStatsConfiguration(item)
        config = self.__lobbyContext.getServerSettings().getCrystalRewardConfig()
        value.showEarnCrystals = config.isCrystalEarnPossible(ARENA_BONUS_TYPE.FUN_RANDOM)
        value.dailyXP = ARENA_BONUS_TYPE_CAPS.checkAny(ARENA_BONUS_TYPE.FUN_RANDOM, ARENA_BONUS_TYPE_CAPS.DAILY_MULTIPLIED_XP)
        return value
