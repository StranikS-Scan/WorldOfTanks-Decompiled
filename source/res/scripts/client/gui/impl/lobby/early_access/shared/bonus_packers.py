# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/shared/bonus_packers.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.backport import TooltipData
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, TokenBonusUIPacker, BonusUIPacker
from early_access_common import EARLY_ACCESS_PREFIX, isEarlyAccessToken

def getEarlyAccessBonusPackersMap():
    packersMap = getDefaultBonusPackersMap()
    packersMap.update({'battleToken': EarlyAccessTokenBonusUIPacker})
    return packersMap


def getEarlyAccessBonusPacker():
    return BonusUIPacker(getEarlyAccessBonusPackersMap())


class EarlyAccessTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _getTokenBonusPackers(cls):
        packers = super(EarlyAccessTokenBonusUIPacker, cls)._getTokenBonusPackers()
        packers[EARLY_ACCESS_PREFIX] = cls.__packEarlyAccessToken
        return packers

    @classmethod
    def _getTooltipsPackers(cls):
        tooltips = super(EarlyAccessTokenBonusUIPacker, cls)._getTooltipsPackers()
        tooltips[EARLY_ACCESS_PREFIX] = cls.__getEarlyAccessTooltip
        return tooltips

    @classmethod
    def _getToolTip(cls, bonus):
        tooltips = super(EarlyAccessTokenBonusUIPacker, cls)._getToolTip(bonus)
        return tooltips

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.early_access.tooltips.EarlyAccessCurrencyTooltipView()]

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        return EARLY_ACCESS_PREFIX if isEarlyAccessToken(tokenID) else super(EarlyAccessTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def __packEarlyAccessToken(cls, model, _, *args):
        model.setIconSmall(backport.image(R.images.armory_yard.gui.maps.icons.token.s20()))
        model.setIconBig(backport.image(R.images.armory_yard.gui.maps.icons.token.s44()))
        return model

    @classmethod
    def __getEarlyAccessTooltip(cls, *args):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[])]
