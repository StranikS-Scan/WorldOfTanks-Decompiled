# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/common/filter_popover.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.daapi.view.common.filter_popover import FILTER_SECTION, BattlePassCarouselFilterPopover
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class FunRandomCarouselFilterPopover(BattlePassCarouselFilterPopover):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def _generateMapping(cls, hasRented, hasEvent, hasRoles, **kwargs):
        mapping = super(FunRandomCarouselFilterPopover, cls)._generateMapping(hasRented, hasEvent, hasRoles, **kwargs)
        filterSpecialsList = mapping[FILTER_SECTION.SPECIALS]
        filterSpecialsList.append('funRandom')
        if 'clanRented' in filterSpecialsList:
            filterSpecialsList.remove('clanRented')
        config = cls.__lobbyContext.getServerSettings().getCrystalRewardConfig()
        if not config.isCrystalEarnPossible(ARENA_BONUS_TYPE.FUN_RANDOM):
            filterSpecialsList.remove('crystals')
        if not BONUS_CAPS.checkAny(ARENA_BONUS_TYPE.FUN_RANDOM, BONUS_CAPS.DAILY_MULTIPLIED_XP):
            filterSpecialsList.remove('bonus')
        return mapping
