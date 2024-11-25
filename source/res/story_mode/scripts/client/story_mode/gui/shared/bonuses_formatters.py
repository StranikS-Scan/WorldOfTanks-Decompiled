# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/shared/bonuses_formatters.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import AWARDS_SIZES, PreformattedBonus
from story_mode.gui.story_mode_gui_constants import BONUS_ORDER
if typing.TYPE_CHECKING:
    from gui.server_events.awards_formatters import _PreformattedBonus
_IMG_PATH_PREFIX = 'img://gui'

def getImgPath(path):
    if path is None:
        return ''
    else:
        return path if path.startswith('img:') else _IMG_PATH_PREFIX + path[2:]


class StoryModeBonusesAwardsComposer(CurtailingAwardsComposer):

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        return bonus

    def _packBonuses(self, preformattedBonuses, size):
        sortedRewards = sorted(preformattedBonuses, key=self._bonusesSortFunction)
        return super(StoryModeBonusesAwardsComposer, self)._packBonuses(sortedRewards, size)

    def _packMergedBonuses(self, mergedBonuses, size=AWARDS_SIZES.SMALL):
        mergedBonusCount = len(mergedBonuses)
        imgs = {AWARDS_SIZES.SMALL: RES_ICONS.getBonusIcon(AWARDS_SIZES.SMALL, 'default'),
         AWARDS_SIZES.BIG: RES_ICONS.getBonusIcon(AWARDS_SIZES.BIG, 'default')}
        return PreformattedBonus(bonusName='default', label=backport.text(R.strings.marathon.reward.rest(), count=mergedBonusCount), isSpecial=True, images=imgs, specialAlias=TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS, specialArgs=self._getShortBonusesData(mergedBonuses, size), userName='')

    @staticmethod
    def _bonusesSortFunction(bonus):
        name = bonus.bonusName
        return BONUS_ORDER.index(name) if name in BONUS_ORDER else len(BONUS_ORDER) + 1
