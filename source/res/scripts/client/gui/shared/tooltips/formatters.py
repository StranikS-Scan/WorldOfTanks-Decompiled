# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/formatters.py
from gui import makeHtmlString
from gui.Scaleform.genConsts.ACTION_PRICE_CONSTANTS import ACTION_PRICE_CONSTANTS
from gui.Scaleform.genConsts.BATTLE_RESULT_TYPES import BATTLE_RESULT_TYPES
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import i18n, time_utils
TXT_GAP_FOR_BIG_TITLE = 2
TXT_GAP_FOR_SMALL_TITLE = 3

def packPadding(top=0, left=0, bottom=0, right=0):
    data = {}
    if top != 0:
        data['top'] = top
    if left != 0:
        data['left'] = left
    if bottom != 0:
        data['bottom'] = bottom
    if right != 0:
        data['right'] = right
    return data


def packBlockDataItem(linkage, data, padding=None):
    data = {'linkage': linkage,
     'data': data}
    if padding is not None:
        data['padding'] = padding
    return data


def packTextBlockData(text, useHtml=True, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, padding=None):
    return packBlockDataItem(linkage, {'text': text,
     'useHtml': useHtml}, padding)


def packAlignedTextBlockData(text, align, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, padding=None):
    return packBlockDataItem(linkage, {'text': makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': align,
              'message': text}),
     'useHtml': True}, padding)


def packTotalItemsBlockData(counter, text, counterVisible):
    return packBlockDataItem(BATTLE_RESULT_TYPES.TOOLTIP_TOTAL_ITEMS_BLOCK_LINKAGE, {'text': text,
     'counter': counter,
     'counterVisible': counterVisible})


def packTextParameterBlockData(name, value, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_PARAMETER_BLOCK_LINKAGE, valueWidth=-1, gap=5, padding=None):
    data = {'name': name,
     'value': value}
    if valueWidth != -1:
        data['valueWidth'] = valueWidth
    if gap != -1:
        data['gap'] = gap
    return packBlockDataItem(linkage, data, padding)


def packTextParameterWithIconBlockData(name, value, icon, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_PARAMETER_WITH_ICON_BLOCK_LINKAGE, valueWidth=-1, gap=5, nameOffset=-1, padding=None):
    data = {'name': name,
     'value': value,
     'icon': icon}
    if valueWidth != -1:
        data['valueWidth'] = valueWidth
    if gap != -1:
        data['gap'] = gap
    if nameOffset != -1:
        data['nameOffset'] = nameOffset
    return packBlockDataItem(linkage, data, padding)


def packBuildUpBlockData(blocks, gap=0, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding=None, stretchBg=True):
    data = {'blocksData': blocks,
     'stretchBg': stretchBg}
    if gap != 0:
        data['gap'] = gap
    return packBlockDataItem(linkage, data, padding)


def packTitleDescBlock(title, desc=None, gap=TXT_GAP_FOR_BIG_TITLE, useHtml=True, textBlockLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding=None):
    blocks = [packTextBlockData(title, useHtml, textBlockLinkage)]
    if desc is not None:
        blocks.append(packTextBlockData(desc, useHtml, textBlockLinkage))
    return packBuildUpBlockData(blocks, gap, blocksLinkage, padding)


def packTitleDescBlockSmallTitle(title, desc=None, useHtml=True, textBlockLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding=None):
    return packTitleDescBlock(title, desc, TXT_GAP_FOR_SMALL_TITLE, useHtml, textBlockLinkage, blocksLinkage, padding)


def packResultBlockData(title, text):
    return packBuildUpBlockData([packTextBlockData(title, True, BATTLE_RESULT_TYPES.TOOLTIP_RESULT_TTILE_LEFT_LINKAGE), packTextBlockData(text, True, BATTLE_RESULT_TYPES.TOOLTIP_ICON_TEXT_PARAMETER_LINKAGE)])


def packImageTextBlockData(title=None, desc=None, img=None, imgPadding=None, imgAtLeft=True, txtPadding=None, txtGap=0, txtOffset=-1, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE, padding=None):
    data = {'imageAtLeft': imgAtLeft,
     'textsAlign': txtAlign}
    if title is not None:
        data['title'] = title
    if desc is not None:
        data['description'] = desc
    if img is not None:
        data['imagePath'] = img
    if imgPadding is not None:
        data['imagePadding'] = imgPadding
    if txtPadding is not None:
        data['textsPadding'] = txtPadding
    if txtGap != 0:
        data['textsGap'] = txtGap
    if txtOffset != 0:
        data['textsOffset'] = txtOffset
    return packBlockDataItem(linkage, data, padding)


def packImageBlockData(img=None, align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGE_BLOCK_LINKAGE, width=-1, height=-1, padding=None):
    data = {'align': align}
    if img is not None:
        data['imagePath'] = img
    if width != -1:
        data['width'] = width
    if height != -1:
        data['height'] = height
    return packBlockDataItem(linkage, data, padding)


def packSaleTextParameterBlockData(name, saleData, actionStyle=ACTION_PRICE_CONSTANTS.STATE_CAMOUFLAGE, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_SALE_TEXT_PARAMETER_BLOCK_LINKAGE, padding=None):
    data = {'name': name,
     'saleData': saleData,
     'actionStyle': actionStyle}
    return packBlockDataItem(linkage, data, padding)


def packStatusDeltaBlockData(title, valueStr, statusBarData, buffIconSrc='', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_STATUS_DELTA_PARAMETER_BLOCK_LINKAGE, padding=None):
    data = {'title': title,
     'valueStr': valueStr,
     'statusBarData': statusBarData,
     'buffIconSrc': buffIconSrc}
    return packBlockDataItem(linkage, data, padding)


def packItemActionTooltipData(item, isBuying=True):
    """
    Build action data for given fitting item
    
    :param item:
    :param isBuying:
    :return: action data dict
    """
    if isBuying:
        price = item.altPrice or item.buyPrice
        defaultPrice = item.defaultAltPrice or item.defaultPrice
    else:
        price = item.sellPrice
        defaultPrice = item.defaultSellPrice
    return packActionTooltipData(ACTION_TOOLTIPS_TYPE.ITEM, str(item.intCD), isBuying, price, defaultPrice)


def packActionTooltipData(type, key, isBuying, price, oldPrice):
    """
    Packs data into action tooltip VO.
    
    :param type: an ACTION_TOOLTIPS_STATE
    :param key: key
    :param isBuying: True if tooltip is for buying, otherwise False
    :param price: current price
    :param oldPrice: old price
    :return: VO
    """
    states = list()
    for currency, oldValue in oldPrice.iteritems():
        priceValue = price.get(currency)
        if priceValue < oldValue:
            state = ACTION_TOOLTIPS_STATE.DISCOUNT if isBuying else ACTION_TOOLTIPS_STATE.PENALTY
        elif priceValue > oldValue:
            state = ACTION_TOOLTIPS_STATE.PENALTY if isBuying else ACTION_TOOLTIPS_STATE.DISCOUNT
        else:
            state = None
        states.append(state)

    return {'type': type,
     'key': key,
     'isBuying': isBuying,
     'state': states,
     'newPrice': price,
     'oldPrice': oldPrice,
     'ico': price.getCurrency()}


def packItemRentActionTooltipData(item, rentPackage):
    """
    Build rent action data for given fitting item
    
    :param item:
    :param rentPackage:
    :return: action data dict
    """
    goldState = creditsState = ACTION_TOOLTIPS_STATE.DISCOUNT
    defaultPrice = rentPackage['defaultRentPrice']
    price = rentPackage['rentPrice']
    return {'type': ACTION_TOOLTIPS_TYPE.RENT,
     'key': str(item.intCD),
     'state': (creditsState, goldState),
     'newPrice': price,
     'oldPrice': defaultPrice,
     'rentPackage': rentPackage['days']}


def packImageListParameterBlockData(listIconSrc, columnWidth, rowHeight, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGE_LIST_BLOCK_LINKAGE, padding=None):
    return packBlockDataItem(linkage, {'listIconSrc': listIconSrc,
     'columnWidth': columnWidth,
     'rowHeight': rowHeight}, padding)


def getActionPriceData(item):
    price = item.altPrice or item.buyPrice
    defaultPrice = item.defaultAltPrice or item.defaultPrice
    minRentPricePackage = item.getRentPackage()
    action = None
    if minRentPricePackage:
        if minRentPricePackage['rentPrice'] != minRentPricePackage['defaultRentPrice']:
            action = packItemRentActionTooltipData(item, minRentPricePackage)
    elif not item.isRestoreAvailable():
        if price != defaultPrice:
            action = packItemActionTooltipData(item)
    return action


def getLimitExceededPremiumTooltip():
    return makeTooltip(i18n.makeString(TOOLTIPS.LOBBY_HEADER_BUYPREMIUMACCOUNT_DISABLED_HEADER), i18n.makeString(TOOLTIPS.LOBBY_HEADER_BUYPREMIUMACCOUNT_DISABLED_BODY, number=time_utils.ONE_YEAR / time_utils.ONE_DAY))
