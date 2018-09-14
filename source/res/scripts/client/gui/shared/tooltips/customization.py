# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/customization.py
import BigWorld
import nations
from constants import IGR_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.customization_2_0 import g_customizationController
from gui.customization_2_0.data_aggregator import CUSTOMIZATION_TYPE, DURATION, TYPE_NAME
from gui.game_control import getIGRCtrl
from gui.shared.ItemsCache import g_itemsCache
from gui import makeHtmlString
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from helpers.i18n import makeString as _ms
from nations import NONE_INDEX as ANY_NATION
from gui.customization_2_0.filter import PURCHASE_TYPE

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
    """Tooltip data provider for the customization elements in customization windows.
    """

    def __init__(self, context):
        super(CustomizationItemTooltip, self).__init__(context, TOOLTIP_TYPE.TECH_CUSTOMIZATION)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(330)
        self._item = None
        self._itemType = 0
        self._nationId = 0
        self.__slotIdx = -1
        return

    def _getObtainMethod(self):
        """Find the appropriate method of how the element can be obtained.
        """
        for obtainMethod, condition in ((self.__obtainedFromIgr, self._item.getIgrType() != IGR_TYPE.NONE),
         (self.__obtainedInDossier, self._item.isInDossier),
         (self.__obtainedInSlot, self.__isInstalled()),
         (self.__notObtained, True)):
            if condition:
                return obtainMethod()

    def _packBlocks(self, *args):
        items = []
        if len(args) == 1:
            self._item = g_customizationController.carousel.items[args[0]]['object']
            self._itemType = g_customizationController.carousel.currentType
            self.__slotIdx = -1
        else:
            self.__slotIdx, self._itemType = args[:2]
            self._item = g_customizationController.carousel.slots.getSlotItem(*args[:2])
        data = self._getItemData()
        if self.__isInQuest():
            data['itemsCount'] = None
        items.append(self._packTitleBlock(data))
        items.append(self._packIconBlock(data))
        items.append(self._packBonusBlock(data))
        if data['condition'] is not None and data['type'] != CUSTOMIZATION_TYPE.CAMOUFLAGE:
            items.append(self._packConditionBlock(data))
        if data['wasBought']:
            items.append(self._packAlreadyHaveBlock(data))
        else:
            items.append(self._packWayToBuyBlock(data))
        if data['description'] is not None:
            items.append(self._packDescBlock(data))
        items.append(self._packStatusBlock(data))
        return items

    def _packTitleBlock(self, data):
        title = data['title']
        itemsCount = data['itemsCount']
        if itemsCount is not None and itemsCount > 1:
            title += _ms('#vehicle_customization:customization/tooltip/alreadyHave/count', count=itemsCount)
        typeText = ''
        if self._itemType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            typeText = _ms('#vehicle_customization:camouflage')
        elif self._itemType == CUSTOMIZATION_TYPE.EMBLEM:
            typeText = _ms('#vehicle_customization:emblem')
        elif self._itemType == CUSTOMIZATION_TYPE.INSCRIPTION:
            typeText = _ms('#vehicle_customization:inscription')
        typeText += ' ' + _ms(data['groupName'])
        return formatters.packImageTextBlockData(title=text_styles.highTitle(title), padding={'top': -5}, desc=text_styles.main(typeText))

    def _packIconBlock(self, data):
        actualWidth = 84
        if self._itemType == CUSTOMIZATION_TYPE.INSCRIPTION:
            actualWidth = 176
        return formatters.packImageBlockData(img=data['icon'], align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=actualWidth, height=84)

    def _packBonusBlock(self, data):
        conditionBonus = data['condition'] is not None and data['type'] != CUSTOMIZATION_TYPE.CAMOUFLAGE
        bonusTitleLocal = makeHtmlString('html_templates:lobby/textStyle', 'bonusLocalText', {'message': '{0}{1}'.format(data['bonus_title_local'], '*' if conditionBonus else '')})
        return formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.concatStylesWithSpace(bonusTitleLocal), desc=text_styles.main(data['bonus_desc']), img=data['bonus_icon'], imgPadding={'left': 11,
          'top': 3}, txtGap=-4, txtOffset=70, padding={'top': -1,
          'left': 7})], 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packAppliedToVehicles(self, data):
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle('#vehicle_customization:customization/tooltip/applied/title'))]
        allowedVehicles = data['allowedVehicles']
        notAllowedVehicles = data['notAllowedVehicles']
        allowedNations = data['allowedNations']
        notAllowedNations = data['notAllowedNations']
        allowedVehicles = map(lambda vId: g_itemsCache.items.getItemByCD(vId), allowedVehicles)
        notAllowedVehicles = map(lambda vId: g_itemsCache.items.getItemByCD(vId), notAllowedVehicles)
        allowedVehicles = filter(lambda vehicle: not vehicle.isSecret, allowedVehicles)
        notAllowedVehicles = filter(lambda vehicle: not vehicle.isSecret, notAllowedVehicles)
        if data['boundToCurrentVehicle']:
            description = _ms('#tooltips:customization/questAward/currentVehicle')
        elif allowedVehicles:
            description = self._getVehiclesNames(allowedVehicles)
        else:
            if allowedNations:
                if len(allowedNations) > len(notAllowedNations):
                    description = _ms('#vehicle_customization:customization/tooltip/applied/allNations')
                    description += _ms('#vehicle_customization:customization/tooltip/applied/elementsSeparator')
                    description += _ms('#vehicle_customization:customization/tooltip/applied/excludeNations', nations=self._getNationNames(notAllowedNations))
                else:
                    description = _ms('#vehicle_customization:customization/tooltip/applied/vehicleNation', nation=self._getNationNames(allowedNations))
            elif self._item.getNationID() == ANY_NATION:
                description = _ms('#vehicle_customization:customization/tooltip/applied/allNations')
            else:
                description = _ms('#vehicle_customization:customization/tooltip/applied/vehicleNation', nation=self._getNationNames([self._item.getNationID()]))
            if notAllowedVehicles:
                description += _ms('#vehicle_customization:customization/tooltip/applied/elementsSeparator')
                description += _ms('#vehicle_customization:customization/tooltip/applied/excludeVehicles', vehicles=self._getVehiclesNames(notAllowedVehicles))
        subBlocks.append(formatters.packTextBlockData(text_styles.main(description)))
        return formatters.packBuildUpBlockData(subBlocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE)

    def _packWayToBuyBlock(self, data):
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle(_ms('#vehicle_customization:customization/tooltip/wayToBuy/title')), padding={'bottom': 6})]
        for buyItem in data['buyItems']:
            buyItemDesc = text_styles.main(buyItem['desc'])
            if buyItem['type'] == BUY_ITEM_TYPE.WAYS_TO_BUY_MISSION:
                subBlocks.append(formatters.packImageTextBlockData(desc=buyItemDesc, img=RES_ICONS.MAPS_ICONS_LIBRARY_QUEST_ICON, imgPadding={'left': 53,
                 'top': 3}, txtGap=-4, txtOffset=73))
            if buyItem['type'] == BUY_ITEM_TYPE.WAYS_TO_BUY_FOREVER:
                if buyItem['isSale']:
                    subBlocks.append(formatters.packSaleTextParameterBlockData(name=buyItemDesc, saleData={'newPrice': (0, buyItem['value'])}, padding={'left': 0}))
                else:
                    price = text_styles.concatStylesWithSpace(text_styles.gold(BigWorld.wg_getIntegralFormat(long(buyItem['value']))), icons.gold())
                    subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=price, valueWidth=70))
            if buyItem['type'] == BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP:
                if buyItem['isSale']:
                    subBlocks.append(formatters.packSaleTextParameterBlockData(name=buyItemDesc, saleData={'newPrice': (buyItem['value'], 0)}, padding={'left': 0}))
                else:
                    price = text_styles.concatStylesWithSpace(text_styles.credits(BigWorld.wg_getIntegralFormat(long(buyItem['value']))), icons.credits())
                    subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=price, valueWidth=70))
            if buyItem['type'] == BUY_ITEM_TYPE.WAYS_TO_BUY_IGR:
                subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=icons.premiumIgrSmall(), padding={'left': 0}))

        return formatters.packBuildUpBlockData(subBlocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, {'left': 3})

    def _packAlreadyHaveBlock(self, data):
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle(_ms('#vehicle_customization:customization/tooltip/alreadyHave/title')), padding={'bottom': 6})]
        padding = {'left': 10}
        for buyItem in data['buyItems']:
            buyItemDesc = text_styles.main(buyItem['desc'])
            if buyItem['type'] == BUY_ITEM_TYPE.ALREADY_HAVE_IGR:
                subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=icons.premiumIgrSmall(), padding=padding))
            subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value='', padding=padding))

        return formatters.packBuildUpBlockData(subBlocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, {'left': 3})

    def _packDescBlock(self, data):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(_ms('#vehicle_customization:customization/tooltip/description/history/title')), desc=text_styles.standard(data['description']), txtGap=8)

    def _packConditionBlock(self, data):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(_ms('#vehicle_customization:customization/tooltip/description/conditions/title')), desc=text_styles.standard('*{0}'.format(data['condition'])), txtGap=8)

    def _packStatusBlock(self, data):
        status = ''
        if data['status'] == STATUS.ON_BOARD:
            status = text_styles.statInfo(_ms('#vehicle_customization:customization/tooltip/status/onBoard'))
        elif data['status'] == STATUS.ALREADY_HAVE:
            status = text_styles.statInfo(_ms('#vehicle_customization:customization/tooltip/status/alreadyHave'))
        elif data['status'] == STATUS.AVAILABLE_FOR_BUY:
            status = text_styles.warning(_ms('#vehicle_customization:customization/tooltip/status/availableForBuy'))
        elif data['status'] == STATUS.DO_MISSION:
            status = text_styles.warning(_ms('#vehicle_customization:customization/tooltip/status/doMission'))
        elif data['status'] == STATUS.DO_IGR:
            status = icons.premiumIgrBig()
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': status}), padding={'bottom': -4,
         'top': -4})

    def _getItemData(self):
        buyItems, wasBought, status = self._getObtainMethod()
        data = {'type': self._itemType,
         'title': self._item.getName(),
         'itemsCount': self._item.numberOfItems,
         'icon': self._item.getTexturePath(),
         'bonus_icon': self._item.qualifier.getIcon42x42(),
         'bonus_title_local': self._item.qualifier.getFormattedValue(),
         'bonus_desc': self._item.qualifier.getExtendedName(),
         'condition': self._item.qualifier.getDescription(),
         'allowedVehicles': self._item.allowedVehicles,
         'notAllowedVehicles': self._item.notAllowedVehicles,
         'allowedNations': self._item.allowedNations,
         'notAllowedNations': self._item.notAllowedNations,
         'boundToCurrentVehicle': False,
         'wasBought': wasBought,
         'buyItems': buyItems,
         'status': status,
         'description': self._item.getDescription(),
         'groupName': self._item.getGroupName()}
        return data

    def _getNationNames(self, nationIds):
        nationNames = map(lambda id: _ms('#nations:{0}'.format(nations.AVAILABLE_NAMES[id])), nationIds)
        return _ms('#vehicle_customization:customization/tooltip/applied/elementsSeparator').join(nationNames)

    def _getVehiclesNames(self, vehicles):
        vehiclesNames = map(lambda vehicle: vehicle.userName, vehicles)
        return _ms('#vehicle_customization:customization/tooltip/applied/elementsSeparator').join(vehiclesNames)

    def __isInstalled(self):
        if self.__slotIdx < 0:
            slotIdx = g_customizationController.carousel.currentSlotIdx
        else:
            slotIdx = self.__slotIdx
        selectedSlotItemID = g_customizationController.carousel.slots.getInstalledItem(slotIdx, self._itemType).getID()
        return selectedSlotItemID == self._item.getID()

    def __isInQuest(self):
        """Check if item is a quest award in a ~current~ view.
        
        In case of carousel, returns True only if current purchase type is Quest.
        In case of slots, returns True only if item has been put there in state of
        quest award.
        Return False otherwise.
        """
        if self.__slotIdx < 0:
            purchaseType = g_customizationController.carousel.filter.purchaseType
            return purchaseType == PURCHASE_TYPE.QUEST and self._item.isInQuests
        else:
            slotsData = g_customizationController.carousel.slots.getData()
            slotItem = slotsData['data'][self._itemType]['data'][self.__slotIdx]
            return slotItem['purchaseTypeIcon'] == RES_ICONS.MAPS_ICONS_LIBRARY_QUEST_ICON

    def __obtainedFromIgr(self):
        """Check if item can be obtained by IRG.
        
        Returns:
            A tuple (buyItems, wasBough, status) where:
            buyItems - a list of different ways this item can be bought;
            wasBought - specifies if item is already bought;
            status - one of the STATUS constants
        """
        if self._item.getIgrType() == getIGRCtrl().getRoomType():
            buyItems = [{'value': 0,
              'type': BUY_ITEM_TYPE.ALREADY_HAVE_IGR,
              'isSale': False,
              'desc': _ms('#vehicle_customization:customization/tooltip/alreadyHave/igr')}]
            wasBought = True
            status = STATUS.ON_BOARD if self.__isInstalled() else STATUS.ALREADY_HAVE
        else:
            buyItems = [{'value': 0,
              'type': BUY_ITEM_TYPE.WAYS_TO_BUY_IGR,
              'isSale': False,
              'desc': _ms('#vehicle_customization:customization/tooltip/wayToBuy/igr')}]
            wasBought = False
            status = STATUS.DO_IGR
        return (buyItems, wasBought, status)

    def __obtainedInSlot(self):
        """Check if item was bought and is installed in slot.
        
        Returns:
            A tuple (buyItems, wasBough, status) where:
            buyItems - a list of different ways this item can be bought;
            wasBought - specifies if item is already bought;
            status - one of the STATUS constants
        """
        days = g_customizationController.carousel.slots.getInstalledItem(self.__slotIdx, self._itemType).duration
        leftDays = g_customizationController.carousel.slots.getInstalledItem(self.__slotIdx, self._itemType).getNumberOfDaysLeft()
        buyItems = [{'value': 0,
          'type': BUY_ITEM_TYPE.ALREADY_HAVE_TEMP,
          'isSale': False,
          'desc': _ms('#customization:tooltip/element/purchase/acquired/days', total=days, left=leftDays)}]
        return (buyItems, True, STATUS.ON_BOARD)

    def __obtainedInDossier(self):
        """Check if item was bought.
        
        Returns:
            A tuple (buyItems, wasBough, status) where:
            buyItems - a list of different ways this item can be bought;
            wasBought - specifies if item is already bought;
            status - one of the STATUS constants
        """
        buyItem = {'value': 0,
         'isSale': False}
        if self._item.numberOfDays is not None:
            buyItem['type'] = BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP
            buyItem['desc'] = _ms('#vehicle_customization:customization/tooltip/wayToBuy/temp', days=self._item.numberOfDays)
        else:
            buyItem['type'] = BUY_ITEM_TYPE.ALREADY_HAVE_FOREVER
            buyItem['desc'] = _ms('#vehicle_customization:customization/tooltip/wayToBuy/forever')
        status = STATUS.ON_BOARD if self.__isInstalled() else STATUS.ALREADY_HAVE
        return ([buyItem], True, status)

    def __notObtained(self):
        """Check if item is obtainable from quests or from the shop.
        
        Returns:
            A tuple (buyItems, wasBough, status) where:
            buyItems - a list of different ways this item can be bought;
            wasBought - specifies if item is already bought;
            status - one of the STATUS constants
        """
        buyItems = []
        if self.__isInQuest():
            status = STATUS.DO_MISSION
            incompleteQuestItems = g_customizationController.dataAggregator.associatedQuests
            questName = incompleteQuestItems[self._itemType][self._item.getID()].name
            buyItems.append({'type': BUY_ITEM_TYPE.WAYS_TO_BUY_MISSION,
             'desc': _ms('#vehicle_customization:customization/tooltip/taskDescription', name=questName)})
        else:
            status = STATUS.AVAILABLE_FOR_BUY
            for duration in DURATION.ALL:
                if duration == DURATION.PERMANENT:
                    buyString = 'forever'
                    wayToBuy = BUY_ITEM_TYPE.WAYS_TO_BUY_FOREVER
                else:
                    buyString = 'temp'
                    wayToBuy = BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP
                buyItems.append({'value': self._item.getPrice(duration),
                 'type': wayToBuy,
                 'isSale': self._item.isSale(duration),
                 'desc': _ms('#vehicle_customization:customization/tooltip/wayToBuy/{0}'.format(buyString), days=duration)})

        return (buyItems, False, status)


class QuestCustomizationItemTooltip(CustomizationItemTooltip):
    """Tooltip data provider for the customization elements in event window.
    """

    def __init__(self, context):
        super(QuestCustomizationItemTooltip, self).__init__(context)
        self.__duration = 0
        self.__isPermanent = False
        self.__boundToVehicle = None
        self.__boundToCurrentVehicle = False
        self.__itemsCount = 0
        return

    def _getObtainMethod(self):
        return ([], False, STATUS.DO_MISSION)

    def _getItemData(self):
        data = super(QuestCustomizationItemTooltip, self)._getItemData()
        if self.__boundToVehicle is not None:
            data['allowedVehicles'].append(self.__boundToVehicle)
        data['boundToCurrentVehicle'] = self.__boundToCurrentVehicle
        data['itemsCount'] = self.__itemsCount
        return data

    def _packBlocks(self, itemType, itemId, nationId, duration, isPermanent=False, itemsCount=None, isUsed=False, boundToVehicle=None, boundToCurrentVehicle=False):
        items = []
        self._item = g_customizationController.dataAggregator.createElement(itemId, itemType, nationId)
        self._itemType = itemType
        self.__duration = duration
        self.__itemsCount = self.__getStoredCount()
        self.__isPermanent = isPermanent
        self.__boundToVehicle = boundToVehicle
        self.__boundToCurrentVehicle = boundToCurrentVehicle
        data = self._getItemData()
        items.append(self._packTitleBlock(data))
        items.append(self._packIconBlock(data))
        items.append(self._packBonusBlock(data))
        if data['condition'] is not None and data['type'] != CUSTOMIZATION_TYPE.CAMOUFLAGE:
            items.append(self._packConditionBlock(data))
        items.append(self._packAppliedToVehicles(data))
        items.append(self._packDurationBlock())
        if data['description'] is not None:
            items.append(self._packDescBlock(data))
        items.append(self._packStatusBlock(data))
        return items

    def _packDurationBlock(self):
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle('#vehicle_customization:timeLeft/title'))]
        if self.__isPermanent:
            duration = _ms('#vehicle_customization:timeLeft/infinity')
        else:
            dimension = _ms('#vehicle_customization:timeLeft/temporal/days')
            duration = _ms('#vehicle_customization:timeLeft/temporal/used', time=self.__duration / 60 / 60 / 24, dimension=dimension)
        subBlocks.append(formatters.packTextBlockData(text_styles.main(duration)))
        return formatters.packBuildUpBlockData(subBlocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE)

    def __getStoredCount(self):
        inventoryItems = g_customizationController.dataAggregator.getInventoryItems(self._nationId)
        if self._item.getID() in inventoryItems[self._itemType]:
            item = inventoryItems[self._itemType][self._item.getID()]
            isGold, itemNum = item[6]
            if isGold:
                return itemNum
        return None
