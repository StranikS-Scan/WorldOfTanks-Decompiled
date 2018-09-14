# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/main_view.py
from CurrentVehicle import g_currentVehicle
from adisp import process
from constants import IGR_TYPE, EVENT_TYPE
from gui import DialogsInterface, makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.CustomizationMainViewMeta import CustomizationMainViewMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization import g_customizationController
from gui.customization.shared import checkInQuest, formatPriceCredits, formatPriceGold, getSalePriceString, DURATION, CUSTOMIZATION_TYPE, QUALIFIER_TYPE, QUALIFIER_TYPE_INDEX, FILTER_TYPE
from gui.server_events import events_dispatcher
from gui.shared import events
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip, getAbsoluteUrl
from helpers import dependency
from helpers.i18n import makeString as _ms
from shared import getDialogRemoveElement, getDialogReplaceElement
from skeletons.gui.game_control import IIGRController
_DURATION_TOOLTIPS = {DURATION.PERMANENT: (VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_ALWAYS, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_LOWERCASE_ALWAYS),
 DURATION.MONTH: (VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_MONTH, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_LOWERCASE_MONTH),
 DURATION.WEEK: (VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_WEEK, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_LOWERCASE_WEEK)}
_SLOT_TYPE_TOOLTIPS = {CUSTOMIZATION_TYPE.CAMOUFLAGE: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SLOT_CAMOUFLAGE,
 CUSTOMIZATION_TYPE.EMBLEM: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SLOT_EMBLEM,
 CUSTOMIZATION_TYPE.INSCRIPTION: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_SLOT_INSCRIPTION}
_EMPTY_SLOTS_ICONS = {CUSTOMIZATION_TYPE.CAMOUFLAGE: (RES_ICONS.MAPS_ICONS_CUSTOMIZATION_SLOTS_EMPTY_CAMOUFLAGE_WINTER, RES_ICONS.MAPS_ICONS_CUSTOMIZATION_SLOTS_EMPTY_CAMOUFLAGE_SUMMER, RES_ICONS.MAPS_ICONS_CUSTOMIZATION_SLOTS_EMPTY_CAMOUFLAGE_DESERT),
 CUSTOMIZATION_TYPE.EMBLEM: RES_ICONS.MAPS_ICONS_CUSTOMIZATION_SLOTS_EMPTY_EMBLEM,
 CUSTOMIZATION_TYPE.INSCRIPTION: RES_ICONS.MAPS_ICONS_CUSTOMIZATION_SLOTS_EMPTY_INSCRIPTION}

def _getSlotsPanelDataVO(slotsData):
    slotsDataVO = {'data': []}
    for cType in CUSTOMIZATION_TYPE.ALL:
        header = text_styles.middleTitle(_ms('#vehicle_customization:typeSwitchScreen/typeName/{0}'.format(cType)))
        selectorSlotsData = []
        for slotIdx in range(0, len(slotsData[cType])):
            selectorSlotsData.append(_getSlotVO(slotsData[cType][slotIdx], cType, slotIdx))

        slotsDataVO['data'].append({'header': header,
         'data': selectorSlotsData})

    return slotsDataVO


def _getSlotVO(slotData, cType, slotIdx):
    if slotData['element'] is None:
        elementID = -1
        if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            slotImage = _EMPTY_SLOTS_ICONS[cType][slotIdx]
        else:
            slotImage = _EMPTY_SLOTS_ICONS[cType]
    else:
        elementID = slotData['element'].getID()
        slotImage = slotData['element'].getTexturePath()
    slotVO = {'itemID': elementID,
     'slotTooltip': makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_SLOT_HEADER, groupName=_ms(_SLOT_TYPE_TOOLTIPS[cType])), TOOLTIPS.CUSTOMIZATION_SLOT_BODY),
     'removeBtnTooltip': makeTooltip(TOOLTIPS.CUSTOMIZATION_SLOTREMOVE_HEADER, TOOLTIPS.CUSTOMIZATION_SLOTREMOVE_BODY),
     'revertBtnVisible': slotData['isRevertible'],
     'revertBtnTooltip': makeTooltip(TOOLTIPS.CUSTOMIZATION_SLOTREVERT_HEADER, TOOLTIPS.CUSTOMIZATION_SLOTREVERT_BODY),
     'spot': slotData['spot'],
     'isInDossier': slotData['isInDossier'],
     'img': slotImage}
    if slotData['element'] is not None:
        slotVO['bonusVisible'] = slotData['element'].qualifier.getValue() > 0
        slotVO['bonus'] = _getSlotBonusString(slotData['element'].qualifier, slotData['isInDossier'])
        if slotData['isInQuest']:
            purchaseTypeIcon = RES_ICONS.MAPS_ICONS_LIBRARY_QUEST_ICON
        elif slotData['duration'] == DURATION.PERMANENT:
            purchaseTypeIcon = RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2
        else:
            purchaseTypeIcon = RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2
        slotVO['purchaseTypeIcon'] = purchaseTypeIcon
        slotVO['duration'] = slotData['duration']
    return slotVO


def _getSlotBonusString(qualifier, isInDossier):
    bonus = makeHtmlString('html_templates:lobby/customization', 'bonusString', {'bonusIcon': getAbsoluteUrl(qualifier.getIcon16x16()),
     'bonusValue': qualifier.getValue(),
     'isConditional': '' if qualifier.getDescription() is None else '*'})
    if not isInDossier:
        bonus = text_styles.bonusAppliedText(bonus)
    return bonus


def _getDurationTypeVO():
    durationTypeVOs = []
    for duration, (tooltipText, tooltipLowercaseText) in _DURATION_TOOLTIPS.items():
        if duration == DURATION.PERMANENT:
            icon = icons.gold()
        else:
            icon = icons.credits()
        label = '{0}{1}'.format(_ms(tooltipText), icon)
        tooltip = makeTooltip(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_HEADER, time=_ms(tooltipText)), _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_BODY, time=_ms(tooltipLowercaseText)))
        tooltipDisabled = makeTooltip(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_HEADER, time=_ms(tooltipText)), VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_DISABLED)
        durationTypeVOs.append({'label': label,
         'tooltip': tooltip,
         'tooltipDisabled': tooltipDisabled})

    return durationTypeVOs


def _createBonusVOList(blData, bonusNameList):
    result = []
    for qTypeName in bonusNameList:
        bonusVO = {'bonusName': blData[qTypeName]['bonusName'],
         'bonusIcon': blData[qTypeName]['bonusIcon'],
         'animationPanel': blData[qTypeName]['animationPanel'],
         'bonusType': qTypeName}
        result.append(bonusVO)

    return result


def _getInvoiceItemDialogMeta(dialogType, cType, carouselItem, l10nExtraParams):
    l10nParams = {'cTypeName': _ms('#vehicle_customization:typeSwitchScreen/typeName/{0}'.format(cType)),
     'itemName': carouselItem.getName()}
    l10nParams.update(l10nExtraParams)
    return I18nConfirmDialogMeta('customization/install_invoice_item/{0}'.format(dialogType), messageCtx=l10nParams, focusedID=DIALOG_BUTTON_ID.CLOSE)


class MainView(CustomizationMainViewMeta):
    igrCtrl = dependency.descriptor(IIGRController)

    def __init__(self, ctx=None):
        super(MainView, self).__init__()
        self.__isCarouselHidden = True
        self.__controller = None
        return

    def showGroup(self, cType, slotIdx):
        self.__controller.slots.select(cType, slotIdx)
        if self.__isCarouselHidden:
            self.__isCarouselHidden = False
            self.__setBottomPanelData()
            self.as_showSelectorItemS(cType)

    def removeSlot(self, cType, slotIdx):
        self.__removeSlot(cType, slotIdx)

    def revertSlot(self, cType, slotIdx):
        self.__controller.slots.dropAppliedItem(cType, slotIdx)

    def backToSelectorGroup(self):
        self.__isCarouselHidden = True
        self.__setBottomPanelData()
        self.as_showSelectorGroupS()
        self.__controller.events.onBackToSelectorGroup()

    def installCustomizationElement(self, idx):
        self.__installElement(idx)

    def setDurationType(self, durationIdx):
        self.__controller.carousel.changeDuration(DURATION.ALL[durationIdx])

    def closeWindow(self):
        if self.__controller.cart.items:
            DialogsInterface.showDialog(I18nConfirmDialogMeta('customization/close'), self.__confirmCloseWindow)
        else:
            self.__confirmCloseWindow(True)

    def showBuyWindow(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def showPurchased(self, value):
        self.__controller.filter.set(FILTER_TYPE.SHOW_IN_DOSSIER, value)

    def goToTask(self, idx):
        item = self.__controller.carousel.items[idx]['element']
        cType = self.__controller.slots.currentType
        quests = self.__controller.dataAggregator.getIncompleteQuestItems()
        questData = quests[cType][item.getID()]
        events_dispatcher.showEventsWindow(eventID=questData.id, eventType=EVENT_TYPE.BATTLE_QUEST)

    def _populate(self):
        super(MainView, self)._populate()
        self.__controller = g_customizationController
        self.__controller.init()
        self.__controller.events.onCartUpdated += self.__setBottomPanelData
        self.__controller.events.onMultiplePurchaseProcessed += self.__onPurchaseProcessed
        self.__controller.events.onCarouselUpdated += self.__setCarouselData
        self.__controller.events.onSlotUpdated += self.__onSlotUpdated
        self.__controller.events.onCartEmptied += self.as_hideBuyingPanelS
        self.__controller.events.onCartFilled += self.as_showBuyingPanelS
        self.__controller.events.onBonusesUpdated += self.__setBonusData
        self.__controller.start()
        self.as_setSlotsPanelDataS(_getSlotsPanelDataVO(self.__controller.slots.currentSlotsData))
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__setBottomPanelData,
         'stats.gold': self.__setBottomPanelData})
        g_currentVehicle.onChanged += self.__setHeaderInitData
        self.__setHeaderInitData()
        self.__setFooterInitData()
        self.__setCarouselInitData()
        self.__setBottomPanelData()
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.HIDE_HANGAR, True))

    def _dispose(self):
        self.__controller.tankModel.applyInitialModelAttributes()
        self.__controller.events.onCartUpdated -= self.__setBottomPanelData
        self.__controller.events.onMultiplePurchaseProcessed -= self.__onPurchaseProcessed
        self.__controller.events.onCarouselUpdated -= self.__setCarouselData
        self.__controller.events.onSlotUpdated -= self.__onSlotUpdated
        self.__controller.events.onCartEmptied -= self.as_hideBuyingPanelS
        self.__controller.events.onCartFilled -= self.as_showBuyingPanelS
        self.__controller.events.onBonusesUpdated -= self.__setBonusData
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__setHeaderInitData
        self.__controller.fini()
        self.__controller = None
        super(MainView, self)._dispose()
        return

    def __onSlotUpdated(self, newSlotData, cType, slotIdx):
        slotVo = _getSlotVO(newSlotData, cType, slotIdx)
        self.as_updateSlotS({'data': slotVo,
         'type': cType,
         'idx': slotIdx})

    def __onCustomizationQuestsUpdated(self, incompleteQuestItems):
        self.__incompleteQuestItems = incompleteQuestItems

    def __setBottomPanelData(self, *args):
        if self.__isCarouselHidden:
            occupiedSlotsNum, totalSlotsNum = self.__controller.slots.getSummary()
            label = text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.TYPESWITCHSCREEN_SLOTSUMMARY, occupiedSlotsNum=occupiedSlotsNum, totalSlotsNum=totalSlotsNum))
        else:
            label = text_styles.middleTitle(_ms('#vehicle_customization:typeSwitchScreen/typeName/plural/{0}'.format(self.__controller.slots.currentType)))
        totalGold = self.__controller.cart.totalPriceGold
        totalCredits = self.__controller.cart.totalPriceCredits
        notEnoughGoldTooltip = notEnoughCreditsTooltip = ''
        enoughGold = g_itemsCache.items.stats.gold >= totalGold
        enoughCredits = g_itemsCache.items.stats.credits >= totalCredits
        if not enoughGold:
            diff = text_styles.gold(totalGold - g_itemsCache.items.stats.gold)
            notEnoughGoldTooltip = makeTooltip(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTENOUGHRESOURCES_HEADER), _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTENOUGHRESOURCES_BODY, count='{0}{1}'.format(diff, icons.gold())))
        if not enoughCredits:
            diff = text_styles.credits(totalCredits - g_itemsCache.items.stats.credits)
            notEnoughCreditsTooltip = makeTooltip(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTENOUGHRESOURCES_HEADER), _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NOTENOUGHRESOURCES_BODY, count='{0}{1}'.format(diff, icons.credits())))
        self.as_setBottomPanelHeaderS({'newHeaderText': label,
         'buyBtnLabel': _ms(MENU.CUSTOMIZATION_BUTTONS_APPLY, count=len(self.__controller.cart.items)),
         'pricePanel': {'totalPriceCredits': formatPriceCredits(totalCredits),
                        'totalPriceGold': formatPriceGold(totalGold),
                        'enoughGold': enoughGold,
                        'enoughCredits': enoughCredits,
                        'notEnoughGoldTooltip': notEnoughGoldTooltip,
                        'notEnoughCreditsTooltip': notEnoughCreditsTooltip}})

    def __setHeaderInitData(self):
        isElite = g_currentVehicle.item.isElite
        vTypeId = g_currentVehicle.item.type
        vTypeId = '{0}_elite'.format(vTypeId) if isElite else vTypeId
        self.as_setHeaderDataS({'titleText': text_styles.promoTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATIONHEADER_TITLE),
         'tankName': text_styles.promoSubTitle(g_currentVehicle.item.userName),
         'tankType': vTypeId,
         'isElite': isElite,
         'closeBtnTooltip': makeTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_HEADERCLOSEBTN_HEADER, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_HEADERCLOSEBTN_BODY)})

    def __setFooterInitData(self):
        self.as_setBottomPanelInitDataS({'backBtnLabel': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BOTTOMPANEL_BACKBTN_LABEL),
         'backBtnDescription': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BOTTOMPANEL_BACKBTN_DESCRIPTION),
         'pricePanelVO': {'goldIcon': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1,
                          'creditsIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1}})

    def __confirmCloseWindow(self, proceed):
        if proceed:
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __setBonusData(self, blData):
        visibilityPanelRenderList = _createBonusVOList(blData, [QUALIFIER_TYPE.CAMOUFLAGE])
        self.as_setBonusPanelDataS({'bonusTitle': text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATIONBONUSPANEL_VISIBILITYTITLE),
         'bonusRenderersList': visibilityPanelRenderList})

    def __setCarouselInitData(self):
        self.as_setCarouselInitS({'icoFilter': RES_ICONS.MAPS_ICONS_BUTTONS_FILTER,
         'durationType': _getDurationTypeVO(),
         'durationSelectIndex': 0,
         'onlyPurchased': True,
         'icoPurchased': RES_ICONS.MAPS_ICONS_FILTERS_PRESENCE,
         'message': '{2}{0}\n{1}'.format(text_styles.neutral(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_HEADER), text_styles.main(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_DESCRIPTION), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, vSpace=-3)),
         'fitterTooltip': makeTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_CAROUSEL_FILTER_HEADER, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_CAROUSEL_FILTER_BODY),
         'chbPurchasedTooltip': makeTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_CAROUSEL_CHBPURCHASED_HEADER, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_CAROUSEL_CHBPURCHASED_BODY)})

    def __setCarouselData(self, blData):
        itemVOs = []
        selectedIndex = -1
        for item in blData['items']:
            element = item['element']
            isInQuest = checkInQuest(element, self.__controller.filter.purchaseType)
            if item['installedInCurrentSlot']:
                label = text_styles.main(VEHICLE_CUSTOMIZATION.CAROUSEL_ITEMLABEL_APPLIED)
            elif element.isInDossier:
                label = text_styles.main(VEHICLE_CUSTOMIZATION.CAROUSEL_ITEMLABEL_PURCHASED)
            elif element.getIgrType() != IGR_TYPE.NONE:
                if element.getIgrType() == self.igrCtrl.getRoomType():
                    label = text_styles.main(VEHICLE_CUSTOMIZATION.CAROUSEL_ITEMLABEL_PURCHASED)
                else:
                    label = icons.premiumIgrSmall()
            elif isInQuest:
                label = icons.quest()
            else:
                if item['duration'] == DURATION.PERMANENT:
                    priceFormatter = text_styles.gold
                    priceIcon = icons.gold()
                else:
                    priceFormatter = text_styles.credits
                    priceIcon = icons.credits()
                label = priceFormatter('{0}{1}'.format(element.getPrice(item['duration']), priceIcon))
            data = {'id': element.getID(),
             'icon': element.getTexturePath(),
             'label': label,
             'selected': item['appliedToCurrentSlot'] or item['installedInCurrentSlot'] and not blData['hasAppliedItem'],
             'goToTaskBtnVisible': isInQuest,
             'goToTaskBtnText': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMCAROUSEL_RENDERER_GOTOTASK),
             'newElementIndicatorVisible': item['isNewElement']}
            if element.qualifier.getValue() > 0:
                data['bonusType'] = element.qualifier.getIcon16x16()
                data['bonusPower'] = text_styles.stats('+{0}%{1}'.format(element.qualifier.getValue(), '*' if element.qualifier.getDescription() is not None else ''))
            if data['selected']:
                selectedIndex = blData['items'].index(item)
            if element.isOnSale(item['duration']) and not element.isInDossier and not item['installedInCurrentSlot'] and not isInQuest:
                data['salePrice'] = getSalePriceString(self.__controller.slots.currentType, element, item['duration'])
            itemVOs.append(data)

        carouselLength = len(itemVOs)
        self.as_setCarouselDataS({'rendererList': itemVOs,
         'rendererWidth': blData['rendererWidth'],
         'filterCounter': '{0}{1}'.format(text_styles.stats(carouselLength) if carouselLength > 0 else text_styles.error(carouselLength), text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_COUNTER, all=blData['unfilteredLength']))),
         'messageVisible': carouselLength == 0,
         'counterVisible': True,
         'goToIndex': blData['goToIndex'],
         'selectedIndex': selectedIndex})
        return

    def __onPurchaseProcessed(self):
        self.backToSelectorGroup()

    @process
    def __removeSlot(self, cType, slotIdx):
        isContinue = True
        installedSlotItem = self.__controller.slots.getInstalledSlotData(slotIdx, cType)
        if installedSlotItem['duration'] > 0:
            isContinue = yield DialogsInterface.showDialog(getDialogRemoveElement(installedSlotItem['element'].getName(), cType))
        if isContinue:
            self.__controller.slots.clearSlot(cType, slotIdx)

    @process
    def __installElement(self, idx):
        isContinue = True
        element = self.__controller.carousel.items[idx]['element']
        cType = self.__controller.slots.currentType
        installedSlotData = self.__controller.slots.getInstalledSlotData()
        numberOfDaysLeft = installedSlotData['daysLeft']
        if element.isInDossier:
            if numberOfDaysLeft > 0 and element.getIgrType() != IGR_TYPE.PREMIUM:
                currentSlotData = self.__controller.slots.getCurrentSlotData()
                isContinue = yield DialogsInterface.showDialog(getDialogReplaceElement(currentSlotData['element'].getName(), cType))
            if element.numberOfDays is not None and not element.isReplacedByIGRItem:
                isContinue = yield DialogsInterface.showDialog(_getInvoiceItemDialogMeta('temporary', cType, element, {'willBeDeleted': text_styles.error(_ms(DIALOGS.CUSTOMIZATION_INSTALL_INVOICE_ITEM_WILL_BE_DELETED))}))
            elif element.numberOfItems is not None:
                if element.numberOfItems > 1:
                    isContinue = yield DialogsInterface.showDialog(_getInvoiceItemDialogMeta('permanent', cType, element, {'numberLeft': element.numberOfItems - 1}))
                else:
                    isContinue = yield DialogsInterface.showDialog(_getInvoiceItemDialogMeta('permanent_last', cType, element, {}))
        if isContinue:
            self.__controller.carousel.pickElement(idx)
        return
