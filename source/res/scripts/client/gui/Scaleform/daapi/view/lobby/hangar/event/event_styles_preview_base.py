# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_styles_preview_base.py
import logging
import GUI
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.lobby.halloween_event.event_tanks_highlight_controller import EventTanksHighlightController
from gui.Scaleform.daapi.view.meta.EventStylesTradeMeta import EventStylesTradeMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.events_dispatcher import showEventShop
from gui.shared import event_bus_handlers, events, event_dispatcher, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import vehicles
from items.vehicles import VehicleDescriptor, makeVehicleTypeCompDescrByName
from skeletons.gui.customization import ICustomizationService
from gui.customization.constants import CustomizationModes
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from items.components.c11n_constants import SeasonType
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui import SystemMessages
_logger = logging.getLogger(__name__)

class EventStylesTradeBase(LobbySelectableView, EventStylesTradeMeta):
    __background_alpha__ = 0.0
    __metaclass__ = event_bus_handlers.EventBusListener
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    hangarSpace = dependency.descriptor(IHangarSpace)
    gameEventController = dependency.descriptor(IGameEventController)
    c11nService = dependency.descriptor(ICustomizationService)
    _DEACTIVATABLE_BUY_BUTTON = False

    def __init__(self, ctx=None):
        super(EventStylesTradeBase, self).__init__()
        self.__blur = GUI.WGUIBackgroundBlur()
        self.__highlightController = EventTanksHighlightController()
        self._ctx = ctx
        self._carouselDP = None
        self._selectedTank = ctx['itemIndex'] if 'itemIndex' in ctx else 0
        self._highlightHangarVehicle = False
        return

    def closeView(self):
        showEventShop()

    def onBackClick(self):
        self.closeView()

    def onUseClick(self):
        vehicleTypes = self._getVehicleTypes()
        index = min(self._selectedTank, len(vehicleTypes) - 1)
        vehicleType = vehicleTypes[index]
        vehicle = self._getVehiclesInInventory().get(makeVehicleTypeCompDescrByName(vehicleType), None)
        isVehInInventory = vehicle and vehicle.invID != -1
        if isVehInInventory and vehicle.isInBattle:
            SystemMessages.pushMessage(text=backport.text(R.strings.tooltips.hangar.tuning.disabled.body()), type=SystemMessages.SM_TYPE.ErrorHeader, messageData={'header': backport.text(R.strings.tooltips.hangar.tuning.disabled.header())})
            _logger.error('It is not possible to show customization view for vehicle while it is in battle')
            self.closeView()
            return
        else:
            style = self._getStyle(index)
            if not style:
                return
            styleItem = self.c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, style['styleID'])

            def styleCallback():
                ctx = self.c11nService.getCtx()
                ctx.changeMode(CustomizationModes.STYLED)
                ctx.selectItem(styleItem.intCD)

            if isVehInInventory:
                outfit = vehicle.getOutfit(vehicle.getAnyOutfitSeason())
                callback = styleCallback if not outfit.style or outfit.style.compactDescr != styleItem.intCD else None
                g_currentVehicle.selectVehicle(vehicle.invID)
                self.c11nService.showCustomization(vehicle.invID, callback=callback)
            else:
                self.__gotoStorage()
            return

    def onSelect(self, index):
        if self._selectVehicleByIndex(index):
            self._onSelect(index)

    def _onSelect(self, index):
        self._changeStyle(index)

    def showBlur(self):
        self.__blur.enable = True

    def hideBlur(self):
        self.__blur.enable = False

    def showMarkers(self):
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)

    def hideMarkers(self):
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        self._carouselDP = TradeCarouselDataProvider()
        self._carouselDP.setFlashObject(self.as_getDataProviderS())
        super(EventStylesTradeBase, self)._populate()
        self._updateData()
        self.__highlightController.start(self._highlightHangarVehicle)
        self.itemsCache.onSyncCompleted += self.__onCacheResync

    def _dispose(self):
        self._carouselDP = None
        self.__highlightController.stop(self._highlightHangarVehicle)
        self.hideBlur()
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        super(EventStylesTradeBase, self)._dispose()
        return

    def _selectVehicleByIndex(self, index):
        if index == self._carouselDP.pyGetSelectedIdx() and index == self._selectedTank:
            _logger.debug('Vehicle with index: %s already selected.', index)
            return False
        self._carouselDP.setSelectedIndex(index)
        self._carouselDP.refresh()
        self._selectedTank = index
        _logger.debug('Vehicle with index %s selected.', index)
        return True

    def _getSkinVO(self, style):
        vehiclesInInventory = self._getVehiclesInInventory()
        stylesInInventory = self._getStylesInInventory()
        currency, price = style['currency'], style['price']
        styleID = int(style['styleID'])
        vehicleDescr = VehicleDescriptor(typeName=style['vehicle'])
        vehicleType = vehicleDescr.type
        styleItem = self.c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
        curAmount = self._getCurrencyAmount(currency)
        bonusValue = 0
        for container in (styleItem.getOutfit(season).hull for season in SeasonType.SEASONS if styleItem.getOutfit(season)):
            camoIntCD = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItemCD()
            camo = self.c11nService.getItemByCD(camoIntCD) if camoIntCD else None
            if camo and camo.bonus:
                _, bonusValue = vehicleDescr.computeBaseInvisibility(crewFactor=0, camouflageId=camo.id)
                break

        notEnoughCount = max(price - curAmount, 0)
        isGold = currency == CURRENCIES_CONSTANTS.GOLD
        specialAlias = TOOLTIPS_CONSTANTS.EVENT_GOLD_ERROR if isGold else TOOLTIPS_CONSTANTS.EVENT_TOKEN_ERROR
        if vehicleType.compactDescr in vehiclesInInventory:
            description = backport.text(R.strings.event.tradeStyles.warningHasTank())
        else:
            description = backport.text(R.strings.event.tradeStyles.warning(), name=vehicleType.shortUserString)
        return {'name': styleItem.userName,
         'header': backport.text(R.strings.event.tradeStyles.confirmationTitle(), name=vehicleType.shortUserString),
         'description': description,
         'price': price,
         'notEnoughCount': notEnoughCount,
         'buyButtonEnabled': price <= curAmount if self._DEACTIVATABLE_BUY_BUTTON else True,
         'currency': currency,
         'haveInStorage': styleID in stylesInInventory,
         'haveTank': vehicleType.compactDescr in vehiclesInInventory,
         'suitableTank': vehicleType.shortUserString,
         'image': styleItem.icon,
         'bonus': '+{:.0%}'.format(bonusValue),
         'tooltip': '',
         'specialArgs': [notEnoughCount],
         'specialAlias': specialAlias,
         'isSpecial': True}

    def _getVO(self):
        styles = self._getStyles()
        skins = [ self._getSkinVO(style) for style in styles ]
        return {'selectedIndex': self._selectedTank if len(styles) > 1 else 0,
         'skins': skins,
         'banners': []}

    def _updateData(self):
        if not self.gameEventController.getShop().shopData:
            return
        self.as_setDataS(self._getVO())
        styles = self._getStyles()
        stylesInInventory = self._getStylesInInventory()
        carouselItems = []
        for style in styles:
            currency, price = style['currency'], style['price']
            curAmount = self._getCurrencyAmount(currency)
            styleID = int(style['styleID'])
            vehicleDescriptor = VehicleDescriptor(typeName=style['vehicle'])
            vehicleType = vehicleDescriptor.type
            priceFormatted = {'price': ((currency, price),)}
            count = int(styleID in stylesInInventory)
            styleItem = self.c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
            carouselName = backport.text(R.strings.event.tradeStyles.carouselSkinName(), name=vehicleType.shortUserString)
            carouselItems.append((vehicleType.compactDescr,
             styleItem,
             priceFormatted,
             count,
             carouselName,
             curAmount >= price))

        self._carouselDP.clear()
        self._carouselDP.buildList(carouselItems)
        self._carouselDP.setSelectedIndex(self._selectedTank)
        self._carouselDP.refresh()

    def _getCurrencyAmount(self, currency):
        pass

    def _getStyles(self):
        return []

    def _getStyle(self, index):
        styles = self._getStyles()
        if index >= len(styles):
            _logger.error('Wrong style index %s %s', index, styles)
            return
        return styles[index]

    def _getVehicleTypes(self):
        styles = self._getStyles()
        return [ style['vehicle'] for style in styles ]

    def __onCacheResync(self, reason, diff):
        self._updateData()

    def _getVehiclesInInventory(self):
        return self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)

    def _getStylesInInventory(self):
        criteria = REQ_CRITERIA.INVENTORY ^ REQ_CRITERIA.CUSTOMIZATION.IS_INSTALLED_ON_ANY_VEHICLE
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.STYLE, criteria).itervalues()
        return set((item.id for item in items))

    def _changeStyle(self, index):
        style = self._getStyle(index)
        if not style:
            return
        typeName, styleID = style['vehicle'], style['styleID']
        vehicleDescr = vehicles.VehicleDescr(typeName=typeName)
        styleItem = self.c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
        g_currentPreviewVehicle.selectStyledVehicle(vehicleDescr, styleItem)

    def __gotoStorage(self):
        g_currentPreviewVehicle.selectNoVehicle()
        event_dispatcher.showStorage(STORAGE_CONSTANTS.CUSTOMIZATION)

    def __getVehicleShortName(self, vehicleCD):
        return self.itemsCache.items.getItemByCD(vehicleCD).shortUserName


class TradeCarouselDataProvider(ListDAAPIDataProvider):

    def __init__(self):
        super(TradeCarouselDataProvider, self).__init__()
        self.__list = []
        self.__selectedIndex = -1

    @property
    def collection(self):
        return self.__list

    def emptyItem(self):
        return None

    def clear(self):
        self.__list = []
        self.__selectedIndex = -1

    def fini(self):
        self.clear()
        self.destroy()

    def setSelectedIndex(self, index):
        self.__selectedIndex = index

    def buildList(self, changedStyleCDs):
        for vehicleID, style, price, count, name, buyOperationAllowed in changedStyleCDs:
            self.__list.append(self.__buildCustomizationItemData(style, vehicleID, price, count, name, buyOperationAllowed))

        if self.__selectedIndex == -1:
            self.__selectedIndex = 0

    def pyGetSelectedIdx(self):
        return self.__selectedIndex

    @staticmethod
    def __buildCustomizationItemData(item, vehicleCD, price, count, name, buyOperationAllowed):
        voDict = buildCustomizationItemDataVO(item=item, count=count, plainView=False, showDetailItems=True, addExtraName=False)
        voDict['customVehicleCD'] = vehicleCD
        voDict['styleName'] = voDict['styleNameSmall'] = name
        voDict['buyPrice'] = price
        voDict['buyOperationAllowed'] = buyOperationAllowed
        return voDict
