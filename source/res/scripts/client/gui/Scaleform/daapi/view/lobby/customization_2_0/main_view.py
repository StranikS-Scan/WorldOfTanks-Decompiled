# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization_2_0/main_view.py
from gui import DialogsInterface
from constants import IGR_TYPE, EVENT_TYPE
from adisp import process
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.lobby.customization_2_0.shared import getDialogRemoveElement, getDialogReplaceElement
from gui.Scaleform.daapi.view.meta.CustomizationMainViewMeta import CustomizationMainViewMeta
from gui.Scaleform.locale.CUSTOMIZATION import CUSTOMIZATION
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization_2_0.cart import Cart
from gui.game_control import getIGRCtrl
from gui.server_events import events_dispatcher
from gui.shared import events
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms
from gui.shared.formatters import text_styles, icons
from gui.customization_2_0.filter import QUALIFIER_TYPE_INDEX, FILTER_TYPE
from gui.customization_2_0.shared import formatPriceCredits, formatPriceGold, getSalePriceString
from gui.customization_2_0.elements.qualifier import QUALIFIER_TYPE
from gui.customization_2_0 import g_customizationController
_BONUS_TOOLTIP_BODY = {QUALIFIER_TYPE.ALL: TOOLTIPS.CUSTOMIZATION_BONUSPANEL_BONUS_ENTIRECREW_BODY,
 QUALIFIER_TYPE.RADIOMAN: TOOLTIPS.CUSTOMIZATION_BONUSPANEL_BONUS_RADIOMAN_BODY,
 QUALIFIER_TYPE.COMMANDER: TOOLTIPS.CUSTOMIZATION_BONUSPANEL_BONUS_COMMANDER_BODY,
 QUALIFIER_TYPE.DRIVER: TOOLTIPS.CUSTOMIZATION_BONUSPANEL_BONUS_DRIVER_BODY,
 QUALIFIER_TYPE.GUNNER: TOOLTIPS.CUSTOMIZATION_BONUSPANEL_BONUS_AIMER_BODY,
 QUALIFIER_TYPE.LOADER: TOOLTIPS.CUSTOMIZATION_BONUSPANEL_BONUS_LOADER_BODY,
 QUALIFIER_TYPE.CAMOUFLAGE: TOOLTIPS.CUSTOMIZATION_BONUSPANEL_BONUS_MASKING_BODY}
_BONUS_TOOLTIP_NAME = {QUALIFIER_TYPE.ALL: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_ENTIRECREW,
 QUALIFIER_TYPE.RADIOMAN: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_RADIOMAN,
 QUALIFIER_TYPE.COMMANDER: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_COMMANDER,
 QUALIFIER_TYPE.DRIVER: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_DRIVER,
 QUALIFIER_TYPE.GUNNER: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_AIMER,
 QUALIFIER_TYPE.LOADER: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_LOADER,
 QUALIFIER_TYPE.CAMOUFLAGE: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_MASKING}
_DURATION_MAPPING = {0: 0,
 1: 30,
 2: 7}

class MainView(CustomizationMainViewMeta):

    def __init__(self, ctx=None):
        super(MainView, self).__init__()
        self.__carouselHidden = True
        self.__animationTestIndex = -1
        self.__isPurchaseProcess = False
        g_customizationController.init()

    def showGroup(self, cType, slotIdx):
        g_customizationController.carousel.slots.select(cType, slotIdx)
        if self.__carouselHidden:
            self.__carouselHidden = False
            self.__setBottomPanelData()
            self.as_showSelectorItemS(cType)

    def __setBottomPanelData(self):
        if self.__carouselHidden:
            label = g_customizationController.carousel.slots.getSummaryString()
        else:
            label = g_customizationController.carousel.slots.getCurrentTypeLabel()
        totalGold = g_customizationController.carousel.slots.cart.totalPriceGold
        totalCredits = g_customizationController.carousel.slots.cart.totalPriceCredits
        notEnoughGoldTooltip = notEnoughCreditsTooltip = ''
        enoughGold = g_itemsCache.items.stats.gold >= totalGold
        enoughCredits = g_itemsCache.items.stats.credits >= totalCredits
        if not enoughGold:
            diff = text_styles.gold(totalGold - g_itemsCache.items.stats.gold)
            notEnoughGoldTooltip = makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_NOTENOUGHRESOURCES_HEADER), _ms(TOOLTIPS.CUSTOMIZATION_NOTENOUGHRESOURCES_BODY, count='{0}{1}'.format(diff, icons.gold())))
        if not enoughCredits:
            diff = text_styles.credits(totalCredits - g_itemsCache.items.stats.credits)
            notEnoughCreditsTooltip = makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_NOTENOUGHRESOURCES_HEADER), _ms(TOOLTIPS.CUSTOMIZATION_NOTENOUGHRESOURCES_BODY, count='{0}{1}'.format(diff, icons.credits())))
        self.as_setBottomPanelHeaderS({'newHeaderText': label,
         'buyBtnLabel': _ms(MENU.CUSTOMIZATION_BUTTONS_APPLY, count=len(g_customizationController.carousel.slots.cart.items)),
         'pricePanel': {'totalPriceCredits': formatPriceCredits(totalCredits),
                        'totalPriceGold': formatPriceGold(totalGold),
                        'enoughGold': enoughGold,
                        'enoughCredits': enoughCredits,
                        'notEnoughGoldTooltip': notEnoughGoldTooltip,
                        'notEnoughCreditsTooltip': notEnoughCreditsTooltip}})

    @process
    def removeSlot(self, cType, slotIdx):
        isContinue = True
        installedItem = g_customizationController.carousel.slots.getInstalledItem(slotIdx, cType)
        if installedItem.duration > 0:
            slotItem = g_customizationController.carousel.slots.getItemById(cType, installedItem.getID())
            isContinue = yield DialogsInterface.showDialog(getDialogRemoveElement(slotItem.getName(), cType))
        if isContinue:
            g_customizationController.carousel.slots.clearSlot(cType, slotIdx)

    def revertSlot(self, cType, slotIdx):
        g_customizationController.carousel.slots.dropAppliedItem(cType, slotIdx)

    def backToSelectorGroup(self):
        self.__carouselHidden = True
        self.__setBottomPanelData()
        self.as_showSelectorGroupS()
        g_customizationController.updateTank3DModel()

    @process
    def installCustomizationElement(self, idx):
        isContinue = True
        carouselItem = g_customizationController.carousel.items[idx]['object']
        cType = g_customizationController.carousel.currentType
        if carouselItem.isInDossier:
            if g_customizationController.carousel.slots.getInstalledItem().getNumberOfDaysLeft() > 0 and carouselItem.getIgrType() != IGR_TYPE.PREMIUM:
                slotItem = g_customizationController.carousel.slots.getSlotItem()
                isContinue = yield DialogsInterface.showDialog(getDialogReplaceElement(slotItem.getName(), cType))
            if carouselItem.numberOfDays is not None and not carouselItem.isReplacedByIGRItem:
                isContinue = yield DialogsInterface.showDialog(self.__getInvoiceItemDialogMeta('temporary', cType, carouselItem, {'willBeDeleted': text_styles.error(_ms('#dialogs:customization/install_invoice_item/will_be_deleted'))}))
            elif carouselItem.numberOfItems is not None:
                if carouselItem.numberOfItems > 1:
                    isContinue = yield DialogsInterface.showDialog(self.__getInvoiceItemDialogMeta('permanent', cType, carouselItem, {'numberLeft': carouselItem.numberOfItems - 1}))
                else:
                    isContinue = yield DialogsInterface.showDialog(self.__getInvoiceItemDialogMeta('permanent_last', cType, carouselItem, {}))
        if isContinue:
            g_customizationController.carousel.applyItem(idx)
        return

    def setDurationType(self, durationIdx):
        g_customizationController.carousel.changeDuration(_DURATION_MAPPING[durationIdx])

    def closeWindow(self):
        if g_customizationController.carousel.slots.cart.items:
            DialogsInterface.showDialog(I18nConfirmDialogMeta('customization/close'), self.__confirmCloseWindow)
        else:
            self.__confirmCloseWindow(True)

    def showBuyWindow(self):
        self.app.loadView(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW)

    def showPurchased(self, value):
        g_customizationController.carousel.filter.set(FILTER_TYPE.SHOW_IN_DOSSIER, value)
        g_customizationController.carousel.filter.apply()

    def _dispose(self):
        g_customizationController.updateTank3DModel(isReset=True)
        g_customizationController.carousel.updated -= self.__setCarouselData
        g_customizationController.carousel.slots.updated -= self.as_updateSlotS
        g_customizationController.carousel.slots.cart.totalPriceUpdated -= self.__setBottomPanelData
        g_customizationController.carousel.slots.cart.availableMoneyUpdated -= self.__setBottomPanelData
        g_customizationController.carousel.slots.cart.emptied -= self.as_hideBuyingPanelS
        g_customizationController.carousel.slots.cart.filled -= self.as_showBuyingPanelS
        g_customizationController.carousel.slots.bonusPanel.bonusesUpdated -= self.__setBonusData
        g_currentVehicle.onChanged -= self.__setHeaderInitData
        g_customizationController.carousel.slots.cart.purchaseProcessed -= self.__onPurchaseProcessed
        Cart.purchaseProcessStarted -= self.__onPurchaseProcessStarted
        g_customizationController.fini()
        super(MainView, self)._dispose()

    def _populate(self):
        super(MainView, self)._populate()
        g_currentVehicle.onChanged += self.__setHeaderInitData
        g_customizationController.carousel.updated += self.__setCarouselData
        g_customizationController.carousel.slots.updated += self.as_updateSlotS
        g_customizationController.carousel.slots.cart.totalPriceUpdated += self.__setBottomPanelData
        g_customizationController.carousel.slots.cart.availableMoneyUpdated += self.__setBottomPanelData
        g_customizationController.carousel.slots.cart.emptied += self.as_hideBuyingPanelS
        g_customizationController.carousel.slots.cart.filled += self.as_showBuyingPanelS
        g_customizationController.carousel.slots.bonusPanel.bonusesUpdated += self.__setBonusData
        g_customizationController.carousel.slots.cart.purchaseProcessed += self.__onPurchaseProcessed
        Cart.purchaseProcessStarted += self.__onPurchaseProcessStarted
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.HIDE_HANGAR, True))
        self.__setHeaderInitData()
        self.__setBonusData(g_customizationController.carousel.slots.bonusPanel.bonusData)
        self.as_setSlotsPanelDataS(g_customizationController.carousel.slots.getData())
        self.__setCarouselInitData()
        self.__setBottomPanelData()
        self.as_setBottomPanelInitDataS({'backBtnLabel': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BOTTOMPANEL_BACKBTN_LABEL),
         'backBtnDescription': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BOTTOMPANEL_BACKBTN_DESCRIPTION),
         'pricePanelVO': {'goldIcon': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1,
                          'creditsIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1}})

    def __setHeaderInitData(self):
        isElite = g_currentVehicle.item.isElite
        vTypeId = g_currentVehicle.item.type
        vTypeId = '{0}_elite'.format(vTypeId) if isElite else vTypeId
        self.as_setHeaderDataS({'titleText': text_styles.promoTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATIONHEADER_TITLE),
         'tankName': text_styles.promoSubTitle(g_currentVehicle.item.userName),
         'tankType': vTypeId,
         'isElite': isElite,
         'closeBtnTooltip': makeTooltip(TOOLTIPS.CUSTOMIZATION_HEADERCLOSEBTN_HEADER, TOOLTIPS.CUSTOMIZATION_HEADERCLOSEBTN_BODY)})

    def __confirmCloseWindow(self, proceed):
        if proceed:
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __createBonusVOList(self, blData, bonusNameList):
        result = []
        for qTypeName in bonusNameList:
            bonusVO = {'bonusName': blData[qTypeName]['bonusName'],
             'bonusIcon': blData[qTypeName]['bonusIcon'],
             'animationPanel': blData[qTypeName]['animationPanel'],
             'bonusType': qTypeName}
            result.append(bonusVO)

        return result

    def __setBonusData(self, blData):
        crewPanelRenderList = self.__createBonusVOList(blData, QUALIFIER_TYPE_INDEX)
        visibilityPanelRenderList = self.__createBonusVOList(blData, [QUALIFIER_TYPE.CAMOUFLAGE])
        self.as_setBonusPanelDataS({'crewPanel': {'bonusTitle': text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATIONBONUSPANEL_CREWTITLE),
                       'bonusRenderersList': crewPanelRenderList},
         'visibilityPanel': {'bonusTitle': text_styles.middleTitle(VEHICLE_CUSTOMIZATION.CUSTOMIZATIONBONUSPANEL_VISIBILITYTITLE),
                             'bonusRenderersList': visibilityPanelRenderList}})

    def __setCarouselInitData(self):
        self.as_setCarouselInitS({'icoFilter': RES_ICONS.MAPS_ICONS_BUTTONS_FILTER,
         'durationType': [self.__getDurationTypeVO('{0}{1}'.format(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_ALWAYS), icons.gold()), makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_HEADER, time=_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_ALWAYS)), _ms(TOOLTIPS.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_BODY, time=_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_LOWERCASE_ALWAYS))), makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_HEADER, time=_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_ALWAYS)), VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_DISABLED)), self.__getDurationTypeVO('{0}{1}'.format(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_MONTH), icons.credits()), makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_HEADER, time=_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_MONTH)), _ms(TOOLTIPS.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_BODY, time=_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_LOWERCASE_MONTH))), makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_HEADER, time=_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_MONTH)), VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_DISABLED)), self.__getDurationTypeVO('{0}{1}'.format(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_WEEK), icons.credits()), makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_HEADER, time=_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_WEEK)), _ms(TOOLTIPS.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_BODY, time=_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_LOWERCASE_WEEK))), makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_CAROUSEL_DURATIONTYPE_HEADER, time=_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_WEEK)), VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_DURATION_DISABLED))],
         'durationSelectIndex': 0,
         'onlyPurchased': True,
         'icoPurchased': RES_ICONS.MAPS_ICONS_FILTERS_PRESENCE,
         'message': '{2}{0}\n{1}'.format(text_styles.neutral(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_HEADER), text_styles.main(VEHICLE_CUSTOMIZATION.CAROUSEL_MESSAGE_DESCRIPTION), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, 16, 16, -3, 0)),
         'fitterTooltip': makeTooltip(TOOLTIPS.CUSTOMIZATION_CAROUSEL_FILTER_HEADER, TOOLTIPS.CUSTOMIZATION_CAROUSEL_FILTER_BODY),
         'chbPurchasedTooltip': makeTooltip(TOOLTIPS.CUSTOMIZATION_CAROUSEL_CHBPURCHASED_HEADER, TOOLTIPS.CUSTOMIZATION_CAROUSEL_CHBPURCHASED_BODY)})

    def __getDurationTypeVO(self, label, tooltip, tooltipDisabled):
        return {'label': label,
         'tooltip': tooltip,
         'tooltipDisabled': tooltipDisabled}

    def __setCarouselData(self, blData):
        itemVOs = []
        for item in blData['items']:
            if item['installedInSlot']:
                label = text_styles.main(CUSTOMIZATION.CAROUSEL_ITEMLABEL_APPLIED)
            elif item['isInDossier']:
                label = text_styles.main(CUSTOMIZATION.CAROUSEL_ITEMLABEL_PURCHASED)
            elif item['object'].getIgrType() != IGR_TYPE.NONE:
                if item['object'].getIgrType() == getIGRCtrl().getRoomType():
                    label = text_styles.main(CUSTOMIZATION.CAROUSEL_ITEMLABEL_PURCHASED)
                else:
                    label = icons.premiumIgrSmall()
            elif item['isInQuests']:
                label = icons.quest()
            else:
                if item['priceIsGold']:
                    priceFormatter = text_styles.gold
                    priceIcon = icons.gold()
                else:
                    priceFormatter = text_styles.credits
                    priceIcon = icons.credits()
                label = priceFormatter('{0}{1}'.format(item['price'], priceIcon))
            data = {'id': item['id'],
             'icon': item['object'].getTexturePath(),
             'bonusType': item['object'].qualifier.getIcon16x16(),
             'bonusPower': text_styles.stats('+{0}%{1}'.format(item['object'].qualifier.getValue(), '*' if item['object'].qualifier.getDescription() is not None else '')),
             'label': label,
             'selected': item['appliedToCurrentSlot'],
             'goToTaskBtnVisible': item['isInQuests'],
             'goToTaskBtnText': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMCAROUSEL_RENDERER_GOTOTASK),
             'newElementIndicatorVisible': False}
            cType = g_customizationController.carousel.currentType
            if item['object'].isSale(item['duration']) and not item['isInDossier'] and not item['installedInSlot'] and not item['isInQuests']:
                data['salePrice'] = getSalePriceString(cType, item['object'], item['duration'])
            itemVOs.append(data)

        carouselLength = len(itemVOs)
        self.as_setCarouselDataS({'rendererList': itemVOs,
         'rendererWidth': blData['rendererWidth'],
         'filterCounter': '{0}{1}'.format(text_styles.stats(carouselLength) if carouselLength > 0 else text_styles.error(carouselLength), text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_COUNTER, all=blData['unfilteredLength']))),
         'messageVisible': carouselLength == 0,
         'counterVisible': True,
         'goToIndex': blData['goToIndex'],
         'selectedIndex': blData['selectedIndex']})
        return

    def __getLabelOfSelectBtn(self, item):
        return VEHICLE_CUSTOMIZATION.CUSTOMIZATIONITEMCAROUSEL_RENDERER_APPLY if item['isInDossier'] else VEHICLE_CUSTOMIZATION.CUSTOMIZATIONITEMCAROUSEL_RENDERER_SELECT

    def __getInvoiceItemDialogMeta(self, dialogType, cType, carouselItem, l10nExtraParams):
        l10nParams = {'cTypeName': _ms('#customization:typeSwitchScreen/typeName/{0}'.format(cType)),
         'itemName': carouselItem.getName()}
        l10nParams.update(l10nExtraParams)
        return I18nConfirmDialogMeta('customization/install_invoice_item/' + dialogType, messageCtx=l10nParams, focusedID=DIALOG_BUTTON_ID.CLOSE)

    def __onPurchaseProcessStarted(self):
        self.__isPurchaseProcess = True

    def __onPurchaseProcessed(self):
        if self.__isPurchaseProcess:
            self.__isPurchaseProcess = False
            self.backToSelectorGroup()

    def goToTask(self, idx):
        item = g_customizationController.carousel.items[idx]['object']
        quests = g_customizationController.dataAggregator.associatedQuests
        cType = g_customizationController.carousel.currentType
        questData = quests[cType][item.getID()]
        events_dispatcher.showEventsWindow(eventID=questData.id, eventType=EVENT_TYPE.BATTLE_QUEST)
