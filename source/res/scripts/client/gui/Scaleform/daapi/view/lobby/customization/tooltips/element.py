# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/tooltips/element.py
import BigWorld
import nations
from CurrentVehicle import g_currentVehicle
from constants import IGR_TYPE
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.customization import g_customizationController as controller
from gui.customization.shared import DURATION, CUSTOMIZATION_TYPE, PURCHASE_TYPE
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles, icons
from gui.shared.items_parameters import params_helper, MAX_RELATIVE_VALUE, formatters as params_formatters
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.i18n import makeString as _ms
from nations import NONE_INDEX as ANY_NATION
from skeletons.gui.game_control import IIGRController

class STATUS(object):
    NONE = 0
    ON_BOARD = 1
    ALREADY_HAVE = 2
    AVAILABLE_FOR_BUY = 3
    DO_MISSION = 4
    DO_IGR = 5


class BUY_ITEM_TYPE(object):
    NONE = 0
    WAYS_TO_BUY_FOREVER = 2
    WAYS_TO_BUY_TEMP = 3
    WAYS_TO_BUY_IGR = 4
    WAYS_TO_BUY_MISSION = 5
    ALREADY_HAVE_FOREVER = 6
    ALREADY_HAVE_TEMP = 7
    ALREADY_HAVE_IGR = 8


class SimplifiedStatsBlockConstructor(object):

    def __init__(self, stockParams, comparator):
        self.__stockParams = stockParams
        self.__comparator = comparator

    def construct(self):
        blocks = []
        for parameter in params_formatters.getRelativeDiffParams(self.__comparator):
            delta = parameter.state[1]
            value = parameter.value
            if delta > 0:
                value -= delta
            blocks.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(MENU.tank_params(parameter.name)), valueStr=params_formatters.simlifiedDeltaParameter(parameter), statusBarData={'value': value,
             'delta': delta,
             'minValue': 0,
             'markerValue': self.__stockParams[parameter.name],
             'maxValue': MAX_RELATIVE_VALUE,
             'useAnim': False}, padding=formatters.packPadding(left=72, top=8)))

        return blocks


class ElementTooltip(BlocksTooltipData):
    """Tooltip data provider for the customization elements in customization windows.
    """
    igrCtrl = dependency.descriptor(IIGRController)

    def __init__(self, context):
        super(ElementTooltip, self).__init__(context, TOOLTIP_TYPE.TECH_CUSTOMIZATION)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(330)
        self._item = None
        self._cType = 0
        self._nationId = 0
        self._slotIdx = -1
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
            self._item = controller.carousel.items[args[0]]['element']
            self._cType = controller.slots.currentType
            self._slotIdx = -1
        else:
            self._slotIdx, self._cType = args[:2]
            self._item = controller.slots.getCurrentSlotData(self._slotIdx, self._cType)['element']
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
        if data['status'] != STATUS.NONE:
            items.append(self._packStatusBlock(data))
        return items

    def _packTitleBlock(self, data):
        title = data['title']
        itemsCount = data['itemsCount']
        if itemsCount is not None and itemsCount > 1:
            title += _ms('#vehicle_customization:customization/tooltip/alreadyHave/count', count=itemsCount)
        typeText = ''
        if self._cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            typeText = _ms('#vehicle_customization:camouflage')
        elif self._cType == CUSTOMIZATION_TYPE.EMBLEM:
            typeText = _ms('#vehicle_customization:emblem')
        elif self._cType == CUSTOMIZATION_TYPE.INSCRIPTION:
            typeText = _ms('#vehicle_customization:inscription')
        typeText += ' ' + _ms(data['groupName'])
        return formatters.packImageTextBlockData(title=text_styles.highTitle(title), padding={'top': -5}, desc=text_styles.main(typeText))

    def _packIconBlock(self, data):
        actualWidth = 84
        if self._cType == CUSTOMIZATION_TYPE.INSCRIPTION:
            actualWidth = 176
        return formatters.packImageBlockData(img=data['icon'], align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=actualWidth, height=84)

    def _packBonusBlock(self, data):
        vehicle = g_currentVehicle.item
        blocks = []
        conditionBonus = data['condition'] is not None and data['type'] != CUSTOMIZATION_TYPE.CAMOUFLAGE
        bonusTitleLocal = makeHtmlString('html_templates:lobby/textStyle', 'bonusLocalText', {'message': '{0}{1}'.format(data['bonus_title_local'], '*' if conditionBonus else '')})
        blocks.append(formatters.packImageTextBlockData(title=text_styles.concatStylesWithSpace(bonusTitleLocal), desc=text_styles.main(data['bonus_desc']), img=data['bonus_icon'], imgPadding={'left': 11,
         'top': 3}, txtGap=-4, txtOffset=70, padding={'top': -1,
         'left': 7}))
        if data['showTTC'] and vehicle is not None and self._cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            stockVehicle = g_itemsCache.items.getStockVehicle(vehicle.intCD)
            comparator = params_helper.camouflageComparator(vehicle, self._item)
            stockParams = params_helper.getParameters(stockVehicle)
            simplifiedBlocks = SimplifiedStatsBlockConstructor(stockParams, comparator).construct()
            if len(simplifiedBlocks) > 0:
                blocks.extend(simplifiedBlocks)
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

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
            description = _ms('#vehicle_customization:customization/questAward/currentVehicle')
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
        data = {'type': self._cType,
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
         'groupName': self._item.getGroupName(),
         'showTTC': True}
        return data

    def _getNationNames(self, nationIds):
        nationNames = map(lambda id: _ms('#nations:{0}'.format(nations.AVAILABLE_NAMES[id])), nationIds)
        return _ms('#vehicle_customization:customization/tooltip/applied/elementsSeparator').join(nationNames)

    def _getVehiclesNames(self, vehicles):
        vehiclesNames = map(lambda vehicle: vehicle.userName, vehicles)
        return _ms('#vehicle_customization:customization/tooltip/applied/elementsSeparator').join(vehiclesNames)

    def __isInstalled(self):
        if self._slotIdx < 0:
            slotIdx = controller.slots.currentSlotIdx
        else:
            slotIdx = self._slotIdx
        selectedSlotElement = controller.slots.getInstalledSlotData(slotIdx, self._cType)['element']
        if selectedSlotElement is None:
            return False
        else:
            return selectedSlotElement.getID() == self._item.getID()
            return

    def __isInQuest(self):
        """Check if item is a quest award in a ~current~ view.
        
        In case of carousel, returns True only if current purchase type is Quest.
        In case of slots, returns True only if item has been put there in state of
        quest award.
        Return False otherwise.
        """
        if self._slotIdx < 0:
            purchaseType = controller.filter.purchaseType
            return purchaseType == PURCHASE_TYPE.QUEST and self._item.isInQuests
        else:
            slotsData = controller.slots.currentSlotsData
            return slotsData[self._cType][self._slotIdx]['isInQuest']

    def __obtainedFromIgr(self):
        """Check if item can be obtained by IRG.
        
        Returns:
            A tuple (buyItems, wasBough, status) where:
            buyItems - a list of different ways this item can be bought;
            wasBought - specifies if item is already bought;
            status - one of the STATUS constants
        """
        if self._item.getIgrType() == self.igrCtrl.getRoomType():
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
        if self._slotIdx < 0:
            slotIdx = controller.slots.currentSlotIdx
        else:
            slotIdx = self._slotIdx
        days = controller.slots.getInstalledSlotData(slotIdx, self._cType)['duration']
        leftDays = controller.slots.getInstalledSlotData(slotIdx, self._cType)['daysLeft']
        buyItems = [{'value': 0,
          'type': BUY_ITEM_TYPE.ALREADY_HAVE_TEMP,
          'isSale': False,
          'desc': _ms('#vehicle_customization:tooltip/element/purchase/acquired/days', total=days, left=leftDays)}]
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
            incompleteQuestItems = controller.dataAggregator.getIncompleteQuestItems()
            questName = incompleteQuestItems[self._cType][self._item.getID()].name
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
                 'isSale': self._item.isOnSale(duration),
                 'desc': _ms('#vehicle_customization:customization/tooltip/wayToBuy/{0}'.format(buyString), days=duration)})

        return (buyItems, False, status)


class QuestElementTooltip(ElementTooltip):
    """Tooltip data provider for the customization elements in event window.
    """

    def __init__(self, context):
        super(QuestElementTooltip, self).__init__(context)
        self.__duration = 0
        self.__isPermanent = False
        self.__boundToVehicle = None
        self.__boundToCurrentVehicle = False
        self.__isReceived = False
        return

    def _getObtainMethod(self):
        if self.__isReceived:
            return ([{'value': 0,
               'isSale': False}], True, STATUS.NONE)
        else:
            return ([], False, STATUS.DO_MISSION)

    def _getItemData(self):
        data = super(QuestElementTooltip, self)._getItemData()
        if self.__boundToVehicle is not None:
            data['allowedVehicles'].append(self.__boundToVehicle)
        data['boundToCurrentVehicle'] = self.__boundToCurrentVehicle
        data['description'] = None
        data['showTTC'] = False
        return data

    def _packBlocks(self, itemType, itemId, nationId, duration, isPermanent=False, boundToVehicle=None, boundToCurrentVehicle=False, isReceived=True):
        items = []
        self._item = controller.dataAggregator.createElement(itemId, itemType, nationId)
        self._cType = itemType
        self.__duration = duration
        self.__isPermanent = isPermanent
        self.__boundToVehicle = boundToVehicle
        self.__boundToCurrentVehicle = boundToCurrentVehicle
        self.__isReceived = isReceived
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
        if data['status'] != STATUS.NONE:
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
