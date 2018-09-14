# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/customization.py
import BigWorld
from constants import IGR_TYPE
from gui.Scaleform.locale.CUSTOMIZATION import CUSTOMIZATION
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization_2_0 import g_customizationController, shared
from gui.customization_2_0.data_aggregator import CUSTOMIZATION_TYPE
from gui.game_control import getIGRCtrl
from helpers.i18n import makeString as _ms
from gui import makeHtmlString
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES

class STATUS(object):
    ON_BOARD = 0
    ALREADY_HAVE = 1
    AVAILABLE_FOR_BUY = 2
    DO_MISSION = 3
    DO_IGR = 4


class BUY_ITEM_TYPE(object):
    NONE = 0
    WAYS_TO_BUY_FOREVER = 2
    WAYS_TO_BUY_TEMP = 3
    WAYS_TO_BUY_IGR = 4
    WAYS_TO_BUY_MISSION = 5
    ALREADY_HAVE_FOREVER = 6
    ALREADY_HAVE_TEMP = 7
    ALREADY_HAVE_IGR = 8


class CustomizationItemTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(CustomizationItemTooltip, self).__init__(context, TOOLTIP_TYPE.TECH_CUSTOMIZATION)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(330)
        self._descr = None
        self._cItem = None
        self._itemType = CUSTOMIZATION_TYPE.CAMOUFLAGE
        return

    def _packBlocks(self, *args):
        if len(args) == 1:
            self.__cItem = g_customizationController.carousel.items[args[0]]['object']
            self.__cItemType = g_customizationController.carousel.currentType
            self.__currentSlotIdx = g_customizationController.carousel.currentSlotIdx
        else:
            self.__cItem = g_customizationController.carousel.slots.getSlotItem(*args)
            self.__cItemType = args[1]
            self.__currentSlotIdx = args[0]
        item = self.__getItemData()
        items = super(CustomizationItemTooltip, self)._packBlocks()
        items.append(self._packTitleBlock(item))
        if item['icon']:
            items.append(self._packIconBlock(item))
        items.append(self._packBonusBlock(item))
        if item['wasBought']:
            items.append(self._packAlreadyHaveBlock(item))
        else:
            items.append(self._packWayToBuyBlock(item))
        if item['description'] is not None:
            items.append(self._packDescBlock(item))
        if item['conditional'] is not None:
            items.append(self._packConditionsBlock(item))
        items.append(self._packStatusBlock(item))
        return items

    def _packTitleBlock(self, item):
        title = item['title']
        itemsCount = self.__cItem.numberOfItems
        if itemsCount is not None:
            title += _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_ALREADYHAVE_COUNT, count=itemsCount)
        return formatters.packTitleDescBlock(title=text_styles.highTitle(title), padding={'top': -5})

    def _packIconBlock(self, item):
        actualWidth = 84
        if self.__cItemType == CUSTOMIZATION_TYPE.INSCRIPTION:
            actualWidth = 176
        return formatters.packImageBlockData(img=item['icon'], align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=actualWidth, height=84)

    def _packBonusBlock(self, item):
        bonusTitleLocal = makeHtmlString('html_templates:lobby/textStyle', 'bonusLocalText', {'message': '{0}{1}'.format(item['bonus_title_local'], '' if item['conditional'] is None else '*')})
        return formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.concatStylesWithSpace(bonusTitleLocal, text_styles.stats(item['bonus_title_global'])), desc=text_styles.main(item['bonus_desc']), img=item['bonus_icon'], imgPadding={'left': 11,
          'top': 3}, txtGap=-4, txtOffset=70, padding={'top': -1,
          'left': 7})], 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packWayToBuyBlock(self, item):
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_TITLE)), padding={'bottom': 6})]
        padding = {'left': 0}
        for buyItem in item['buyItems']:
            buyItemDesc = text_styles.main(buyItem['desc'])
            if buyItem['type'] == BUY_ITEM_TYPE.WAYS_TO_BUY_FOREVER:
                if buyItem['isSale']:
                    subBlocks.append(formatters.packSaleTextParameterBlockData(name=buyItemDesc, saleData={'newPrice': (0, buyItem['value'])}, padding=padding))
                else:
                    price = text_styles.concatStylesWithSpace(text_styles.gold(BigWorld.wg_getIntegralFormat(long(buyItem['value']))), icons.gold())
                    subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=price, valueWidth=70))
            elif buyItem['type'] == BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP:
                if buyItem['isSale']:
                    subBlocks.append(formatters.packSaleTextParameterBlockData(name=buyItemDesc, saleData={'newPrice': (buyItem['value'], 0)}, padding=padding))
                else:
                    price = text_styles.concatStylesWithSpace(text_styles.credits(BigWorld.wg_getIntegralFormat(long(buyItem['value']))), icons.credits())
                    subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=price, valueWidth=70))
            elif buyItem['type'] == BUY_ITEM_TYPE.WAYS_TO_BUY_IGR:
                subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=icons.premiumIgrSmall(), padding=padding))
            elif buyItem['type'] == BUY_ITEM_TYPE.WAYS_TO_BUY_MISSION:
                subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=icons.quest(), padding=padding))

        return formatters.packBuildUpBlockData(subBlocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, {'left': 3})

    def _packAlreadyHaveBlock(self, item):
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_ALREADYHAVE_TITLE)), padding={'bottom': 6})]
        padding = {'left': 10}
        for buyItem in item['buyItems']:
            buyItemDesc = text_styles.main(buyItem['desc'])
            if buyItem['type'] == BUY_ITEM_TYPE.ALREADY_HAVE_IGR:
                subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=icons.premiumIgrSmall(), padding=padding))
            else:
                subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value='', padding=padding))

        return formatters.packBuildUpBlockData(subBlocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, {'left': 3})

    def _packConditionsBlock(self, item):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_DESCRIPTION_CONDITIONS_TITLE)), desc=text_styles.standard('*{0}'.format(item['conditional'])), txtGap=8)

    def _packDescBlock(self, item):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_DESCRIPTION_HISTORY_TITLE)), desc=text_styles.standard(item['description']), txtGap=8)

    def _packStatusBlock(self, item):
        status = ''
        if item['status'] == STATUS.ON_BOARD:
            status = text_styles.statInfo(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_STATUS_ONBOARD))
        elif item['status'] == STATUS.ALREADY_HAVE:
            status = text_styles.statInfo(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_STATUS_ALREADYHAVE))
        elif item['status'] == STATUS.AVAILABLE_FOR_BUY:
            status = text_styles.warning(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_STATUS_AVAILABLEFORBUY))
        elif item['status'] == STATUS.DO_MISSION:
            status = text_styles.warning(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_STATUS_DOMISSION))
        elif item['status'] == STATUS.DO_IGR:
            status = icons.premiumIgrBig()
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': status}), padding={'bottom': -4,
         'top': -4})

    def __getItemData(self):
        selectedSlotItemID = g_customizationController.carousel.slots.getInstalledItem(self.__currentSlotIdx, self.__cItemType).getID()
        isInSlot = selectedSlotItemID == self.__cItem.getID()
        wasBought = False
        if self.__cItem.getIgrType() != IGR_TYPE.NONE:
            if self.__cItem.getIgrType() == getIGRCtrl().getRoomType():
                buyItems = [{'value': 0,
                  'type': BUY_ITEM_TYPE.ALREADY_HAVE_IGR,
                  'isSale': False,
                  'desc': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_ALREADYHAVE_IGR)}]
                wasBought = True
                status = STATUS.ON_BOARD if isInSlot else STATUS.ALREADY_HAVE
            else:
                buyItems = [{'value': 0,
                  'type': BUY_ITEM_TYPE.WAYS_TO_BUY_IGR,
                  'isSale': False,
                  'desc': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_IGR)}]
                status = STATUS.DO_IGR
        elif self.__cItem.isInDossier:
            data = {'value': 0,
             'isSale': False}
            if self.__cItem.numberOfDays is not None:
                data['type'] = BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP
                data['desc'] = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_TEMP, days=self.__cItem.numberOfDays)
            else:
                data['type'] = BUY_ITEM_TYPE.ALREADY_HAVE_FOREVER
                data['desc'] = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_FOREVER
            buyItems = [data]
            wasBought = True
            status = STATUS.ON_BOARD if isInSlot else STATUS.ALREADY_HAVE
        elif isInSlot:
            days = g_customizationController.carousel.slots.getInstalledItem(self.__currentSlotIdx, self.__cItemType).duration
            leftDays = g_customizationController.carousel.slots.getInstalledItem(self.__currentSlotIdx, self.__cItemType).getNumberOfDaysLeft()
            buyItems = [{'value': 0,
              'type': BUY_ITEM_TYPE.ALREADY_HAVE_TEMP,
              'isSale': False,
              'desc': _ms(CUSTOMIZATION.TOOLTIP_ELEMENT_PURCHASE_ACQUIRED_DAYS, total=days, left=leftDays)}]
            status = STATUS.ON_BOARD
            wasBought = True
        else:
            buyItems = [{'value': self.__cItem.getPrice(0),
              'type': BUY_ITEM_TYPE.WAYS_TO_BUY_FOREVER,
              'isSale': self.__isSale(BUY_ITEM_TYPE.WAYS_TO_BUY_FOREVER),
              'desc': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_FOREVER)}, {'value': self.__cItem.getPrice(30),
              'type': BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP,
              'isSale': self.__isSale(BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP),
              'desc': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_TEMP, days='30')}, {'value': self.__cItem.getPrice(7),
              'type': BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP,
              'isSale': self.__isSale(BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP),
              'desc': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_TEMP, days='7')}]
            status = STATUS.AVAILABLE_FOR_BUY
        item = {'type': self.__cItemType,
         'title': self.__cItem.getName(),
         'icon': self.__cItem.getTexturePath(),
         'bonus_icon': self.__cItem.qualifier.getIcon42x42(),
         'bonus_title_local': self.__cItem.qualifier.getFormattedValue(),
         'bonus_title_global': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_GLOBAL, count=g_customizationController.carousel.slots.bonusPanel.bonusData[self.__cItem.qualifier.getType()]['bonusTotalCount']),
         'bonus_desc': self.__cItem.qualifier.getExtendedName(),
         'wasBought': wasBought,
         'buyItems': buyItems,
         'status': status,
         'description': self.__cItem.getDescription(),
         'conditional': self.__cItem.qualifier.getDescription()}
        return item

    def __isSale(self, wayToBuy):
        if wayToBuy == BUY_ITEM_TYPE.WAYS_TO_BUY_FOREVER:
            days = 0
        else:
            days = 30
        return shared.isSale(self.__cItemType, days)
