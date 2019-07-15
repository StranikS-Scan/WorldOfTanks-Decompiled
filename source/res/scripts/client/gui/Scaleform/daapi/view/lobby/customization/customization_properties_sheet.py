# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_properties_sheet.py
from collections import namedtuple
from itertools import islice
from CurrentVehicle import g_currentVehicle
from gui import DialogsInterface
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, PMConfirmationDialogMeta
from gui.Scaleform.daapi.view.lobby.customization.shared import SCALE_SIZE
from gui.Scaleform.daapi.view.meta.CustomizationPropertiesSheetMeta import CustomizationPropertiesSheetMeta
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nTabs
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from gui.shared.gui_items.customization.c11n_items import camoIconTemplate
from skeletons.gui.shared import IItemsCache
from gui import makeHtmlString
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from gui.customization.shared import getAppliedRegionsForCurrentHangarVehicle, getCustomizationTankPartName, C11nId
from gui.shared.gui_items.customization.outfit import Area
from skeletons.gui.shared.utils import IHangarSpace
from constants import CLIENT_COMMAND_SOURCES
CustomizationCamoSwatchVO = namedtuple('CustomizationCamoSwatchVO', 'paletteIcon selected')
_MAX_PALETTES = 3
_PALETTE_TEXTURE = 'gui/maps/vehicles/camouflages/camo_palette_{colornum}.dds'
_DEFAULT_COLORNUM = 1
_PALETTE_BACKGROUND = 'gui/maps/vehicles/camouflages/camo_palettes_back.dds'
_PALETTE_WIDTH = 42
_PALETTE_HEIGHT = 42
_SEASONS_REMOVE_TEXT = {SeasonType.SUMMER: VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_SEASONS_SUMMER,
 SeasonType.WINTER: VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_SEASONS_WINTER,
 SeasonType.DESERT: VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_SEASONS_DESERT,
 SeasonType.SUMMER | SeasonType.WINTER: VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_SEASONS_SUMMER_WINTER,
 SeasonType.SUMMER | SeasonType.DESERT: VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_SEASONS_SUMMER_DESERT,
 SeasonType.WINTER | SeasonType.DESERT: VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_SEASONS_WINTER_DESERT}
_APPLY_TO_OTHER_SEASONS_DIALOG = 'customization/applyProjectionDecalToOtherSeasons'

class CustomizationPropertiesSheet(CustomizationPropertiesSheetMeta):
    itemsCache = dependency.instance(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(CustomizationPropertiesSheet, self).__init__()
        self.__ctx = None
        self._attachedAnchor = C11nId()
        self._visible = False
        self._extraMoney = None
        self._isItemAppliedToAll = False
        self._showSwitchers = False
        self._isNarrowSlot = False
        self.__inscriptionController = None
        self.__changes = [False] * 3
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.CUSTOMIZATION_INSCRIPTION_CONTROLLER:
            self.__inscriptionController = viewPy

    @property
    def visible(self):
        return self._visible

    @property
    def inEditMode(self):
        return self.__inscriptionController is not None and self.__inscriptionController.visible

    @property
    def attachedAnchor(self):
        return self._attachedAnchor

    @property
    def attached(self):
        return self._attachedAnchor.slotType != -1 and self._attachedAnchor.regionIdx != -1 and self._attachedAnchor.areaId != -1

    def registerInscriptionController(self, inscriptionController, inputLines):
        self.__ctx.vehicleAnchorsUpdater.registerInscriptionController(inscriptionController, inputLines)

    def _populate(self):
        super(CustomizationPropertiesSheet, self)._populate()
        self.__ctx = self.service.getCtx()
        self._attachedAnchor = C11nId()
        self._extraMoney = None
        self._isItemAppliedToAll = False
        self.__ctx.onCacheResync += self.__onCacheResync
        self.__ctx.onCustomizationItemInstalled += self.__onItemsInstalled
        self.__ctx.onCustomizationItemsRemoved += self.__onItemsRemoved
        self.__ctx.onCamouflageColorChanged += self.__onCamouflageColorChanged
        self.__ctx.onCamouflageScaleChanged += self.__onCamouflageScaleChanged
        self.__ctx.onProjectionDecalScaleChanged += self.__onProjectionDecalScaleChanged
        self.__ctx.onProjectionDecalMirrored += self.__onProjectionDecalMirrored
        self.__ctx.onCustomizationItemsBought += self.__onItemsBought
        self.__ctx.onCustomizationItemSold += self.__onItemSold
        self.__ctx.onCustomizationTabChanged += self.__onTabChanged
        self.__ctx.onChangeAutoRent += self.__onChangeAutoRent
        self.__ctx.onSelectAnchor += self.__onSelectAnchor
        self.__ctx.onEditModeFinished += self.onEditModeFinished
        self.__ctx.onCarouselRebuild += self.__onCarouselRebuild
        g_currentVehicle.onChanged += self.__onVehicleChanged
        return

    def _dispose(self):
        self.__ctx.onCustomizationItemSold -= self.__onItemSold
        self.__ctx.onCustomizationItemsBought -= self.__onItemsBought
        self.__ctx.onCamouflageScaleChanged -= self.__onCamouflageScaleChanged
        self.__ctx.onCamouflageColorChanged -= self.__onCamouflageColorChanged
        self.__ctx.onProjectionDecalScaleChanged -= self.__onProjectionDecalScaleChanged
        self.__ctx.onProjectionDecalMirrored -= self.__onProjectionDecalMirrored
        self.__ctx.onCustomizationItemsRemoved -= self.__onItemsRemoved
        self.__ctx.onCustomizationItemInstalled -= self.__onItemsInstalled
        self.__ctx.onCacheResync -= self.__onCacheResync
        self.__ctx.onCustomizationTabChanged -= self.__onTabChanged
        self.__ctx.onChangeAutoRent -= self.__onChangeAutoRent
        self.__ctx.onSelectAnchor -= self.__onSelectAnchor
        self.__ctx.onEditModeFinished -= self.onEditModeFinished
        self.__ctx.onCarouselRebuild -= self.__onCarouselRebuild
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self._extraMoney = None
        self._isItemAppliedToAll = False
        self._attachedAnchor = C11nId()
        self.__ctx = None
        self.__inscriptionController = None
        super(CustomizationPropertiesSheet, self)._dispose()
        return

    def onEditModeFinished(self):
        self.__update()

    def locateOnAnchor(self, areaID, slotID, regionID):
        anchor = C11nId(areaID, slotID, regionID)
        if anchor != self._attachedAnchor:
            self.__attachToAnchor(anchor)

    def locateToCustomizationPreview(self):
        anchor = C11nId()
        self.__attachToAnchor(anchor)

    def handleEscBtn(self):
        return self.__inscriptionController.handleEscBtn() if self.__inscriptionController is not None else False

    def handleDelBtn(self):
        if self.__inscriptionController is not None:
            if self.__inscriptionController.handleDelBtn():
                return True
        if self.visible:
            if self.__ctx.currentTab == C11nTabs.STYLE:
                self.__ctx.removeStyle(self.__ctx.modifiedStyle.intCD)
            else:
                self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, self.__ctx.selectedSlot)
            return True
        else:
            return False

    def handleLobbyClick(self):
        return self.__inscriptionController.handleLobbyClick() if self.__inscriptionController is not None else False

    def handleBuyWindow(self):
        if self.__inscriptionController is not None:
            purchaseItems = self.__ctx.getPurchaseItems()
            showProhibitedHint = False
            if len(purchaseItems) == 1:
                item = purchaseItems[0].item
                showProhibitedHint = item is not None and item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER
            self.__inscriptionController.finish(cancelIfEmpty=True, removeProhibited=not showProhibitedHint)
            return self.__inscriptionController.visible
        else:
            return False

    def confirmHeaderNavigation(self):
        if self.__inscriptionController is not None:
            self.__inscriptionController.cancel()
        return

    def show(self):
        if self.__ctx.vehicleAnchorsUpdater is None:
            return
        else:
            self.__ctx.vehicleAnchorsUpdater.attachMenuToAnchor(self._attachedAnchor)
            self._visible = True
            if self.__update():
                self.__ctx.onPropertySheetShown(self._attachedAnchor)
                self.__ctx.vehicleAnchorsUpdater.displayMenu(True)
                self.__updateAnchorSwitchers()
            return

    def hide(self):
        if not self.visible:
            return
        else:
            self._visible = False
            self.as_hideS()
            if self.__inscriptionController is not None:
                self.__inscriptionController.hide()
            self.__ctx.onPropertySheetHidden()
            return

    def elementControlsHide(self):
        self.__ctx.vehicleAnchorsUpdater.displayMenu(False)

    def onActionBtnClick(self, actionType, actionData):
        if actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS:
            self._isItemAppliedToAll = not self._isItemAppliedToAll
            self.__applyToOtherAreas(self._isItemAppliedToAll)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS:
            self.__applyToOtherSeasons()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE:
            self.__removeElement()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_RENT_CHECKBOX_CHANGE:
            self.__ctx.changeAutoRent(CLIENT_COMMAND_SOURCES.RENTED_STYLE_RADIAL_MENU)
            self.__update()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_PARTS:
            self.__removeFromAllAreas()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_SCALE_CHANGE:
            if self._attachedAnchor.slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
                if self._currentComponent.patternSize != actionData:
                    self.__ctx.changeCamouflageScale(self._attachedAnchor.areaId, self._attachedAnchor.regionIdx, actionData)
            elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                actionData += 1
                if self._currentComponent.scaleFactorId != actionData:
                    self.__ctx.changeProjectionDecalScale(self._attachedAnchor.areaId, self._attachedAnchor.regionIdx, actionData)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_COLOR_CHANGE:
            if self._currentComponent.palette != actionData:
                self.__ctx.changeCamouflageColor(self._attachedAnchor.areaId, self._attachedAnchor.regionIdx, actionData)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_CLOSE:
            self.hide()
            self.__ctx.onClearItem()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_MIRROR:
            self.__ctx.mirrorProjectionDecal(self._attachedAnchor.areaId, self._attachedAnchor.regionIdx)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_EDIT:
            self.__ctx.storePersonalNumber(self._currentComponent.number)
            self.__inscriptionController.show(self._attachedAnchor)
            self.__update()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_INFO:
            self.__ctx.onShowStyleInfo()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_GET_BACK:
            currentIntCD = self._currentItem.intCD
            self.__removeElement()
            self.__ctx.onGetItemBackToHand(currentIntCD)

    def onClose(self):
        self.hide()

    @property
    def _currentSlotData(self):
        if not self.attached or self._attachedAnchor.slotType == GUI_ITEM_TYPE.STYLE:
            return
        else:
            container = self.__ctx.currentOutfit.getContainer(self._attachedAnchor.areaId)
            slot = container.slotFor(self._attachedAnchor.slotType)
            if slot is None:
                return
            slotId = self.__ctx.getSlotIdByAnchorId(self._attachedAnchor)
            return slot.getSlotData(slotId.regionIdx) if slotId is not None else None

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
        return self.__ctx.modifiedStyle if self._attachedAnchor.slotType == GUI_ITEM_TYPE.STYLE else None

    def __update(self):
        if self._currentItem is None and self._currentStyle is None:
            self.hide()
            return False
        elif self.visible and self.attached:
            self.__updateInscriptionController()
            self.__updateItemAppliedToAllFlag()
            self.__updateExtraPrice()
            self.as_setDataAndShowS(self.__makeVO())
            self.__ctx.caruselItemUnselected()
            return True
        else:
            return False

    def __attachToAnchor(self, anchor):
        if not g_currentVehicle.isPresent():
            return
        else:
            if self.attached:
                self.__inscriptionController.finish(cancelIfEmpty=True, removeProhibited=True)
            self._attachedAnchor = anchor
            if self._currentItem is not None or self._currentStyle is not None:
                self.show()
            else:
                self.hide()
            return

    def __applyToOtherAreas(self, installItem):
        if self.__ctx.currentTab not in (C11nTabs.PAINT, C11nTabs.CAMOUFLAGE):
            return
        currentSeason = self.__ctx.currentSeason
        if installItem:
            self.__ctx.installItemToAllTankAreas(currentSeason, self._attachedAnchor.slotType, self._currentSlotData)
        else:
            self.__ctx.removeItemFromAllTankAreas(currentSeason, self._attachedAnchor.slotType)
        self.__update()

    def __removeFromAllAreas(self):
        currentSeason = self.__ctx.currentSeason
        self.__ctx.removeItemFromAllTankAreas(currentSeason, self._attachedAnchor.slotType)
        self.__update()

    def __applyToOtherSeasons(self):
        if self.__ctx.currentTab not in (C11nTabs.EFFECT,
         C11nTabs.EMBLEM,
         C11nTabs.INSCRIPTION,
         C11nTabs.PROJECTION_DECAL):
            return
        if not self._isItemAppliedToAll:
            if self.__ctx.currentTab == C11nTabs.PROJECTION_DECAL:
                lockedSeasons = self.__ctx.getLockedProjectionDecalSeasons(self._attachedAnchor.regionIdx)
                if lockedSeasons:
                    self.__showApplyToOtherSeasonsDialog(lockedSeasons)
                    return
            self.__ctx.installItemForAllSeasons(self._attachedAnchor.areaId, self._attachedAnchor.slotType, self._attachedAnchor.regionIdx, self._currentSlotData)
            self._isItemAppliedToAll = True
        else:
            self.__ctx.removeItemForAllSeasons(self._attachedAnchor.areaId, self._attachedAnchor.slotType, self._attachedAnchor.regionIdx)
            self._isItemAppliedToAll = False
        self.__update()

    def __showApplyToOtherSeasonsDialog(self, lockedSeasons):
        removedText = text_styles.alert(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_SEASONS_REMOVED)
        seasonsString = self.__getLockedSeasonsString(lockedSeasons)
        if len(lockedSeasons) == 1:
            dialogMessage = _ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_DIALOG_SEASON)
        else:
            dialogMessage = _ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_DIALOG_SEASONS)
        message = makeHtmlString('html_templates:lobby/customization/dialog', 'decal', {'value': _ms(dialogMessage, season=seasonsString.decode('utf-8').upper(), removed=removedText.decode('utf-8').upper())})
        DialogsInterface.showDialog(PMConfirmationDialogMeta(_APPLY_TO_OTHER_SEASONS_DIALOG, messageCtx={'message': message,
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_90X84}, focusedID=DIALOG_BUTTON_ID.CLOSE), self.__installProjectionDecalToAllSeasonsDialogCallback)

    def __installProjectionDecalToAllSeasonsDialogCallback(self, confirmed):

        def projectionDecalsFilter(item):
            return item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL

        if not confirmed:
            return
        lockedSeasons = self.__ctx.getLockedProjectionDecalSeasons(self._attachedAnchor.regionIdx)
        for season in lockedSeasons:
            outfit = self.__ctx.getModifiedOutfit(season)
            self.__ctx.removeItemsFromOutfit(outfit, projectionDecalsFilter, refresh=False)

        self.__ctx.installItemForAllSeasons(self._attachedAnchor.areaId, self._attachedAnchor.slotType, self._attachedAnchor.regionIdx, self._currentSlotData)
        self._isItemAppliedToAll = True

    def __removeElement(self):
        if self._attachedAnchor.slotType == GUI_ITEM_TYPE.STYLE:
            self.__ctx.removeStyle(self._currentStyle.intCD)
        else:
            slotId = self.__ctx.getSlotIdByAnchorId(self._attachedAnchor)
            if slotId is not None:
                self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, slotId)
        return

    def __updateInscriptionController(self):
        if self.__inscriptionController is None:
            return
        else:
            self.__inscriptionController.update(self._attachedAnchor)
            return

    def __updateAnchorSwitchers(self):
        if not self.visible:
            return
        installPrev, installNext = self.__ctx.getItemSwitchersState()
        self.as_setArrowsStatesS(installPrev, installNext)

    def __updateItemAppliedToAllFlag(self):
        self._isItemAppliedToAll = False
        if self.__ctx.currentTab in (C11nTabs.PAINT, C11nTabs.CAMOUFLAGE):
            self._isItemAppliedToAll = True
            for areaId in Area.TANK_PARTS:
                regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, self._attachedAnchor.slotType)
                multiSlot = self.__ctx.currentOutfit.getContainer(areaId).slotFor(self._attachedAnchor.slotType)
                for regionIdx in regionsIndexes:
                    slotData = multiSlot.getSlotData(regionIdx)
                    df = self._currentSlotData.weakDiff(slotData)
                    if slotData.item is None or df.item is not None:
                        break
                else:
                    continue

                self._isItemAppliedToAll = False
                break

        elif self.__ctx.currentTab in (C11nTabs.EFFECT,
         C11nTabs.EMBLEM,
         C11nTabs.INSCRIPTION,
         C11nTabs.PROJECTION_DECAL):
            self._isItemAppliedToAll = True
            firstSeason = SeasonType.COMMON_SEASONS[0]
            firstSlotId = self.__ctx.getSlotIdByAnchorId(self._attachedAnchor, firstSeason)
            if firstSlotId is None:
                self._isItemAppliedToAll = False
                return
            fistSlotData = self.__ctx.getModifiedOutfit(firstSeason).getContainer(firstSlotId.areaId).slotFor(firstSlotId.slotType).getSlotData(firstSlotId.regionIdx)
            if fistSlotData.item is not None:
                for season in SeasonType.COMMON_SEASONS[1:]:
                    slotId = self.__ctx.getSlotIdByAnchorId(self._attachedAnchor, season)
                    if slotId is None:
                        self._isItemAppliedToAll = False
                        break
                    slotData = self.__ctx.getModifiedOutfit(season).getContainer(slotId.areaId).slotFor(slotId.slotType).getSlotData(slotId.regionIdx)
                    df = fistSlotData.weakDiff(slotData)
                    if slotData.item is None or df.item is not None:
                        self._isItemAppliedToAll = False
                        break

            else:
                self._isItemAppliedToAll = False
        return

    def __makeVO(self):
        isEditMode = self.__inscriptionController.visible
        vo = {'renderersData': self.__makeRenderersVOs() if not isEditMode else [],
         'isBigRadius': self._attachedAnchor.slotType in (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.PROJECTION_DECAL, GUI_ITEM_TYPE.EMBLEM),
         'showSwitchers': self._showSwitchers and not isEditMode,
         'isNarrowSlot': self._isNarrowSlot}
        return vo

    def __makeSlotVO(self):
        vo = None
        if not self._currentItem:
            vo = {'imgIconSrc': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK_POPOVER_SMALL}
        return vo

    def __makeRenderersVOs(self):
        renderers = []
        if self._attachedAnchor.slotType == GUI_ITEM_TYPE.PAINT:
            renderers.append(self.__makeSetOnOtherTankPartsRendererVO())
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
            renderers.append(self.__makeCamoColorRendererVO())
            renderers.append(self.__makeScaleRendererVO())
            renderers.append(self.__makeSetOnOtherTankPartsRendererVO())
        elif self._attachedAnchor.slotType in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.MODIFICATION):
            if self._currentItem.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
                renderers.append(self.__makeEditInscriptionRendererVO())
            renderers.append(self.__makeSetOnOtherSeasonsRendererVO())
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.STYLE:
            renderers.append(self.__makeStyleInfoRendererVO())
            isExtentionEnabled = self._currentStyle is not None and self._currentStyle.isRentable
            if isExtentionEnabled:
                renderers.append(self.__makeExtensionRendererVO())
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            renderers.append(self.__makeMirorRendererVO())
            renderers.append(self.__makeScaleRendererVO())
            renderers.append(self.__makeGetBackRendererVO())
            renderers.append(self.__makeSetOnOtherSeasonsRendererVO())
        renderers.append(self.__makeRemoveRendererVO())
        renderers.append(self.__makeCloseeRendererVO())
        return renderers

    def __updateExtraPrice(self):
        if self._isItemAppliedToAll and self._currentItem:
            appliedIems = tuple((it for it in self.__ctx.getPurchaseItems() if not it.isDismantling and it.item.intCD == self._currentItem.intCD))
            if self.__ctx.currentTab in (C11nTabs.PAINT, C11nTabs.CAMOUFLAGE):
                appliedIems = tuple((it for it in appliedIems if it.group == self.__ctx.currentSeason))
            outfit = self.__ctx.originalOutfit
            slotData = outfit.getContainer(self._attachedAnchor.areaId).slotFor(self._attachedAnchor.slotType).getSlotData(self._attachedAnchor.regionIdx)
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
        icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_FULL_TANK
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_FULL_TANK_HOVER
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_APPLYTOWHOLETANK
        disableTooltip = _ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_APPLYTOWHOLETANKDISABLED, itemType=_ms('#vehicle_customization:propertySheet/actionBtn/forCurrentItem/' + self._currentItem.itemTypeName))
        enabled = True
        if self._isItemAppliedToAll:
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_ICON_DEL_TANK
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_ICON_DEL_TANK_HOVER
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_CANCEL
        else:
            enabled = self.__ctx.isPossibleToInstallToAllTankAreas(self.__ctx.currentSeason, self._attachedAnchor.slotType, self._currentSlotData)
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_FULL_TANK_DISABLE,
         'actionBtnLabel': actionBtnLabel,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'animatedTransition': True,
         'disableTooltip': disableTooltip,
         'enabled': enabled}

    def __makeMirorRendererVO(self):
        if self._attachedAnchor.slotType not in (GUI_ITEM_TYPE.PROJECTION_DECAL,):
            return {'iconSrc': '',
             'iconHoverSrc': '',
             'iconDisableSrc': '',
             'actionBtnLabel': '',
             'actionType': '',
             'rendererLnk': '',
             'enabled': False}
        isMirrorOn = self._currentItem.canBeMirrored
        alreadyMirrored = self._currentComponent.isMirrored()
        icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_MIRROR_01_NORMAL
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_MIRROR_01_HOVER
        if alreadyMirrored:
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_MIRROR_02_NORMAL
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_MIRROR_02_HOVER
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_MIRROR
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_MIRROR_01_DISABLED,
         'actionBtnLabel': actionBtnLabel,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_MIRROR,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'disableTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_PROPERTYSHEET_DISABLED_MIRROR,
         'enabled': isMirrorOn}

    def __makeGetBackRendererVO(self):
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_GETBACK
        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MOVE_NORMAL,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MOVE_HOVER,
         'actionBtnLabel': actionBtnLabel,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_GET_BACK,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'enabled': True}

    def __makeRemoveRendererVO(self):
        if self._attachedAnchor.slotType == GUI_ITEM_TYPE.MODIFICATION:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_MODIFICATION
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.EMBLEM:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_EMBLEM
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.INSCRIPTION:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_INSCRIPTION
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_PROJECTIONDECAL
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.STYLE:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVESTYLE
        else:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.getSheetBtnRemoveText(getCustomizationTankPartName(self._attachedAnchor.areaId, self._attachedAnchor.regionIdx))
        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_DEL,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_DEL_HOVER,
         'actionBtnLabel': actionBtnLabel,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE,
         'animatedTransition': True,
         'enabled': True}

    def __makeCloseeRendererVO(self):
        iconSrc = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_CLOSE
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_CLOSE_HOVER
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_CLOSE
        return {'iconSrc': iconSrc,
         'iconHoverSrc': hoverIcon,
         'actionBtnLabel': actionBtnLabel,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_CLOSE,
         'enabled': True}

    def __makeStyleInfoRendererVO(self):
        enabled = self._currentStyle is not None and bool(self._currentStyle.longDescriptionSpecial)
        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_INFO,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_INFO_HOVER,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_INFO_DISABLE,
         'actionBtnLabel': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_INFO,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_INFO,
         'disableTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_PROPERTYSHEET_DISABLED_STYLEINFO,
         'enabled': enabled}

    def __makeExtensionRendererVO(self):
        if self.__ctx.autoRentEnabled():
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_ICON_DEL_RENT
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_ICON_DEL_RENT_HOVER
            label = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_NOTAUTOPROLONGATIONLABEL
        else:
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_RENTAL
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_RENTAL_HOVER
            label = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_AUTOPROLONGATIONLABEL
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_RENTAL_DISABLE,
         'actionBtnLabel': label,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_RENT_CHECKBOX_CHANGE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'animatedTransition': True,
         'enabled': True}

    def __makeCamoColorRendererVO(self):
        btnsBlockVO = []
        colornum = _DEFAULT_COLORNUM
        for palette in self._currentItem.palettes:
            colornum = max(colornum, sum(((color >> 24) / 255.0 > 0 for color in palette)))

        for idx, palette in enumerate(islice(self._currentItem.palettes, _MAX_PALETTES)):
            texture = _PALETTE_TEXTURE.format(colornum=colornum)
            icon = camoIconTemplate(texture, _PALETTE_WIDTH, _PALETTE_HEIGHT, palette, background=_PALETTE_BACKGROUND)
            btnsBlockVO.append(CustomizationCamoSwatchVO(icon, idx == self._currentComponent.palette)._asdict())

        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_PALETTE,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_PALETTE_HOVER,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_PALETTE_DISABLE,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_COLOR_CHANGE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_SCALE_COLOR_RENDERER_UI,
         'btnsBlockVO': btnsBlockVO,
         'disableTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_PROPERTYSHEET_DISABLED_COLOR,
         'enabled': len(btnsBlockVO) == _MAX_PALETTES}

    def __makeScaleRendererVO(self):
        btnsBlockVO = []
        if self._attachedAnchor.slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
            selected = self._currentComponent.patternSize
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            selected = self._currentComponent.scaleFactorId - 1
        else:
            return {'iconSrc': '',
             'iconHoverSrc': '',
             'iconDisableSrc': '',
             'actionType': '',
             'rendererLnk': '',
             'btnsBlockVO': '',
             'enabled': False}
        for idx, scaleSizeLabel in enumerate(SCALE_SIZE):
            btnsBlockVO.append({'paletteIcon': '',
             'label': scaleSizeLabel,
             'selected': selected == idx,
             'value': idx})

        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_SCALE,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_SCALE_HOVER,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_SCALE_DISABLE,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_SCALE_CHANGE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_SCALE_COLOR_RENDERER_UI,
         'btnsBlockVO': btnsBlockVO,
         'enabled': True}

    def __makeSetOnOtherSeasonsRendererVO(self):
        icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_SEASON
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_SEASON_HOVER
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_APPLYTOALLMAPS
        notifyString = ''
        enabled = True
        needNotify = False
        disableTooltip = _ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_APPLYTOALLMAPSDISABLED, itemType=_ms('#vehicle_customization:propertySheet/actionBtn/forCurrentItem/' + self._currentItem.itemTypeName))
        if self._isItemAppliedToAll:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_SEASONS
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_ICON_DEL_ALL_SEASON
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_ICON_SEASON_X_HOVER
        else:
            enabled = self.__ctx.isPossibleToInstallItemForAllSeasons(self._attachedAnchor.areaId, self._attachedAnchor.slotType, self._attachedAnchor.regionIdx, self._currentSlotData)
        if self._attachedAnchor.slotType == GUI_ITEM_TYPE.MODIFICATION:
            disableTooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_PROPERTYSHEET_DISABLED_SEASONEFFECT
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.EMBLEM:
            disableTooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_PROPERTYSHEET_DISABLED_SEASONEMBLEM
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.INSCRIPTION:
            disableTooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_PROPERTYSHEET_DISABLED_SEASONINSCRIPTION
        elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            disableTooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_PROPERTYSHEET_DISABLED_SEASONDECAL
            lockedSeasons = self.__ctx.getLockedProjectionDecalSeasons(self._attachedAnchor.regionIdx)
            if lockedSeasons:
                needNotify = True
                notifyString = self.__makeProjectionDecalInstallToOtherSeasonsNotifyString(lockedSeasons)
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_SEASON_DISABLE,
         'actionBtnLabel': actionBtnLabel,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'animatedTransition': True,
         'disableTooltip': disableTooltip,
         'notifyText': notifyString,
         'needNotify': needNotify,
         'enabled': enabled}

    def __makeProjectionDecalInstallToOtherSeasonsNotifyString(self, lockedSeasons):
        removedText = text_styles.alert(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_SEASONS_REMOVED)
        seasonsText = self.__getLockedSeasonsString(lockedSeasons)
        if len(lockedSeasons) == 1:
            tooltipText = _ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_TOOLTIP_SEASON)
        else:
            tooltipText = _ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_NOTIFY_DECAL_TOOLTIP_SEASONS)
        notifyString = makeHtmlString('html_templates:lobby/customization/notify', 'decal', {'value': _ms(tooltipText, season=seasonsText, removed=removedText)})
        return notifyString

    def __getLockedSeasonsString(self, lockedSeasons):
        seasonsMask = SeasonType.UNDEFINED
        for season in lockedSeasons:
            seasonsMask |= season

        seasonsString = text_styles.alert(_SEASONS_REMOVE_TEXT.get(seasonsMask, ''))
        return seasonsString

    def __makeEditInscriptionRendererVO(self):
        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_EDIT,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_EDIT_HOVER,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_EDIT_DISABLE,
         'actionBtnLabel': VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_EDIT_INSCRIPTION,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_EDIT,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'animatedTransition': True,
         'enabled': True}

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            self.hide()
            return
        self.__update()

    def __onCamouflageColorChanged(self, areaId, regionIdx, paletteIdx):
        self.__update()

    def __onCamouflageScaleChanged(self, areaId, regionIdx, scale):
        self.__update()

    def __onProjectionDecalScaleChanged(self, areaId, regionIdx, scale):
        self.__update()

    def __onProjectionDecalMirrored(self, areaId, regionIdx):
        self.__update()

    def __onItemsInstalled(self, item, component, slotId, limitReached):
        if self._currentItem is not None or self._currentStyle is not None:
            if not self.visible:
                self.show()
            else:
                self.__update()
                self.__updateAnchorSwitchers()
        return

    def __onItemsRemoved(self):
        if self._currentItem is None and self._currentStyle is None:
            self.hide()
        else:
            self.__update()
        return

    def __onItemsBought(self, purchaseItems, results):
        self.__update()

    def __onItemSold(self, item, count):
        self.__update()

    def __onTabChanged(self, tabIndex):
        self._showSwitchers = tabIndex not in C11nTabs.REGIONS
        self._isNarrowSlot = tabIndex == C11nTabs.EMBLEM

    def __onChangeAutoRent(self):
        self.__update()

    def __onSelectAnchor(self, areaId, slotType, regionIdx):
        if self.attached and self._attachedAnchor != C11nId(areaId, slotType, regionIdx):
            if self.__inscriptionController is not None:
                self.__inscriptionController.finish(cancelIfEmpty=True, removeProhibited=True)
        return

    def __onCarouselRebuild(self):
        self.__updateAnchorSwitchers()

    def __onVehicleChanged(self):
        self.hide()
