# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/formatters.py
from gui import makeHtmlString
from gui.Scaleform.genConsts.ACTION_PRICE_CONSTANTS import ACTION_PRICE_CONSTANTS
from gui.Scaleform.genConsts.BATTLE_RESULT_TYPES import BATTLE_RESULT_TYPES
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
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


def packTitleDescParameterWithIconBlockData(title, value='', icon=None, desc=None, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TITLE_DESC_PARAMETER_WITH_ICON_BLOCK_LINKAGE, valueAtRight=False, valueWidth=-1, gap=5, titlePadding=None, valuePadding=None, iconPadding=None, padding=None, iconAlpha=1):
    data = {'name': title,
     'value': value,
     'valueAtRight': valueAtRight,
     'iconAlpha': iconAlpha,
     'gap': gap}
    if icon is not None:
        data['icon'] = icon
    if valueWidth != -1:
        data['valueWidth'] = valueWidth
    if titlePadding is not None:
        data['titlePadding'] = titlePadding
    if valuePadding is not None:
        data['valuePadding'] = valuePadding
    if iconPadding is not None:
        data['iconPadding'] = iconPadding
    if gap != -1:
        data['gap'] = gap
    if desc is not None:
        blocks = [packBlockDataItem(linkage, data), packTextBlockData(desc)]
        return packBuildUpBlockData(blocks, gap, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding)
    else:
        return packBlockDataItem(linkage, data, padding)
        return


def packDashLineItemPriceBlockData(title, value, icon, desc=None, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_DASHLINE_ITEM_PRICE_BLOCK_LINKAGE, padding=None):
    data = {'name': title,
     'value': value,
     'icon': icon,
     'gap': -1,
     'valueWidth': -1}
    return packBlockDataItem(linkage, data, padding)


def packBuildUpBlockData(blocks, gap=0, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding=None, stretchBg=True):
    data = {'blocksData': blocks,
     'stretchBg': stretchBg}
    if gap != 0:
        data['gap'] = gap
    return packBlockDataItem(linkage, data, padding)


def packTitleDescBlock(title, desc=None, gap=TXT_GAP_FOR_BIG_TITLE, useHtml=True, textBlockLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding=None, descPadding=None):
    blocks = [packTextBlockData(title, useHtml, textBlockLinkage)]
    if desc is not None:
        blocks.append(packTextBlockData(desc, useHtml, textBlockLinkage, descPadding))
    return packBuildUpBlockData(blocks, gap, blocksLinkage, padding)


def packTitleDescBlockSmallTitle(title, desc=None, useHtml=True, textBlockLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding=None):
    return packTitleDescBlock(title, desc, TXT_GAP_FOR_SMALL_TITLE, useHtml, textBlockLinkage, blocksLinkage, padding)


def packResultBlockData(title, text):
    return packBuildUpBlockData([packTextBlockData(title, True, BATTLE_RESULT_TYPES.TOOLTIP_RESULT_TTILE_LEFT_LINKAGE), packTextBlockData(text, True, BATTLE_RESULT_TYPES.TOOLTIP_ICON_TEXT_PARAMETER_LINKAGE)])


def packImageTextBlockData(title=None, desc=None, img=None, imgPadding=None, imgAtLeft=True, txtPadding=None, txtGap=0, txtOffset=-1, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE, padding=None):
    data = {'spriteAtLeft': imgAtLeft,
     'textsAlign': txtAlign}
    if title is not None:
        data['title'] = title
    if desc is not None:
        data['description'] = desc
    if img is not None:
        data['imagePath'] = img
    if imgPadding is not None:
        data['spritePadding'] = imgPadding
    if txtPadding is not None:
        data['textsPadding'] = txtPadding
    if txtGap != 0:
        data['textsGap'] = txtGap
    if txtOffset != 0:
        data['textsOffset'] = txtOffset
    return packBlockDataItem(linkage, data, padding)


def packItemTitleDescBlockData(title=None, desc=None, img=None, imgPadding=None, imgAtLeft=True, txtPadding=None, txtGap=0, txtOffset=-1, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_ITEM_TITLE_DESC_BLOCK_LANKAGE, padding=None, overlayPath=None, overlayPadding=None, highlightPath=None, highlightPadding=None):
    data = {'spriteAtLeft': imgAtLeft,
     'textsAlign': txtAlign}
    if title is not None:
        data['title'] = title
    if desc is not None:
        data['description'] = desc
    if img is not None:
        data['imagePath'] = img
    if imgPadding is not None:
        data['spritePadding'] = imgPadding
    if txtPadding is not None:
        data['textsPadding'] = txtPadding
    if txtGap != 0:
        data['textsGap'] = txtGap
    if txtOffset != 0:
        data['textsOffset'] = txtOffset
    if overlayPath is not None:
        data['overlayPath'] = overlayPath
        if overlayPadding is not None:
            data['overlayPadding'] = overlayPadding
    if highlightPath is not None:
        data['highlightPath'] = highlightPath
        if highlightPadding is not None:
            data['highlightPadding'] = highlightPadding
    return packBlockDataItem(linkage, data, padding)


def packRendererTextBlockData(rendererType, dataType, rendererData, title=None, desc=None, rendererPadding=None, imgAtLeft=True, txtPadding=None, txtGap=0, txtOffset=-1, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_RENDERER_TEXT_BLOCK_LINKAGE, padding=None):
    data = {'rendererData': {'rendererType': rendererType,
                      'data': rendererData,
                      'dataType': dataType},
     'spriteAtLeft': imgAtLeft,
     'textsAlign': txtAlign}
    if title is not None:
        data['title'] = title
    if desc is not None:
        data['description'] = desc
    if rendererPadding is not None:
        data['spritePadding'] = rendererPadding
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


def packSaleTextParameterBlockData(name, saleData, actionStyle=ACTION_PRICE_CONSTANTS.STATE_CAMOUFLAGE, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_SALE_TEXT_PARAMETER_BLOCK_LINKAGE, padding=None, currency=None):
    data = {'name': name,
     'saleData': saleData,
     'actionStyle': actionStyle,
     'currency': currency}
    return packBlockDataItem(linkage, data, padding)


def packStatusDeltaBlockData(title, valueStr, statusBarData, buffIconSrc='', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_STATUS_DELTA_PARAMETER_BLOCK_LINKAGE, padding=None):
    data = {'title': title,
     'valueStr': valueStr,
     'statusBarData': statusBarData,
     'buffIconSrc': buffIconSrc}
    return packBlockDataItem(linkage, data, padding)


def packCrewSkillsBlockData(crewStr, skillsStr, crewfIconSrc='', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_CREW_SKILLS_BLOCK_LINKAGE, padding=None):
    data = {'crewStr': crewStr,
     'skillsStr': skillsStr,
     'crewfIconSrc': crewfIconSrc}
    return packBlockDataItem(linkage, data, padding)


def packGroupBlockData(listData, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_GROUP_BLOCK_LINKAGE, padding=None):
    data = {'rendererType': RANKEDBATTLES_ALIASES.RANKED_AWARD_RENDERER_ALIAS,
     'listIconSrc': listData,
     'align': BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER,
     'rendererWidth': 48}
    return packBlockDataItem(linkage, data, padding)


def packRankBlockData(rank, isEnabled=True, isMaster=False, rankCount='', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_RANK_BLOCK_LINKAGE, padding=None):
    data = {'imageSrc': rank.getIcon('big'),
     'smallImageSrc': rank.getIcon('small'),
     'isEnabled': isEnabled,
     'isMaster': isMaster,
     'rankID': str(rank.getID()),
     'rankCount': str(rankCount)}
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
    defaultPrice = rentPackage['defaultRentPrice']
    price = rentPackage['rentPrice']
    states = [ ACTION_TOOLTIPS_STATE.DISCOUNT for _ in price ]
    return {'type': ACTION_TOOLTIPS_TYPE.RENT,
     'key': str(item.intCD),
     'state': states,
     'newPrice': price,
     'oldPrice': defaultPrice,
     'rentPackage': rentPackage['days']}


def packImageListParameterBlockData(listIconSrc, columnWidth, rowHeight, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TILE_LIST_BLOCK_LINKAGE, padding=None):
    return packBlockDataItem(linkage, {'dataType': 'String',
     'rendererType': 'ImageRendererUI',
     'listIconSrc': listIconSrc,
     'columnWidth': columnWidth,
     'rowHeight': rowHeight}, padding)


def packQuestAwardsBlockData(listData, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TILE_LIST_BLOCK_LINKAGE, padding=None):
    return packBlockDataItem(linkage, {'dataType': 'net.wg.gui.data.AwardItemVO',
     'rendererType': 'AwardItemRendererUI',
     'listIconSrc': listData,
     'columnWidth': 85,
     'rowHeight': 50}, padding)


def packMissionVehiclesBlockData(listData, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TILE_LIST_BLOCK_LINKAGE, padding=None):
    """
    Gets vehicles list for VehicleKill or VehicleDamage quest's conditions to display in tooltip
    """
    return packBlockDataItem(linkage, {'dataType': 'net.wg.gui.lobby.missions.data.MissionVehicleItemRendererVO',
     'rendererType': 'MissionVehicleItemRendererUI',
     'listIconSrc': listData,
     'columnWidth': 290,
     'rowHeight': 32}, padding)


def packMissionVehiclesTypeBlockData(listData, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_TILE_LIST_BLOCK_LINKAGE, padding=None):
    """
    Gets filters data: nations, types, levels for VehicleKill or VehicleDamage quest's conditions to display in tooltip
    """
    return packBlockDataItem(linkage, {'dataType': 'net.wg.gui.lobby.missions.data.MissionVehicleTypeRendererVO',
     'rendererType': 'MissionVehicleTypeRendererUI',
     'listIconSrc': listData,
     'columnWidth': 470,
     'rowHeight': 70}, padding)


def getActionPriceData(item):
    price = item.altPrice or item.buyPrice
    defaultPrice = item.defaultAltPrice or item.defaultPrice
    minRentPricePackage = item.getRentPackage()
    action = None
    if minRentPricePackage and minRentPricePackage['rentPrice'] != minRentPricePackage['defaultRentPrice']:
        action = packItemRentActionTooltipData(item, minRentPricePackage)
    elif not item.isRestoreAvailable():
        if price != defaultPrice:
            action = packItemActionTooltipData(item)
    return action


def getLimitExceededPremiumTooltip():
    return makeTooltip(i18n.makeString(TOOLTIPS.LOBBY_HEADER_BUYPREMIUMACCOUNT_DISABLED_HEADER), i18n.makeString(TOOLTIPS.LOBBY_HEADER_BUYPREMIUMACCOUNT_DISABLED_BODY, number=time_utils.ONE_YEAR / time_utils.ONE_DAY))


def packCounterTextBlockData(countLabel, desc, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_COUNTER_TEXT_BLOCK_LINKAGE, padding=None):
    data = {'label': str(countLabel),
     'description': desc}
    return packBlockDataItem(linkage, data, padding)
