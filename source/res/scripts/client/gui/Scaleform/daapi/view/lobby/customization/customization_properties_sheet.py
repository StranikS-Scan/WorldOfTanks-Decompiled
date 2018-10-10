# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_properties_sheet.py
from collections import namedtuple
from itertools import islice
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.customization.shared import SCALE_SIZE
from gui.Scaleform.daapi.view.meta.CustomizationPropertiesSheetMeta import CustomizationPropertiesSheetMeta
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, C11nTabs
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from gui.shared.gui_items.customization.c11n_items import camoIconTemplate
from skeletons.gui.shared import IItemsCache
from items.components.c11n_constants import SeasonType
from gui.customization.shared import getAppliedRegionsForCurrentHangarVehicle, getCustomizationTankPartName, C11nId
from gui.shared.gui_items.customization.outfit import Area
from skeletons.gui.shared.utils import IHangarSpace
CustomizationCamoSwatchVO = namedtuple('CustomizationCamoSwatchVO', 'paletteIcon selected')
_MAX_PALETTES = 3
_PALETTE_TEXTURE = 'gui/maps/vehicles/camouflages/camo_palette_{colornum}.dds'
_DEFAULT_COLORNUM = 1
_PALETTE_BACKGROUND = 'gui/maps/vehicles/camouflages/camo_palettes_back.dds'
_PALETTE_WIDTH = 42
_PALETTE_HEIGHT = 42
_C11nEditModes = {CUSTOMIZATION_ALIASES.CUSTOMIZATION_POJECTION_INTERACTION_DEFAULT: 0,
 CUSTOMIZATION_ALIASES.CUSTOMIZATION_POJECTION_INTERACTION_MOVE: 1,
 CUSTOMIZATION_ALIASES.CUSTOMIZATION_POJECTION_INTERACTION_SCALE: 2,
 CUSTOMIZATION_ALIASES.CUSTOMIZATION_POJECTION_INTERACTION_ROTATION: 3}

class CustomizationPropertiesSheet(CustomizationPropertiesSheetMeta):
    itemsCache = dependency.instance(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(CustomizationPropertiesSheet, self).__init__()
        self.__ctx = None
        self._slotID = -1
        self._regionID = -1
        self._areaID = -1
        self._isVisible = False
        self._editMode = False
        self._extraMoney = None
        self._isItemAppliedToAll = False
        self.__interactionType = CUSTOMIZATION_ALIASES.CUSTOMIZATION_POJECTION_INTERACTION_DEFAULT
        self.__changes = [False] * 3
        return

    @property
    def isVisible(self):
        return self._isVisible

    def editMode(self, value, interactionType):
        self._editMode = value
        if self._editMode:
            self.__interactionType = interactionType
        else:
            self.interactionStatusUpdate(False)
            self.__interactionType = -1

    def interactionStatusUpdate(self, value):
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_CAMERA_MOVEMENT, ctx={'disable': value}), EVENT_BUS_SCOPE.DEFAULT)

    def setScale(self, value):
        pass

    def setRotation(self, value):
        pass

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
        self.__ctx.onCustomizationProjectionDecalScaleChanged += self.__onProjectionDecalScaleChanged
        self.__ctx.onCustomizationItemsBought += self.__onItemsBought
        self.__ctx.onCustomizationItemSold += self.__onItemSold
        return

    def _dispose(self):
        self.__ctx.onCustomizationItemSold -= self.__onItemSold
        self.__ctx.onCustomizationItemsBought -= self.__onItemsBought
        self.__ctx.onCustomizationCamouflageScaleChanged -= self.__onCamouflageScaleChanged
        self.__ctx.onCustomizationCamouflageColorChanged -= self.__onCamouflageColorChanged
        self.__ctx.onCustomizationProjectionDecalScaleChanged -= self.__onProjectionDecalScaleChanged
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
        self.__ctx.vehicleAnchorsUpdater.displayMenu(True)

    def hide(self):
        if not self.isVisible:
            return
        self._isVisible = False
        self.as_hideS()
        self.__ctx.onPropertySheetHidden()
        self.__ctx.vehicleAnchorsUpdater.displayMenu(False)

    def onActionBtnClick(self, actionType, actionData):
        if actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS:
            self._isItemAppliedToAll = not self._isItemAppliedToAll
            self.__applyToOtherAreas(self._isItemAppliedToAll)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS:
            self._isItemAppliedToAll = not self._isItemAppliedToAll
            self.__applyToOtherSeasons(self._isItemAppliedToAll)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE:
            self.__removeElement()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_RENT_CHECKBOX_CHANGE:
            self.__ctx.changeAutoRent()
            self.__update()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_PARTS:
            self.__removeFromAllAreas()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_SCALE_CHANGE:
            if self._slotID == GUI_ITEM_TYPE.CAMOUFLAGE:
                if self._currentComponent.patternSize != actionData:
                    self.__ctx.changeCamouflageScale(self._areaID, self._regionID, actionData)
            elif self._slotID == GUI_ITEM_TYPE.PROJECTION_DECAL:
                actionData += 1
                if self._currentComponent.scaleFactorId != actionData:
                    self.__ctx.changeProjectionDecalScale(self._areaID, self._regionID, actionData)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_COLOR_CHANGE:
            if self._currentComponent.palette != actionData:
                self.__ctx.changeCamouflageColor(self._areaID, self._regionID, actionData)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_CLOSE:
            self.hide()
            self.__ctx.onClearItem()

    def onClose(self):
        self.hide()

    @property
    def _currentSlotData(self):
        if self._slotID == -1 or self._areaID == -1 or self._slotID == GUI_ITEM_TYPE.STYLE:
            return
        else:
            slot = self.__ctx.currentOutfit.getContainer(self._areaID).slotFor(self._slotID)
            if slot is None or self._regionID == -1:
                return
            slotId = self.__ctx.getSlotIdByAnchorId(C11nId(self._areaID, self._slotID, self._regionID))
            return slot.getSlotData(slotId.regionIdx)

    @property
    def _currentItem(self):
        slotData = self._currentSlotData
        return None if slotData is None else slotData.item

    @property
    def _currentComponent(self):
        slotData = self._currentSlotData
        return None if slotData is None else slotData.component

    @property
    def _currentStyle(self):
        return self.__ctx.modifiedStyle if self._slotID == GUI_ITEM_TYPE.STYLE else None

    def __update(self):
        if self._isVisible and self._slotID != -1 and self._regionID != -1 and self._areaID != -1:
            self.__updateItemAppliedToAllFlag()
            self.__updateExtraPrice()
            self.as_setDataAndShowS(self.__makeVO())
            self.__ctx.caruselItemUnselected()
            self.__ctx.onPropertySheetShown()
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

    def __removeFromAllAreas(self):
        currentSeason = self.__ctx.currentSeason
        self.__ctx.removeItemFromAllTankAreas(currentSeason, self._slotID)
        self.__update()

    def __applyToOtherSeasons(self, installItem):
        if self.__ctx.currentTab not in (C11nTabs.EFFECT,
         C11nTabs.EMBLEM,
         C11nTabs.INSCRIPTION,
         C11nTabs.PROJECTION_DECAL):
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
            slotId = self.__ctx.getSlotIdByAnchorId(C11nId(areaId=self._areaID, slotType=self._slotID, regionIdx=self._regionID))
            if slotId is not None:
                self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, slotId)
        return

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
        vo = {'intCD': -1 if not currentElement else currentElement.intCD,
         'renderersData': self.__makeRenderersVOs() if currentElement else [],
         'isProjectionEnable': self._slotID == GUI_ITEM_TYPE.PROJECTION_DECAL,
         'isBigRadius': self._slotID in (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.PROJECTION_DECAL, GUI_ITEM_TYPE.EMBLEM)}
        return vo

    def __makeSlotVO(self):
        vo = None
        if not self._currentItem:
            vo = {'imgIconSrc': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK_POPOVER_SMALL}
        return vo

    def __makeRenderersVOs(self):
        renderers = []
        if self._slotID == GUI_ITEM_TYPE.PAINT:
            renderers.append(self.__makeSetOnOtherTankPartsRendererVO())
        elif self._slotID == GUI_ITEM_TYPE.CAMOUFLAGE:
            vo = self.__makeCamoColorRendererVO()
            if vo is not None:
                renderers.append(vo)
            renderers.append(self.__makeScaleRendererVO())
            renderers.append(self.__makeSetOnOtherTankPartsRendererVO())
        elif self._slotID in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.MODIFICATION):
            renderers.append(self.__makeSetOnOtherSeasonsRendererVO())
        elif self._slotID == GUI_ITEM_TYPE.STYLE:
            isExtentionEnabled = self._currentStyle and self._currentStyle.isRentable
            if isExtentionEnabled:
                renderers.append(self.__makeExtensionRendererVO())
        elif self._slotID == GUI_ITEM_TYPE.PROJECTION_DECAL:
            renderers.append(self.__makeScaleRendererVO())
        renderers.append(self.__makeRemoveRendererVO())
        renderers.append(self.__makeCloseeRendererVO())
        return renderers

    def __updateExtraPrice(self):
        if self._isItemAppliedToAll and self._currentItem:
            appliedIems = tuple((it for it in self.__ctx.getPurchaseItems() if not it.isDismantling and it.item.intCD == self._currentItem.intCD))
            if self.__ctx.currentTab in (C11nTabs.PAINT, C11nTabs.CAMOUFLAGE):
                appliedIems = tuple((it for it in appliedIems if it.group == self.__ctx.currentSeason))
            outfit = self.__ctx.originalOutfit
            slotData = outfit.getContainer(self._areaID).slotFor(self._slotID).getSlotData(self._regionID)
            isCurrentlyApplied = slotData.item == self._currentItem
            itemCache = self.itemsCache.items.getItemByCD(self._currentItem.intCD)
            inventoryCount = itemCache.inventoryCount
            appliedItemPrice = itemCache.getBuyPrice()
            extraInventoryCount = max(0, len(appliedIems) - max(inventoryCount, int(not isCurrentlyApplied)))
            self._extraMoney = appliedItemPrice.price * extraInventoryCount
        else:
            self._extraMoney = None
        return

    def __makeSetOnOtherTankPartsRendererVO(self):
        icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_TANK
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_TANK_HOVER
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_APPLYTOWHOLETANK
        if self._isItemAppliedToAll:
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_DEL_TANK
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_DEL_TANK_HOVER
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_CANCEL
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'actionBtnLabel': text_styles.tutorial(actionBtnLabel),
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI}

    def __removeAllTankPartsRendererVO(self):
        icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_DEL_TANK
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_DEL_TANK_HOVER
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_CLEAR
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'actionBtnLabel': text_styles.tutorial(actionBtnLabel),
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_PARTS,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI}

    def __makeRemoveRendererVO(self):
        iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_CROSS
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_CROSS_HOVER
        if self._slotID == GUI_ITEM_TYPE.STYLE:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVESTYLE
            iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_STYLE_X
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_STYLE_X_HOVER
        else:
            if self._slotID == GUI_ITEM_TYPE.MODIFICATION:
                actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_TANK
                iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_EFFECTS_X
                hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_EFFECTS_X_HOVER
            elif self._slotID == GUI_ITEM_TYPE.EMBLEM:
                actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_EMBLEM
                iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_EMBLEM_X
                hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_EMBLEM_X_HOVER
            elif self._slotID == GUI_ITEM_TYPE.INSCRIPTION:
                actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_INSCRIPTION
                iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_TYPE_X
                hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_TYPE_X_HOVER
            elif self._slotID == GUI_ITEM_TYPE.PROJECTION_DECAL:
                actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_PROJECTIONDECAL
                iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_EFFECTS_X
                hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_EFFECTS_X_HOVER
            else:
                actionBtnLabel = VEHICLE_CUSTOMIZATION.getSheetBtnRemoveText(getCustomizationTankPartName(self._areaID, self._regionID))
            if self._slotID == GUI_ITEM_TYPE.CAMOUFLAGE:
                iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_CAMO_X
                hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_CAMO_X_HOVER
            elif self._slotID == GUI_ITEM_TYPE.PAINT:
                iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_COLORS_X
                hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_COLORS_X_HOVER
        return {'iconSrc': iconSrc,
         'iconHoverSrc': hoverIcon,
         'actionBtnLabel': text_styles.tutorial(actionBtnLabel),
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE}

    def __makeCloseeRendererVO(self):
        iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_CROSS
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_CROSS_HOVER
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_CLOSE
        return {'iconSrc': iconSrc,
         'iconHoverSrc': hoverIcon,
         'actionBtnLabel': text_styles.tutorial(actionBtnLabel),
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_CLOSE}

    def __makeExtensionRendererVO(self):
        if self.__ctx.autoRentEnabled():
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_DEL_RENT
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_DEL_RENT_HOVER
            label = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_NOTAUTOPROLONGATIONLABEL
        else:
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_RENT
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_RENT_HOVER
            label = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_AUTOPROLONGATIONLABEL
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'actionBtnLabel': text_styles.tutorial(label),
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_RENT_CHECKBOX_CHANGE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI}

    def __makeCamoColorRendererVO(self):
        btnsBlockVO = []
        colornum = _DEFAULT_COLORNUM
        for palette in self._currentItem.palettes:
            colornum = max(colornum, sum(((color >> 24) / 255.0 > 0 for color in palette)))

        for idx, palette in enumerate(islice(self._currentItem.palettes, _MAX_PALETTES)):
            texture = _PALETTE_TEXTURE.format(colornum=colornum)
            icon = camoIconTemplate(texture, _PALETTE_WIDTH, _PALETTE_HEIGHT, palette, background=_PALETTE_BACKGROUND)
            btnsBlockVO.append(CustomizationCamoSwatchVO(icon, idx == self._currentComponent.palette)._asdict())

        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_COLORS,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_COLORS_HOVER,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_COLOR_CHANGE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_SCALE_COLOR_RENDERER_UI,
         'btnsBlockVO': btnsBlockVO} if len(btnsBlockVO) == _MAX_PALETTES else None

    def __makeScaleRendererVO(self):
        btnsBlockVO = []
        if self._slotID == GUI_ITEM_TYPE.CAMOUFLAGE:
            selected = self._currentComponent.patternSize
        else:
            selected = self._currentComponent.scaleFactorId - 1
        for idx, scaleSizeLabel in enumerate(SCALE_SIZE):
            btnsBlockVO.append({'paletteIcon': '',
             'label': scaleSizeLabel,
             'selected': selected == idx,
             'value': idx})

        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_SCALE,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_SCALE_HOVER,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_SCALE_CHANGE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_SCALE_COLOR_RENDERER_UI,
         'btnsBlockVO': btnsBlockVO}

    def __makeSetOnOtherSeasonsRendererVO(self):
        icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_ALL_SEASON
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_ALL_SEASON_HOVER
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_APPLYTOALLMAPS
        if self._isItemAppliedToAll:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_SEASONS
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_DEL_ALL_SEASON
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_ICON_DEL_ALL_SEASON_HOVER
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'actionBtnLabel': text_styles.tutorial(actionBtnLabel),
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI}

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            self.hide()
            return
        if self.__ctx.mode == C11nMode.CUSTOM:
            self.hide()
        else:
            self.__update()

    def __onSeasonChanged(self, seasonType):
        self.hide()

    def __onCamouflageColorChanged(self, areaId, regionIdx, paletteIdx):
        self.__update()

    def __onCamouflageScaleChanged(self, areaId, regionIdx, scale):
        self.__update()

    def __onProjectionDecalScaleChanged(self, areaId, regionIdx, scale):
        self.__update()

    def __onItemsInstalled(self, item, slotId, buyLimitReached):
        self.__update()

    def __onItemsRemoved(self):
        self.hide()

    def __onItemsBought(self, purchaseItems, results):
        self.__update()

    def __onItemSold(self, item, count):
        self.__update()
