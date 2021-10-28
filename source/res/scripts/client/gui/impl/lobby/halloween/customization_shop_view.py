# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/customization_shop_view.py
import itertools
from collections import namedtuple
from functools import partial
import BigWorld
import adisp
from async import async, await
from constants import EVENT, INVOICE_LIMITS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.dialogs.dialogs import showCustomizationConfirmDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.halloween.base_customization_item_view_model import CustomizationTypeEnum
from gui.impl.gen.view_models.views.lobby.halloween.event_keys_counter_panel_view_model import VisualTypeEnum
from gui.impl.lobby.halloween.event_keys_counter_panel_view import EventKeysCounterPanelView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.event_dispatcher import showHangar, showStorage
from frameworks.wulf import ViewSettings, ViewFlags, WindowLayer
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.impl.lobby.halloween.event_helpers import moveCamera, notifyCursorOver3DScene
from gui.impl.lobby.halloween.hangar_event_view import HangarEventView
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl.lobby.halloween.hangar_selectable_view import HangarSelectableView
from gui.impl.gen.view_models.views.lobby.halloween.customization_shop_view_model import CustomizationShopViewModel, BtnTypeEnum
from gui.impl.gen.view_models.common.simple_price_model import PriceTypeEnum
from gui.impl.gen.view_models.views.lobby.halloween.customization_item_view_model import CustomizationItemViewModel
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.gui_items.customization.c11n_items import Customization
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shop import showBuyGoldForBundle
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_event_controller import IGameEventController
from items.components.c11n_constants import CustomizationDisplayType, ProjectionDecalFormTags
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared.money import Currency
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from HalloweenHangarTank import HalloweenHangarTank
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from ids_generators import SequenceIDGenerator
from gui.shared import event_dispatcher as shared_events
from items.components.c11n_constants import SeasonType
from gui.ClientUpdateManager import g_clientUpdateManager
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui import SystemMessages
from gui.customization.constants import CustomizationModes
FORMFACTOR_SIZE = {ProjectionDecalFormTags.SQUARE: 1,
 ProjectionDecalFormTags.RECT1X2: 2,
 ProjectionDecalFormTags.RECT1X3: 3,
 ProjectionDecalFormTags.RECT1X4: 4,
 ProjectionDecalFormTags.RECT1X6: 5}
ShopItemData = namedtuple('ShopItemData', ['index',
 'c11Item',
 'bundleID',
 'entityID'])
ShopBundlePriceInfo = namedtuple('ShopBundlePriceInfo', ['isEnough',
 'priceType',
 'amount',
 'playerAmount'])

class CustomizationShopView(HangarSelectableView, HangarEventView, EventSystemEntity):
    gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)
    hangarSpace = dependency.descriptor(IHangarSpace)
    c11 = dependency.descriptor(ICustomizationService)
    CAMMO_BONUS_FMT = '+{:.0%}'

    def __init__(self, layoutID, initialEntityID=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CustomizationShopViewModel()
        self.__initialEntityID = initialEntityID
        self.__idGen = SequenceIDGenerator()
        self.__shop = self.gameEventController.getShop()
        self.__keysCounterPanel = EventKeysCounterPanelView(VisualTypeEnum.CUSTOMIZATION)
        self.__shopItems = []
        self.__blur = CachedBlur(enabled=False, ownLayer=WindowLayer.MARKER)
        self.__isResetCameraObjectOnFini = True
        super(CustomizationShopView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CustomizationShopView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            eventId = event.getArgument('id')
            specialArgs = []
            if (tooltipId != TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM or eventId is None) and tooltipId != TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_NONHISTORIC_ITEM:
                return
            if tooltipId == TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM:
                shopItem = self.__shopItems[int(eventId)]
                intCD = shopItem.c11Item().intCD
                specialArgs = CustomizationTooltipContext(itemCD=intCD, showInventoryBlock=False)
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
            window.load()
            return window
        else:
            return super(CustomizationShopView, self).createToolTip(event)

    def _onLoading(self):
        super(CustomizationShopView, self)._onLoading()
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdate})
        self.viewModel.onClose += self.__onClose
        self.viewModel.onBack += self.__onBack
        self.viewModel.onMoveSpace += self.__onMoveSpace
        self.viewModel.onOverScene += self.__onOverScene
        self.viewModel.onSelectedChange += self.__onSelectedChange
        self.viewModel.onBtnClick += self.__onBtnClick
        self.__shop.onGoldChanged += self.__onMoneyUpdated
        self.gameEventController.onRewardBoxKeyUpdated += self.__onMoneyUpdated
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraSwitched)
        self.hangarSpace.setVehicleSelectable(True)
        self.setChildView(self.__keysCounterPanel.layoutID, self.__keysCounterPanel)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__buildShopData()
        self.__fillModel()
        if self.__initialEntityID is not None:
            initialShopItem = next((shopItem for shopItem in self.__shopItems if shopItem.entityID == self.__initialEntityID))
            self.__fillSelectedItem(initialShopItem)
        elif self.__shopItems:
            initialShopItem = self.__shopItems[0]
            if initialShopItem.entityID is not None:
                ClientSelectableCameraObject.switchCamera(BigWorld.entities.get(initialShopItem.entityID))
        return

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraSwitched)
        if self.__isResetCameraObjectOnFini:
            ClientSelectableCameraObject.switchCamera()
        self.__shop.onGoldChanged -= self.__onMoneyUpdated
        self.gameEventController.onRewardBoxKeyUpdated -= self.__onMoneyUpdated
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onBack -= self.__onBack
        self.viewModel.onMoveSpace -= self.__onMoveSpace
        self.viewModel.onOverScene -= self.__onOverScene
        self.viewModel.onSelectedChange -= self.__onSelectedChange
        self.viewModel.onBtnClick -= self.__onBtnClick
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__blur:
            self.__blur.fini()
            self.__blur = None
        super(CustomizationShopView, self)._finalize()
        return

    def __disableBlur(self):
        if self.__blur is not None:
            self.__blur.disable()
        self._activateSelectableLogic()
        return

    def __enableBlur(self):
        if self.__blur is not None:
            self.__blur.enable()
        self._deactivateSelectableLogic()
        return

    def __buildShopData(self):
        self.__shopItems = []
        shopBundles = self.__shop.getBundlesByShopType(EVENT.SHOP.TYPE.C11N)
        hangarTanks = [ obj for obj in ClientSelectableCameraObject.allCameraObjects if isinstance(obj, HalloweenHangarTank) ]
        matchedCDs = []
        for bundle in shopBundles:
            bonus = bundle.bonuses[0]
            itemData = bonus.getCustomizations()[0]
            c11Item = bonus.getC11nItem(itemData)
            entityID = None
            if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE:
                vehicles = self.__getC11ItemVehicles(c11Item)
                for hangarTank in hangarTanks:
                    intCD = hangarTank.typeDescriptor.type.compactDescr
                    if intCD in vehicles and intCD not in matchedCDs:
                        matchedCDs.append(intCD)
                        entityID = hangarTank.id
                        break

            itemTypeID = c11Item.itemTypeID
            itemID = itemData.get('id')
            self.__shopItems.append(ShopItemData(index=len(self.__shopItems), c11Item=partial(self.c11.getItemByID, itemTypeID, itemID), bundleID=bundle.id, entityID=entityID))

        return

    def __refillModels(self):
        selectedIndex = int(self.viewModel.selectedItem.getId())
        self.__fillModel()
        self.__fillSelectedItem(self.__shopItems[selectedIndex])

    def __fillModel(self):
        with self.viewModel.transaction() as vm:
            c11ItemsModel = vm.getCustomizationItems()
            c11ItemsModel.clear()
            for shopItem in self.__shopItems:
                bundleModel = CustomizationItemViewModel()
                self.__fillItemModel(bundleModel, shopItem)
                self.__fillPrice(bundleModel.price, shopItem)
                c11ItemsModel.addViewModel(bundleModel)

            c11ItemsModel.invalidate()

    def __fillItemModel(self, model, shopItem):
        bundle = self.__shop.getBundle(shopItem.bundleID)
        c11Item = shopItem.c11Item()
        modelType = CustomizationTypeEnum.DECAL
        isBought = False
        isHistorical = c11Item.customizationDisplayType() == CustomizationDisplayType.HISTORICAL
        inventoryCount = 0
        decalSize = 0
        name = ''
        if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            vehicle = self.__getVehicle(shopItem)
            isBought = self.__shop.getBundlePurchasesCount(bundle.id) > 0 or c11Item.fullCount() > 0
            modelType = CustomizationTypeEnum.STYLE
            name = backport.text(R.strings.event.tradeStyles.carouselSkinName(), name=vehicle.shortUserName if vehicle else '')
        else:
            name = backport.text(R.strings.event.tradeStyles.carouselDecalName(), name=c11Item.userName)
        if hasattr(c11Item, 'formfactor'):
            decalSize = FORMFACTOR_SIZE[c11Item.formfactor]
        model.setType(modelType)
        model.setId(shopItem.index)
        model.setIcon(c11Item.iconUrl)
        model.setName(name)
        model.setIsHistorical(isHistorical)
        model.setWarehouseCount(inventoryCount)
        model.setDecalSize(decalSize)
        model.setIsBought(isBought)

    def __fillPrice(self, priceModel, shopItem):
        bundle = self.__shop.getBundle(shopItem.bundleID)
        price, oldPrice = bundle.price, bundle.oldPrice
        priceInfo = self.__getPriceInfo(price)
        priceModel.setType(priceInfo.priceType)
        priceModel.setValue(priceInfo.amount)
        priceModel.setIsEnough(priceInfo.isEnough)
        priceModel.setHasDiscount(oldPrice is not None)
        if oldPrice is not None:
            priceModel.setDiscountValue(self.__calcDiscount(price.amount, oldPrice.amount))
        return

    def __fillSelectedItem(self, shopItem):
        with self.viewModel.transaction() as vm:
            c11Item = shopItem.c11Item()
            vehicleName = ''
            cammoBonus = 0
            isBought = False
            hasVehicle = False
            isInBattle = False
            itemType = CustomizationTypeEnum.DECAL
            if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE:
                vehicle = self.__getVehicle(shopItem)
                hasVehicle = vehicle.isInInventory
                vehicleName = vehicle.shortUserName if vehicle else ''
                cammoBonus = self.__getCammoBonus(shopItem)
                itemType = CustomizationTypeEnum.STYLE
                bundle = self.__shop.getBundle(shopItem.bundleID)
                isBought = self.__shop.getBundlePurchasesCount(bundle.id) > 0 or c11Item.fullCount() > 0
                isInBattle = vehicle.isInBattle
                vm.selectedItem.setLongName(backport.text(R.strings.event.tradeStyles.skinDescr(), name=vehicleName))
                vm.selectedItem.setIcon(c11Item.iconUrl)
            else:
                vm.selectedItem.setLongName(backport.text(R.strings.event.tradeStyles.carouselShortDecalName()))
                vm.selectedItem.setIcon('img://{0}'.format(c11Item.texture))
            if shopItem.entityID is not None:
                self.__disableBlur()
            else:
                self.__enableBlur()
            vm.selectedItem.setType(itemType)
            vm.selectedItem.setId(shopItem.index)
            vm.selectedItem.setName(c11Item.userName)
            vm.selectedItem.setDescription(c11Item.longDescriptionSpecial)
            vm.selectedItem.setVehicleType(c11Item.userType)
            vm.selectedItem.setBonus(self.CAMMO_BONUS_FMT.format(cammoBonus))
            vm.selectedItem.setCard(backport.text(R.strings.event.tradeStyles.infoMapAny()))
            vm.selectedItem.setMode(backport.text(R.strings.event.tradeStyles.infoModeAny()))
            vm.selectedItem.setVehicleName(vehicleName)
            vm.selectedItem.setIsBought(isBought)
            vm.selectedItem.setHasVehicleInHangar(hasVehicle)
            vm.selectedItem.setIsInBattle(isInBattle)
            stepperMaxValue = self.__getStepperMaxValue(shopItem)
            vm.stepper.setMaximumValue(stepperMaxValue)
            vm.stepper.setSelectedValue(min(1, stepperMaxValue))
            self.__fillPrice(vm.price, shopItem)
        return

    def __onClose(self):
        self.destroyWindow()
        showHangar()

    def __onBack(self):
        self.destroyWindow()
        showHangar()

    @async
    def __onBtnClick(self, args):
        count = args.get('count', None)
        btnType = args.get('btnType', BtnTypeEnum.BUY_STYLE.value)
        if count is None or btnType is None:
            return
        else:
            selectedIndex = int(self.viewModel.selectedItem.getId())
            if btnType == BtnTypeEnum.TO_WAREHOUSE.value:
                self.__gotoStorage()
                return
            if btnType == BtnTypeEnum.TO_CUSTOMIZATION.value:
                self.__gotoC11View(selectedIndex)
                return
            count = 1 if btnType == BtnTypeEnum.BUY_STYLE.value else int(count)
            shopItem = self.__shopItems[selectedIndex]
            bundle = self.__shop.getBundle(shopItem.bundleID)
            self._deactivateSelectableLogic()
            if bundle.price.currencyType == EVENT.SHOP.REAL_CURRENCY:
                playerGold = self.itemsCache.items.stats.money.get(Currency.GOLD, 0)
                totalPrice = bundle.price.amount * count
                if playerGold < totalPrice:
                    showBuyGoldForBundle(bundle.price.amount, {})
                    return
            isOk, _ = yield await(showCustomizationConfirmDialog(shopItem, count))
            if isOk:
                self.__processBuyItem(bundle.id, count)
            self._activateSelectableLogic()
            return

    @adisp.process
    def __processBuyItem(self, idd, count):
        _ = yield self.__shop.purchaseShopBundle(idd, count=count)

    def __gotoStorage(self):
        g_currentPreviewVehicle.selectNoVehicle()
        showStorage(STORAGE_CONSTANTS.CUSTOMIZATION)

    def __gotoC11View(self, selectedIndex):
        shopItem = self.__shopItems[selectedIndex]
        vehicle = self.__getVehicle(shopItem)
        if vehicle is None:
            return
        elif not vehicle.isInInventory:
            return
        elif vehicle.isInBattle:
            SystemMessages.pushMessage(text=backport.text(R.strings.tooltips.hangar.tuning.disabled.body()), type=SystemMessages.SM_TYPE.ErrorHeader, messageData={'header': backport.text(R.strings.tooltips.hangar.tuning.disabled.header())})
            return
        else:
            styleItem = shopItem.c11Item()

            def styleCallback():
                ctx = self.c11.getCtx()
                ctx.changeMode(CustomizationModes.STYLED)
                ctx.selectItem(styleItem.intCD)

            g_currentPreviewVehicle.selectNoVehicle()
            outfit = vehicle.getOutfit(vehicle.getAnyOutfitSeason())
            callback = styleCallback if not outfit.style or outfit.style.compactDescr != styleItem.intCD else None
            self.c11.showCustomization(vehicle.invID, callback=callback)
            return

    def __onMoneyUpdated(self, *args, **kwargs):
        self.__refillModels()

    def __onInventoryUpdate(self, *args, **kwargs):
        self.__refillModels()

    def __onSelectedChange(self, args):
        index = args.get('id', None)
        if index is None:
            return
        else:
            shopItem = self.__shopItems[int(index)]
            if shopItem.c11Item().itemTypeID == GUI_ITEM_TYPE.STYLE and shopItem.entityID is not None:
                entity = BigWorld.entities.get(shopItem.entityID, None)
                if entity is not None and entity.state != CameraMovementStates.ON_OBJECT:
                    ClientSelectableCameraObject.switchCamera(entity)
                    return
            self.__fillSelectedItem(shopItem)
            return

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            moveCamera(dx, dy, dz)
            return

    def __onOverScene(self, args):
        if args is None:
            return
        else:
            notifyCursorOver3DScene(args.get('isOver3dScene', False))
            return

    def __onCameraSwitched(self, event):
        if event.ctx['state'] != CameraMovementStates.MOVING_TO_OBJECT:
            return
        cameraObject = next((obj for obj in ClientSelectableCameraObject.allCameraObjects if obj.id == event.ctx['entityId']))
        if not cameraObject:
            return
        if isinstance(cameraObject, HalloweenHangarTank):
            if cameraObject.isKingReward:
                self.__isResetCameraObjectOnFini = False
                descriptor = cameraObject.typeDescriptor
                shared_events.showHalloweenKingRewardPreview(descriptor.type.compactDescr)
            else:
                shopItem = next((item for item in self.__shopItems if item.entityID == event.ctx['entityId']))
                self.__fillSelectedItem(shopItem)
            return
        self.__onClose()

    def __getPriceInfo(self, bundlePrice):
        priceType = PriceTypeEnum.GOLD if bundlePrice.currencyType == EVENT.SHOP.REAL_CURRENCY else PriceTypeEnum.TOKENS
        playerAmount = self.__getGold() if bundlePrice.currencyType == EVENT.SHOP.REAL_CURRENCY else self.__getKeys()
        return ShopBundlePriceInfo(playerAmount >= bundlePrice.amount, priceType, bundlePrice.amount, playerAmount)

    def __getC11ItemVehicles(self, c11Item):
        return [] if not c11Item.descriptor.filter else list(itertools.chain.from_iterable((node.vehicles for node in c11Item.descriptor.filter.include if node.vehicles)))

    def __getGold(self):
        return self.itemsCache.items.stats.money.get(Currency.GOLD, 0)

    def __getKeys(self):
        return self.__shop.getKeys()

    def __getVehicle(self, shopItem):
        if shopItem.entityID is not None:
            vehicleCD = BigWorld.entities[shopItem.entityID].typeDescriptor.type.compactDescr
        else:
            vehicleCD = next(iter(self.__getC11ItemVehicles(shopItem.c11Item())))
        return None if vehicleCD is None else self.itemsCache.items.getItemByCD(vehicleCD)

    def __getCammoBonus(self, shopItem):
        if shopItem.entityID is None:
            return 0
        else:
            bonusValue = 0
            styleItem = shopItem.c11Item()
            vehicleDescr = BigWorld.entities[shopItem.entityID].typeDescriptor
            for container in (styleItem.getOutfit(season).hull for season in SeasonType.SEASONS if styleItem.getOutfit(season)):
                camoIntCD = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItemCD()
                camo = self.c11.getItemByCD(camoIntCD) if camoIntCD else None
                if camo and camo.bonus:
                    _, bonusValue = vehicleDescr.computeBaseInvisibility(crewFactor=0, camouflageId=camo.id)
                    break

            return bonusValue

    def __getStepperMaxValue(self, shopItem):
        bundle = self.__shop.getBundle(shopItem.bundleID)
        priceInfo = self.__getPriceInfo(bundle.price)
        return min(INVOICE_LIMITS.PERMANENT_CUST_MAX, int(priceInfo.playerAmount / priceInfo.amount))

    @staticmethod
    def __calcDiscount(currentPrice, oldPrice):
        return int(float(oldPrice - currentPrice) / float(oldPrice) * 100.0)
