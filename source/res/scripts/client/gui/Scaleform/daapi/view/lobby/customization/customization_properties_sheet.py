# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_properties_sheet.py
from collections import namedtuple
from itertools import islice
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.customization.shared import SEASONS_ORDER, SEASON_TYPE_TO_NAME, TABS_ITEM_MAPPING, CAMO_SCALE_SIZE
from gui.Scaleform.daapi.view.meta.CustomizationPropertiesSheetMeta import CustomizationPropertiesSheetMeta
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, C11nTabs
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles, currency
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.processors.vehicle import VehicleAutoStyleEquipProcessor
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from helpers.i18n import makeString as _ms
from gui.shared.gui_items.customization.c11n_items import camoIconTemplate
from skeletons.gui.shared import IItemsCache
from items.components.c11n_constants import SeasonType
from gui.customization.shared import getAppliedRegionsForCurrentHangarVehicle, getCustomizationTankPartName
from gui.shared.gui_items.customization.outfit import Area
CustomizationCamoSwatchVO = namedtuple('CustomizationCamoSwatchVO', 'paletteIcon selected')
_MAX_PALETTES = 3
_PALETTE_TEXTURE = 'gui/maps/vehicles/camouflages/camo_palette_{colornum}.dds'
_DEFAULT_COLORNUM = 1
_PALETTE_BACKGROUND = 'gui/maps/vehicles/camouflages/camo_palettes_back.dds'
_PALETTE_WIDTH = 75
_PALETTE_HEIGHT = 18

class CustomizationPropertiesSheet(CustomizationPropertiesSheetMeta):
    itemsCache = dependency.instance(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        super(CustomizationPropertiesSheet, self).__init__()
        self.__ctx = None
        self._slotID = -1
        self._regionID = -1
        self._areaID = -1
        self._isVisible = False
        self._extraMoney = None
        self._isItemAppliedToAll = False
        self.__autoRentEnabled = False
        return

    @property
    def isVisible(self):
        return self._isVisible

    def _populate(self):
        super(CustomizationPropertiesSheet, self)._populate()
        self.__ctx = self.service.getCtx()
        self._extraMoney = None
        self._isItemAppliedToAll = False
        self.__ctx.onCacheResync += self.__onCacheResync
        self.__ctx.onCustomizationSeasonChanged += self.__onSeasonChanged
        self.__ctx.onCustomizationItemInstalled += self.__onItemsInstalled
        self.__ctx.onCustomizationItemsRemoved += self.__onItemsRemoved
        self.__ctx.onCustomizationCamouflageColorChanged += self.__onCamouflageColorChanged
        self.__ctx.onCustomizationCamouflageScaleChanged += self.__onCamouflageScaleChanged
        self.__ctx.onCustomizationItemsBought += self.__onItemsBought
        self.__ctx.onCustomizationItemSold += self.__onItemSold
        return

    def _dispose(self):
        self.__ctx.onCustomizationItemSold -= self.__onItemSold
        self.__ctx.onCustomizationItemsBought -= self.__onItemsBought
        self.__ctx.onCustomizationCamouflageScaleChanged -= self.__onCamouflageScaleChanged
        self.__ctx.onCustomizationCamouflageColorChanged -= self.__onCamouflageColorChanged
        self.__ctx.onCustomizationItemsRemoved -= self.__onItemsRemoved
        self.__ctx.onCustomizationItemInstalled -= self.__onItemsInstalled
        self.__ctx.onCustomizationSeasonChanged -= self.__onSeasonChanged
        self.__ctx.onCacheResync -= self.__onCacheResync
        self._extraMoney = None
        self._isItemAppliedToAll = False
        self._slotID = -1
        self._regionID = -1
        self._areaID = -1
        self.__ctx = None
        super(CustomizationPropertiesSheet, self)._dispose()
        return

    def show(self, areaID, slotID, regionID):
        if self._slotID == slotID and self._regionID == regionID and self._areaID == areaID and self.isVisible:
            return
        self._slotID = slotID
        self._regionID = regionID
        self._areaID = areaID
        self._isVisible = True
        if self.__update():
            self.__ctx.onPropertySheetShown()

    def hide(self):
        if not self.isVisible:
            return
        self._isVisible = False
        self.as_hideS()
        self.__ctx.onPropertySheetHidden()

    def onActionBtnClick(self, actionType, applyToAll):
        if actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS:
            self.__applyToOtherAreas(applyToAll)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS:
            self.__applyToOtherSeasons(applyToAll)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE:
            self.__removeElement()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_RENT_CHECKBOX_CHANGE:
            self.__autoRentEnabled = not self.__autoRentEnabled
            self.__setAutoRent(self.__autoRentEnabled)

    def setCamouflageColor(self, paletteIdx):
        if self._currentComponent.palette != paletteIdx:
            self.__ctx.changeCamouflageColor(self._areaID, self._regionID, paletteIdx)

    def onClose(self):
        self.hide()

    def setCamouflageScale(self, scale, scaleIndex):
        if self._currentComponent.patternSize != scale:
            self.__ctx.changeCamouflageScale(self._areaID, self._regionID, scale)

    @property
    def _currentMultiSlot(self):
        if self._slotID == -1 or self._areaID == -1:
            return None
        else:
            return self.__ctx.currentOutfit.getContainer(self._areaID).slotFor(self._slotID) if self._slotID != GUI_ITEM_TYPE.STYLE else None

    @property
    def _currentSlotData(self):
        slot = self._currentMultiSlot
        return None if not slot or self._regionID == -1 else slot.getSlotData(self._regionID)

    @property
    def _currentItem(self):
        slot = self._currentMultiSlot
        return None if not slot or self._regionID == -1 else slot.getItem(self._regionID)

    @property
    def _currentComponent(self):
        slot = self._currentMultiSlot
        return None if not slot or self._regionID == -1 else slot.getComponent(self._regionID)

    @property
    def _currentStyle(self):
        return self.__ctx.modifiedStyle if self._slotID == GUI_ITEM_TYPE.STYLE else None

    def __update(self):
        if self._isVisible and self._slotID != -1 and self._regionID != -1 and self._areaID != -1:
            self.__updateItemAppliedToAllFlag()
            self.__updateExtraPrice()
            self.__autoRentEnabled = g_currentVehicle.item.isAutoRentStyle
            self.as_setDataAndShowS(self.__makeVO())
            return True
        return False

    def __applyToOtherAreas(self, installItem):
        if self.__ctx.currentTab not in (C11nTabs.PAINT, C11nTabs.CAMOUFLAGE):
            return
        currentSeason = self.__ctx.currentSeason
        if installItem:
            self.__ctx.installItemToAllTankAreas(currentSeason, self._slotID, self._currentSlotData)
        else:
            self.__ctx.removeItemFromAllTankAreas(currentSeason, self._slotID)
        self.__update()

    def __applyToOtherSeasons(self, installItem):
        if self.__ctx.currentTab not in (C11nTabs.EFFECT, C11nTabs.EMBLEM, C11nTabs.INSCRIPTION):
            return
        if installItem:
            self.__ctx.installItemForAllSeasons(self._areaID, self._slotID, self._regionID, self._currentSlotData)
        else:
            self.__ctx.removeItemForAllSeasons(self._areaID, self._slotID, self._regionID)
        self.__update()

    def __removeElement(self):
        if self._slotID == GUI_ITEM_TYPE.STYLE:
            self.__ctx.removeStyle(self._currentStyle.intCD)
        else:
            self.__ctx.removeItemFromRegion(self.__ctx.currentSeason, self._areaID, self._slotID, self._regionID)

    def __updateItemAppliedToAllFlag(self):
        self._isItemAppliedToAll = False
        if self.__ctx.currentTab in (C11nTabs.PAINT, C11nTabs.CAMOUFLAGE):
            self._isItemAppliedToAll = True
            for areaId in Area.TANK_PARTS:
                regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, self._slotID)
                multiSlot = self.__ctx.currentOutfit.getContainer(areaId).slotFor(self._slotID)
                for regionIdx in regionsIndexes:
                    slotData = multiSlot.getSlotData(regionIdx)
                    df = self._currentSlotData.weakDiff(slotData)
                    if slotData.item is None or df.item is not None:
                        break
                else:
                    continue

                self._isItemAppliedToAll = False
                break

        elif self.__ctx.currentTab in (C11nTabs.EFFECT, C11nTabs.EMBLEM, C11nTabs.INSCRIPTION):
            self._isItemAppliedToAll = True
            firstSeason = SeasonType.COMMON_SEASONS[0]
            fistSlotData = self.__ctx.getModifiedOutfit(firstSeason).getContainer(self._areaID).slotFor(self._slotID).getSlotData(self._regionID)
            if fistSlotData.item is not None:
                for season in SeasonType.COMMON_SEASONS[1:]:
                    slotData = self.__ctx.getModifiedOutfit(season).getContainer(self._areaID).slotFor(self._slotID).getSlotData(self._regionID)
                    df = fistSlotData.weakDiff(slotData)
                    if slotData.item is None or df.item is not None:
                        self._isItemAppliedToAll = False
                        break

            else:
                self._isItemAppliedToAll = False
        return

    def __makeVO(self):
        currentElement = self._currentStyle if self._slotID == GUI_ITEM_TYPE.STYLE else self._currentItem
        titleText, descrText = self.__getTitleDescrTexts(currentElement)
        slotImgSrc = ''
        if not currentElement:
            slotImgSrc = RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK_POPOVER_SMALL
        elif self._slotID == GUI_ITEM_TYPE.STYLE and self._currentStyle.isHiddenInUI():
            slotImgSrc = self._currentStyle.icon
        vo = {'intCD': -1 if not currentElement else currentElement.intCD,
         'titleImageSrc': self.__getTitleImage(),
         'titleText': titleText,
         'descrText': descrText,
         'slotImgSrc': slotImgSrc,
         'renderers': self.__makeRenderersVOs() if currentElement else []}
        return vo

    def __makeSlotVO(self):
        vo = None
        if not self._currentItem:
            vo = {'imgIconSrc': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK_POPOVER_SMALL}
        return vo

    def __getTitleImage(self):
        if self._slotID == GUI_ITEM_TYPE.STYLE:
            return ''
        seasonName = SEASON_TYPE_TO_NAME.get(self.__ctx.currentSeason)
        return RES_ICONS.getSeasonTopImage(seasonName)

    def __getTitleDescrTexts(self, currentElement):
        if self._slotID == GUI_ITEM_TYPE.STYLE:
            if not currentElement:
                titleText = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ELEMENTTYPE_ALL
            else:
                titleText = currentElement.userName
        elif self._slotID == GUI_ITEM_TYPE.MODIFICATION:
            titleText = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ELEMENTTYPE_ALL
        elif self._slotID == GUI_ITEM_TYPE.INSCRIPTION:
            titleText = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ELEMENTTYPE_INSCRIPTION
        elif self._slotID == GUI_ITEM_TYPE.EMBLEM:
            titleText = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ELEMENTTYPE_EMBLEM
        else:
            titleText = VEHICLE_CUSTOMIZATION.getSheetVehPartName(getCustomizationTankPartName(self._areaID, self._regionID))
        if not currentElement:
            itemTypeID = TABS_ITEM_MAPPING.get(self.__ctx.currentTab)
            itemTypeName = GUI_ITEM_TYPE_NAMES[itemTypeID]
            descrText = text_styles.neutral(VEHICLE_CUSTOMIZATION.getSheetEmptyDescription(itemTypeName))
        elif self._slotID == GUI_ITEM_TYPE.STYLE:
            descrText = text_styles.main(currentElement.userType)
        elif self._slotID == GUI_ITEM_TYPE.CAMOUFLAGE:
            descrText = text_styles.main(currentElement.userName)
        else:
            descrText = text_styles.main(_ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_DESCRIPTION, itemType=currentElement.userType, itemName=currentElement.userName))
        return (text_styles.highTitle(titleText), descrText)

    def __makeRenderersVOs(self):
        renderers = []
        isExtentionEnabled = False
        if self._slotID == GUI_ITEM_TYPE.PAINT:
            renderers.append(self.__makeSetOnOtherTankPartsRendererVO())
        elif self._slotID == GUI_ITEM_TYPE.CAMOUFLAGE:
            vo = self.__makeCamoColorRendererVO()
            if vo is not None:
                renderers.append(vo)
            renderers.append(self.__makeCamoScaleRendererVO())
            renderers.append(self.__makeSetOnOtherTankPartsRendererVO())
        elif self._slotID == GUI_ITEM_TYPE.EMBLEM or self._slotID == GUI_ITEM_TYPE.INSCRIPTION or self._slotID == GUI_ITEM_TYPE.MODIFICATION:
            renderers.append(self.__makeSetOnOtherSeasonsRendererVO())
        elif self._slotID == GUI_ITEM_TYPE.STYLE and not self._currentStyle.isHiddenInUI():
            vo = self.__makeStyleRendererVO()
            if vo is not None:
                renderers += vo
            isExtentionEnabled = self._currentStyle and self._currentStyle.isRentable
            if isExtentionEnabled:
                renderers.append(self.__makeExtensionRendererVO())
        renderers.append(self.__makeRemoveRendererVO(not isExtentionEnabled))
        return renderers

    def __updateExtraPrice(self):
        if self._isItemAppliedToAll and self._currentItem:
            appliedIems = tuple((it for it in self.__ctx.getPurchaseItems() if not it.isDismantling and it.item.intCD == self._currentItem.intCD))
            if self.__ctx.currentTab in (C11nTabs.PAINT, C11nTabs.CAMOUFLAGE):
                appliedIems = tuple((it for it in appliedIems if it.group == self.__ctx.currentSeason))
            purchaseItems = tuple((it for it in appliedIems if not it.isFromInventory))
            fromInventoryItems = tuple((it for it in appliedIems if it.isFromInventory))
            itemCache = self.itemsCache.items.getItemByCD(self._currentItem.intCD)
            appliedItemPrice = itemCache.getBuyPrice()
            extraInventoryCount = max(0, len(purchaseItems) - int(not fromInventoryItems))
            self._extraMoney = appliedItemPrice.price * extraInventoryCount
        else:
            self._extraMoney = None
        return

    def __makeSetOnOtherTankPartsRendererVO(self):
        extraPriceCurrency = ''
        extraPriceText = ''
        if not self._isItemAppliedToAll:
            currPartName = VEHICLE_CUSTOMIZATION.getSheetVehPartName(getCustomizationTankPartName(self._areaID, self._regionID))
            titleText = text_styles.standard(_ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_TITLE_APPLIEDTO, elementType=text_styles.neutral(currPartName)))
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_APPLYTOWHOLETANK
            actionBtnIconSrc = ''
        else:
            titleText = text_styles.neutral(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_TITLE_ALLTANKPAINTED)
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_CANCEL
            actionBtnIconSrc = RES_ICONS.MAPS_ICONS_LIBRARY_ASSET_1
            if self._extraMoney:
                extraPriceCurrency = self._extraMoney.getCurrency()
                if self._extraMoney.get(extraPriceCurrency):
                    extraPriceText = '{}{}'.format(currency.getStyle(extraPriceCurrency)('+'), currency.applyAll(extraPriceCurrency, self._extraMoney.get(extraPriceCurrency)))
        return {'titleText': titleText,
         'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_TANK,
         'actionBtnLabel': actionBtnLabel,
         'actionBtnIconSrc': actionBtnIconSrc,
         'isAppliedToAll': self._isItemAppliedToAll,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'extraPriceText': extraPriceText,
         'extraPriceIcon': extraPriceCurrency}

    def __makeRemoveRendererVO(self, separatorVisible=True):
        iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_CROSS
        if self._slotID == GUI_ITEM_TYPE.STYLE:
            titleText = ''
            iconSrc = ''
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVESTYLE
        else:
            itemTypeID = TABS_ITEM_MAPPING.get(self.__ctx.currentTab)
            itemTypeName = GUI_ITEM_TYPE_NAMES[itemTypeID]
            titleText = VEHICLE_CUSTOMIZATION.getSheetRemoveText(itemTypeName)
            if self._slotID == GUI_ITEM_TYPE.MODIFICATION:
                actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_TANK
            elif self._slotID == GUI_ITEM_TYPE.EMBLEM:
                actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_EMBLEM
            elif self._slotID == GUI_ITEM_TYPE.INSCRIPTION:
                actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_INSCRIPTION
            else:
                actionBtnLabel = VEHICLE_CUSTOMIZATION.getSheetBtnRemoveText(getCustomizationTankPartName(self._areaID, self._regionID))
        return {'titleText': text_styles.standard(titleText),
         'iconSrc': iconSrc,
         'actionBtnLabel': actionBtnLabel,
         'actionBtnIconSrc': RES_ICONS.MAPS_ICONS_LIBRARY_ASSET_1,
         'isAppliedToAll': False,
         'separatorVisible': separatorVisible,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE}

    def __makeExtensionRendererVO(self):
        return {'actionBtnLabel': _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_AUTOPROLONGATIONLABEL),
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_RENT_CHECKBOX_CHANGE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_CHECKBOX_RENDERER_UI,
         'isSelected': self.__autoRentEnabled}

    def __makeCamoColorRendererVO(self):
        btnsBlockVO = []
        colornum = _DEFAULT_COLORNUM
        for palette in self._currentItem.palettes:
            colornum = max(colornum, sum(((color >> 24) / 255.0 > 0 for color in palette)))

        for idx, palette in enumerate(islice(self._currentItem.palettes, _MAX_PALETTES)):
            texture = _PALETTE_TEXTURE.format(colornum=colornum)
            icon = camoIconTemplate(texture, _PALETTE_WIDTH, _PALETTE_HEIGHT, palette, background=_PALETTE_BACKGROUND)
            btnsBlockVO.append(CustomizationCamoSwatchVO(icon, idx == self._currentComponent.palette)._asdict())

        return {'titleText': text_styles.standard(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_TITLE_COLOR),
         'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_COLORS,
         'isAppliedToAll': False,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_COLOR_CHANGE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_SCALE_COLOR_RENDERER_UI,
         'btnsBlockVO': btnsBlockVO,
         'btnsGroupName': CUSTOMIZATION_ALIASES.COLOR_BTNS_GROUP} if len(btnsBlockVO) == _MAX_PALETTES else None

    def __makeCamoScaleRendererVO(self):
        btnsBlockVO = []
        for idx in xrange(len(CAMO_SCALE_SIZE)):
            btnsBlockVO.append({'paletteIcon': '',
             'label': CAMO_SCALE_SIZE[idx],
             'selected': self._currentComponent.patternSize == idx,
             'value': idx})

        return {'titleText': text_styles.standard(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_TITLE_SCALE),
         'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_SCALE,
         'isAppliedToAll': False,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_SCALE_CHANGE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_SCALE_COLOR_RENDERER_UI,
         'btnsBlockVO': btnsBlockVO,
         'btnsGroupName': CUSTOMIZATION_ALIASES.SCALE_BTNS_GROUP}

    def __makeSetOnOtherSeasonsRendererVO(self):
        activeSeason = SEASON_TYPE_TO_NAME.get(self.__ctx.currentSeason)
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_APPLYTOALLMAPS
        actionBtnIconSrc = ''
        extraPriceText = ''
        extraPriceCurrency = ''
        if self._isItemAppliedToAll:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_SEASONS
            actionBtnIconSrc = RES_ICONS.MAPS_ICONS_LIBRARY_ASSET_1
            titleText = text_styles.neutral(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_TITLE_ALLMAPS)
            if self._extraMoney:
                extraPriceCurrency = self._extraMoney.getCurrency()
                if self._extraMoney.get(extraPriceCurrency):
                    extraPriceText = '{}{}'.format(currency.getStyle(extraPriceCurrency)('+'), currency.applyAll(extraPriceCurrency, self._extraMoney.get(extraPriceCurrency)))
        else:
            titleText = text_styles.standard(_ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_TITLE_APPLIEDTOMAP, mapType=text_styles.neutral(VEHICLE_CUSTOMIZATION.getSheetSeasonName(activeSeason))))
        return {'titleText': titleText,
         'iconSrc': RES_ICONS.getSeasonIcon(activeSeason),
         'actionBtnLabel': actionBtnLabel,
         'actionBtnIconSrc': actionBtnIconSrc,
         'isAppliedToAll': self._isItemAppliedToAll,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'extraPriceText': extraPriceText,
         'extraPriceIcon': extraPriceCurrency,
         'btnEnabled': not g_currentVehicle.isOnlyForEventBattles()}

    def __makeStyleRendererVO(self):
        seasonItemData = []
        allUnique = set()
        if self._currentStyle:
            smallRenderers = True
            for season in SEASONS_ORDER:
                seasonName = SEASON_TYPE_TO_NAME.get(season)
                seasonUnique = set()
                outfit = self._currentStyle.getOutfit(season)
                items = []
                for item, component in outfit.itemsFull():
                    if item.intCD not in seasonUnique and not item.isHiddenInUI():
                        items.append({'image': item.getIconApplied(component),
                         'specialArgs': item.getSpecialArgs(component),
                         'isWide': item.isWide(),
                         'intCD': item.intCD})
                    allUnique.add(item.intCD)
                    seasonUnique.add(item.intCD)
                    if len(items) > 1 and smallRenderers:
                        smallRenderers = False

                titleText = VEHICLE_CUSTOMIZATION.getSheetSeasonName(seasonName)
                seasonItemData.append({'titleText': text_styles.standard(titleText),
                 'itemRendererVOs': items,
                 'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_STYLE_RENDERER_UI})

            for item in seasonItemData:
                item['isSmall'] = smallRenderers

            return seasonItemData

    @decorators.process('loadStats')
    def __setAutoRent(self, autoRent):
        yield VehicleAutoStyleEquipProcessor(g_currentVehicle.item, autoRent).request()

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            self.hide()
            return
        if self.__ctx.mode == C11nMode.CUSTOM:
            self.hide()
        else:
            self.__update()

    def __onSeasonChanged(self, seasonIdx):
        self.__update()

    def __onCamouflageColorChanged(self, areaId, regionIdx, paletteIdx):
        self.__update()

    def __onCamouflageScaleChanged(self, areaId, regionIdx, scale):
        self.__update()

    def __onItemsInstalled(self):
        self.__update()

    def __onItemsRemoved(self):
        self.__update()

    def __onItemsBought(self, purchaseItems, results):
        self.__update()

    def __onItemSold(self, item, count):
        self.__update()
