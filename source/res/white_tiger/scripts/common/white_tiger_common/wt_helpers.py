# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/wt_helpers.py


def getTankPortalActualPrice(tankPortalPrice, discountPerToken, discountTokenCount):
    totalDiscount = discountTokenCount * discountPerToken
    return tankPortalPrice - totalDiscount


def getTankPortalDiscount(tankPortalPrice, discountPerToken, discountTokenCount):
    discount = discountPerToken * discountTokenCount
    return 100.0 * discount / tankPortalPrice
