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
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization import g_customizationController as controller
from gui.customization.shared import DURATION, CUSTOMIZATION_TYPE, PURCHASE_TYPE
from gui.server_events.finders import getPersonalMissionDataFromToken
from gui.shared.formatters import text_styles, icons
from gui.shared.items_parameters import params_helper, formatters as params_formatters
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.i18n import makeString as _ms
from nations import NONE_INDEX as ANY_NATION
from shared_utils import first
from skeletons.gui.game_control import IIGRController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class STATUS(object):
    NONE = 0
    ON_BOARD = 1
    ALREADY_HAVE = 2
    AVAILABLE_FOR_BUY = 3
    DO_MISSION = 4
    DO_IGR = 5
    DO_OPERATION = 6


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
            blocks.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(MENU.tank_params(parameter.name)), valueStr=params_formatters.simlifiedDeltaParameter(parameter), statusBarData=SimplifiedBarVO(value=value, delta=delta, markerValue=self.__stockParams[parameter.name]), padding=formatters.packPadding(left=72, top=8)))

        return blocks


class ElementTooltip(BlocksTooltipData):
    """Tooltip data provider for the customization elements in customization windows.
    """
    itemsCache = dependency.descriptor(IItemsCache)
    igrCtrl = dependency.descriptor(IIGRController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __MAX_QUESTS_TO_SHOW = 3

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
        if self._item is None:
            return []
        else:
            data = self._getItemData()
            if self.__isInQuest():
                data['itemsCount'] = None
            items.append(self._packTitleBlock(data))
            items.append(self._packIconBlock(data))
            if data['bonus_value'] > 0:
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
            title += _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_ALREADYHAVE_COUNT, count=itemsCount)
        typeText = ''
        if self._cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            typeText = _ms('#vehicle_customization:camouflage')
        elif self._cType == CUSTOMIZATION_TYPE.EMBLEM:
            typeText = _ms('#vehicle_customization:emblem')
        elif self._cType == CUSTOMIZATION_TYPE.INSCRIPTION:
            typeText = _ms('#vehicle_customization:inscription')
        typeText += ' ' + _ms(data['groupName'])
        title = text_styles.highTitle(title)
        desc = text_styles.main(typeText)
        img = RES_ICONS.MAPS_ICONS_LIBRARY_QUALIFIERS_42X42_CAMOUFLAGE
        imgPadding = formatters.packPadding(7, 5, 0, 20)
        questListData = controller.dataAggregator.getQuestData(self._cType, self._item)
        if questListData:
            questData = first(questListData)
            if questData and getPersonalMissionDataFromToken(questData.requiredToken)[0]:
                return formatters.packItemTitleDescBlockData(title=title, desc=desc, img=img, imgPadding=imgPadding, overlayPath=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_BRUSH_RARE, overlayPadding=formatters.packPadding(-13, -17), highlightPath=RES_ICONS.MAPS_ICONS_CUSTOMIZATION_CORNER_RARE, highlightPadding=formatters.packPadding(-22, -25), padding={'top': -5,
                 'bottom': -19})
        return formatters.packItemTitleDescBlockData(title=title, desc=desc, img=img, imgPadding=imgPadding, padding={'top': -5,
         'bottom': -4})

    def _packIconBlock(self, data):
        actualWidth = 84
        if self._cType == CUSTOMIZATION_TYPE.INSCRIPTION:
            actualWidth = 176
        return formatters.packImageBlockData(img=data['icon'], align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=actualWidth, height=84, padding={'top': 2,
         'bottom': 4})

    def _packBonusBlock(self, data):
        vehicle = g_currentVehicle.item
        blocks = []
        conditionBonus = data['condition'] is not None and data['type'] != CUSTOMIZATION_TYPE.CAMOUFLAGE
        bonusTitleLocal = makeHtmlString('html_templates:lobby/textStyle', 'bonusLocalText', {'message': '{0}{1}'.format(data['bonus_title_local'], '*' if conditionBonus else '')})
        blocks.append(formatters.packImageTextBlockData(title=text_styles.concatStylesWithSpace(bonusTitleLocal), desc=text_styles.main(data['bonus_desc']), img=data['bonus_icon'], imgPadding={'left': 11,
         'top': 3}, txtGap=-4, txtOffset=70, padding={'top': -1,
         'left': 7}))
        if data['showTTC'] and vehicle is not None and self._cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            stockVehicle = self.itemsCache.items.getStockVehicle(vehicle.intCD)
            comparator = params_helper.camouflageComparator(vehicle, self._item)
            stockParams = params_helper.getParameters(stockVehicle)
            simplifiedBlocks = SimplifiedStatsBlockConstructor(stockParams, comparator).construct()
            if simplifiedBlocks:
                blocks.extend(simplifiedBlocks)
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packAppliedToVehicles(self, data):
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_TITLE))]
        allowedVehicles = data['allowedVehicles']
        notAllowedVehicles = data['notAllowedVehicles']
        allowedNations = data['allowedNations']
        notAllowedNations = data['notAllowedNations']
        allowedVehicles = map(lambda vId: self.itemsCache.items.getItemByCD(vId), allowedVehicles)
        notAllowedVehicles = map(lambda vId: self.itemsCache.items.getItemByCD(vId), notAllowedVehicles)
        allowedVehicles = filter(lambda vehicle: not vehicle.isSecret, allowedVehicles)
        notAllowedVehicles = filter(lambda vehicle: not vehicle.isSecret, notAllowedVehicles)
        if data['boundToCurrentVehicle']:
            description = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_QUESTAWARD_CURRENTVEHICLE)
        elif allowedVehicles:
            description = self._getVehiclesNames(allowedVehicles)
        else:
            if allowedNations:
                if len(allowedNations) > len(notAllowedNations):
                    description = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_ALLNATIONS)
                    description += _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_ELEMENTSSEPARATOR)
                    description += _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_EXCLUDENATIONS, nations=self._getNationNames(notAllowedNations))
                else:
                    description = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_VEHICLENATION, nation=self._getNationNames(allowedNations))
            elif self._item.getNationID() == ANY_NATION:
                description = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_ALLNATIONS)
            else:
                description = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_VEHICLENATION, nation=self._getNationNames([self._item.getNationID()]))
            if notAllowedVehicles:
                description += _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_ELEMENTSSEPARATOR)
                description += _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_EXCLUDEVEHICLES, vehicles=self._getVehiclesNames(notAllowedVehicles))
        subBlocks.append(formatters.packTextBlockData(text_styles.main(description)))
        return formatters.packBuildUpBlockData(subBlocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE)

    def _packWayToBuyBlock(self, data):
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_TITLE), padding={'bottom': 6})]
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
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_ALREADYHAVE_TITLE), padding={'bottom': 6})]
        padding = {'left': 10}
        for buyItem in data['buyItems']:
            buyItemDesc = text_styles.main(buyItem['desc'])
            if buyItem['type'] == BUY_ITEM_TYPE.ALREADY_HAVE_IGR:
                subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value=icons.premiumIgrSmall(), padding=padding))
            subBlocks.append(formatters.packTextParameterBlockData(name=buyItemDesc, value='', padding=padding))

        return formatters.packBuildUpBlockData(subBlocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, {'left': 3})

    def _packDescBlock(self, data):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_DESCRIPTION_HISTORY_TITLE), desc=text_styles.standard(data['description']), txtGap=8)

    def _packConditionBlock(self, data):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_DESCRIPTION_CONDITIONS_TITLE), desc=text_styles.standard('*{0}'.format(data['condition'])), txtGap=8)

    def _packStatusBlock(self, data):
        status = ''
        if data['status'] == STATUS.ON_BOARD:
            status = text_styles.statInfo(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_STATUS_ONBOARD)
        elif data['status'] == STATUS.ALREADY_HAVE:
            status = text_styles.statInfo(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_STATUS_ALREADYHAVE)
        elif data['status'] == STATUS.AVAILABLE_FOR_BUY:
            status = text_styles.warning(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_STATUS_AVAILABLEFORBUY)
        elif data['status'] == STATUS.DO_MISSION:
            status = text_styles.warning(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_STATUS_DOMISSION)
        elif data['status'] == STATUS.DO_OPERATION:
            status = text_styles.warning(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_STATUS_DOOPERATION)
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
         'bonus_value': self._item.qualifier.getValue(),
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
        return _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_ELEMENTSSEPARATOR).join(nationNames)

    def _getVehiclesNames(self, vehicles):
        vehiclesNames = map(lambda vehicle: vehicle.userName, vehicles)
        return _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_ELEMENTSSEPARATOR).join(vehiclesNames)

    def __isInstalled(self):
        if self._slotIdx < 0:
            slotIdx = controller.slots.currentSlotIdx
        else:
            slotIdx = self._slotIdx
        selectedSlotElement = controller.slots.getInstalledSlotData(slotIdx, self._cType)['element']
        return False if selectedSlotElement is None else selectedSlotElement.getID() == self._item.getID()

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
              'desc': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_APPLIED_ELEMENTSSEPARATOR)}]
            wasBought = True
            status = STATUS.ON_BOARD if self.__isInstalled() else STATUS.ALREADY_HAVE
        else:
            buyItems = [{'value': 0,
              'type': BUY_ITEM_TYPE.WAYS_TO_BUY_IGR,
              'isSale': False,
              'desc': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_IGR)}]
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
          'desc': _ms(VEHICLE_CUSTOMIZATION.TOOLTIP_ELEMENT_PURCHASE_ACQUIRED_DAYS, total=days, left=leftDays)}]
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
        wasBought = True
        if self._item.numberOfDays is not None:
            buyItem['type'] = BUY_ITEM_TYPE.WAYS_TO_BUY_TEMP
            buyItem['desc'] = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_TEMP, days=self._item.numberOfDays)
        else:
            buyItem['type'] = BUY_ITEM_TYPE.ALREADY_HAVE_FOREVER
            questData = first(controller.dataAggregator.getQuestData(self._cType, self._item))
            buyItem['desc'] = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_WAYTOBUY_FOREVER)
            if questData:
                isBelongToPM, operationID, isMain = getPersonalMissionDataFromToken(questData.requiredToken)
                if isBelongToPM:
                    operation = self.__eventsCache.personalMissions.getOperations()[operationID]
                    if isMain:
                        key = TOOLTIPS.PERSONALMISSIONS_RARECAMOUFLAGE_OBTAINED_COMPLETE_MAIN
                    else:
                        key = TOOLTIPS.PERSONALMISSIONS_RARECAMOUFLAGE_OBTAINED_COMPLETE_ADD
                    wasBought = False
                    buyItem['type'] = BUY_ITEM_TYPE.WAYS_TO_BUY_MISSION
                    buyItem['desc'] = _ms(key, operationName=operation.getShortUserName())
        status = STATUS.ON_BOARD if self.__isInstalled() else STATUS.ALREADY_HAVE
        return ([buyItem], wasBought, status)

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
            questsData = controller.dataAggregator.getQuestData(self._cType, self._item)
            isBelongToPM, operationID, isMain = getPersonalMissionDataFromToken(first(questsData).requiredToken)
            if isBelongToPM:
                status = STATUS.DO_OPERATION
                operation = self.__eventsCache.personalMissions.getOperations()[operationID]
                if isMain:
                    label = TOOLTIPS.PERSONALMISSIONS_RARECAMOUFLAGE_NOTOBTAINED_MAININCOMPLETE_TITLE
                    completedQuestsCount = len(operation.getCompletedQuests())
                else:
                    label = TOOLTIPS.PERSONALMISSIONS_RARECAMOUFLAGE_NOTOBTAINED_ADDINCOMPLETE_TITLE
                    completedQuestsCount = len(operation.getFullCompletedQuests())
                totalCount = operation.getQuestsCount()
                countLabel = '%s / %s ' % (text_styles.stats(completedQuestsCount), totalCount)
                text = text_styles.main(_ms(label, operationName=operation.getShortUserName(), countLabel=text_styles.main(countLabel)))
                buyItems.append({'type': BUY_ITEM_TYPE.WAYS_TO_BUY_MISSION,
                 'desc': text})
            else:
                status = STATUS.DO_MISSION
                questsNames = ', '.join(map(lambda q: q.name, questsData[:self.__MAX_QUESTS_TO_SHOW]))
                questsCount = len(questsData)
                if questsCount == 1:
                    descriptionKey = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_ONETASKDESCRIPTION
                else:
                    descriptionKey = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_TASKDESCRIPTION
                description = [_ms(descriptionKey, name=questsNames)]
                if questsCount > self.__MAX_QUESTS_TO_SHOW:
                    description.append(text_styles.stats(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_TASKDESCRIPTION_OTHER, count=questsCount - self.__MAX_QUESTS_TO_SHOW)))
                buyItems.append({'type': BUY_ITEM_TYPE.WAYS_TO_BUY_MISSION,
                 'desc': ' '.join(description)})
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
        return ([{'value': 0,
           'isSale': False}], True, STATUS.NONE) if self.__isReceived else ([], False, STATUS.DO_MISSION)

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
        if data['bonus_value'] > 0:
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
        subBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle(VEHICLE_CUSTOMIZATION.TIMELEFT_TITLE))]
        if self.__isPermanent:
            duration = _ms(VEHICLE_CUSTOMIZATION.TIMELEFT_INFINITY)
        else:
            dimension = _ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_DAYS)
            duration = _ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_USED, time=self.__duration / 60 / 60 / 24, dimension=dimension)
        subBlocks.append(formatters.packTextBlockData(text_styles.main(duration)))
        return formatters.packBuildUpBlockData(subBlocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE)
