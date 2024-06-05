# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/shared/bonuses_formatters.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import AWARDS_SIZES, PreformattedBonus
_IMAGE_FORMAT = '.png'
_BONUSES_ALWAYS_ON_DISPLAY = ['freeXP', 'credits']

def getImgName(path):
    return '' if path is None else path.split('/')[-1].replace(_IMAGE_FORMAT, '').replace('-', '_')


class StoryModeBonusesAwardsComposer(CurtailingAwardsComposer):

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        return bonus

    def _packBonuses(self, preformattedBonuses, size):
        sortedRewards = sorted(preformattedBonuses, key=lambda preformattedBonus: preformattedBonus.bonusName not in _BONUSES_ALWAYS_ON_DISPLAY)
        return super(StoryModeBonusesAwardsComposer, self)._packBonuses(sortedRewards, size)

    def _packMergedBonuses(self, mergedBonuses, size=AWARDS_SIZES.SMALL):
        mergedBonusCount = len(mergedBonuses)
        imgs = {AWARDS_SIZES.SMALL: RES_ICONS.getBonusIcon(AWARDS_SIZES.SMALL, 'default'),
         AWARDS_SIZES.BIG: RES_ICONS.getBonusIcon(AWARDS_SIZES.BIG, 'default')}
        return PreformattedBonus(bonusName='default', label=backport.text(R.strings.marathon.reward.rest(), count=mergedBonusCount), isSpecial=True, images=imgs, specialAlias=TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS, specialArgs=self._getShortBonusesData(mergedBonuses, size), userName='')
