# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/server_events/awards_formatters.py
from constants import PREMIUM_ENTITLEMENTS
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin
from fun_random.gui.impl.lobby.common.lootboxes import FunRandomLootBoxTypes, sortTokenFunc
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer, formatShortData
from gui.impl import backport
from gui.server_events.awards_formatters import AWARDS_SIZES, AwardsPacker, getMissionsDefaultFormatterMap, TokenBonusFormatter, UniversalPremiumDaysBonusFormatter

class FunCurtailingAwardsComposer(CurtailingAwardsComposer):

    @classmethod
    def _getShortBonusesData(cls, preformattedBonuses, size=AWARDS_SIZES.SMALL):
        return [ formatShortData(bonus, size) for bonus in preformattedBonuses ]


def getFunFormatterMap():
    mapping = getMissionsDefaultFormatterMap()
    mapping['tokens'] = FunRandomLootBoxFormatter()
    mapping['lootBox'] = FunRandomLootBoxFormatter()
    mapping[PREMIUM_ENTITLEMENTS.BASIC] = UniversalPremiumDaysBonusFormatter()
    mapping[PREMIUM_ENTITLEMENTS.PLUS] = UniversalPremiumDaysBonusFormatter()
    return mapping


def getFunSpecialFormatterMap():
    mapping = getFunFormatterMap()
    mapping['lootBox'] = FunRandomRewardLootBoxFormatter()
    return mapping


def getFunAwardsPacker(isSpecial=False):
    mapping = getFunSpecialFormatterMap() if isSpecial else getFunFormatterMap()
    return AwardsPacker(mapping)


class FunRandomLootBoxFormatter(TokenBonusFormatter, FunAssetPacksMixin):

    def _format(self, bonus):
        result = []
        for token in sorted(bonus.getTokens().itervalues(), key=sortTokenFunc):
            formatted = self._getFormattedBonus(token.id, token, bonus)
            if formatted is not None:
                result.append(formatted)

        return result

    def _getLootboxUserName(self, lootBox):
        return backport.text(self.getModeLocalsResRoot().lootbox.dyn(lootBox.getType())())

    def _getLootboxIcon(self, lootBox, size):
        if lootBox.getType() in FunRandomLootBoxTypes.ALL:
            rarity = lootBox.getType().split('_')[-1]
            return backport.image(self._getIconPath(rarity))
        return super(FunRandomLootBoxFormatter, self)._getLootboxIcon(lootBox, size)

    def _getIconPath(self, rarity):
        return self.getModeIconsResRoot().progression.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(rarity)()


class FunRandomRewardLootBoxFormatter(FunRandomLootBoxFormatter):

    def _getIconPath(self, rarity):
        return self.getModeIconsResRoot().library.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(rarity)()
