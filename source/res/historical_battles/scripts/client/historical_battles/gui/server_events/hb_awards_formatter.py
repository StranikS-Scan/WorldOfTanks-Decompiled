# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/hb_awards_formatter.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import getDefaultFormattersMap, AwardsPacker, TankmenBonusFormatter, PreformattedBonus, TokenBonusFormatter, AWARDS_SIZES, LABEL_ALIGN
from gui.shared.utils.functions import makeTooltip
from gui.server_events.formatters import parseComplexToken
from historical_battles_common.hb_constants import FRONT_COUPON_TOKEN_PREFIX

def getHBCongratsFormatter():
    return AwardsPacker(getHBCongratsFormattersMap())


def getHBQuestsAwardFormatter():
    return AwardsPacker(getHBQuestsAwardFormattersMap())


def getHBCongratsFormattersMap():
    mapping = getDefaultFormattersMap()
    mapping.update({'tankmen': HBCongratsTankmenBonusFormatter()})
    return mapping


def getHBQuestsAwardFormattersMap():
    tokenBonusFormatter = HBQuestsTokenBonusFormatter()
    mapping = getDefaultFormattersMap()
    mapping.update({'tokens': tokenBonusFormatter,
     'battleToken': tokenBonusFormatter,
     'HBCoupon': tokenBonusFormatter})
    return mapping


class HBCongratsTankmenBonusFormatter(TankmenBonusFormatter):

    def _format(self, bonus):
        result = []
        for group in bonus.getTankmenGroups().itervalues():
            roleLevel = group['roleLevel']
            result.append(PreformattedBonus(bonusName=bonus.getName(), userName=self._getUserName('with_skills'), label=self._createLabel(roleLevel), images=self._getImages(bonus), specialAlias=TOOLTIPS_CONSTANTS.TANKMAN, tooltip=makeTooltip(backport.text(R.strings.tooltips.crew.header()), backport.text(R.strings.tooltips.crew.body(), value=roleLevel))))

        return result

    @staticmethod
    def _createLabel(roleLevel):
        return '{}%'.format(roleLevel)


class HBQuestsTokenBonusFormatter(TokenBonusFormatter):

    def _getFormattedBonus(self, tokenID, token, bonus):
        complexToken = parseComplexToken(tokenID)
        if complexToken.isDisplayable:
            if complexToken.styleID.startswith(FRONT_COUPON_TOKEN_PREFIX):
                return self.formatHBCouponToken(complexToken.styleID, FRONT_COUPON_TOKEN_PREFIX, token, bonus)
        return super(HBQuestsTokenBonusFormatter, self)._getFormattedBonus(tokenID, token, bonus)

    def formatHBCouponToken(self, complexStyleID, complexPrefix, token, bonus):
        if token.count > 0:
            bonusName = complexStyleID.replace(complexPrefix, '')
            return PreformattedBonus(bonusName=bonus.getName(), label=self._formatBonusLabel(token.count), userName=self.__getHBCouponUserName(bonusName, token.count), labelFormatter=self._getLabelFormatter(bonus), images=self.__getTokenImages(bonusName), isWulf=True, tooltip=TOOLTIPS_CONSTANTS.HB_ORDER_TOOLTIP, specialArgs=[bonusName], align=LABEL_ALIGN.RIGHT, isCompensation=self._isCompensation(bonus))
        else:
            return None

    @staticmethod
    def __getHBCouponUserName(bonusName, count):
        return backport.text(R.strings.hb_tooltips.quest.award(), bonusName=bonusName, count=count)

    @staticmethod
    def __getTokenImages(bonusName):
        images = {}
        for size in AWARDS_SIZES.ALL():
            res = R.images.historical_battles.gui.maps.icons.quests.bonuses.dyn(size).dyn(bonusName)
            images[size] = backport.image(res()) if res else None

        return images
