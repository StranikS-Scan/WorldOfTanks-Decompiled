# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_properties_sheet.py
from collections import namedtuple
from itertools import islice
import logging
from CurrentVehicle import g_currentVehicle
from async import await, async
from constants import CLIENT_COMMAND_SOURCES
from frameworks.wulf import WindowLayer
from gui import makeHtmlString
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs, isSlotLocked
from gui.Scaleform.daapi.view.lobby.customization.shared import SCALE_SIZE
from gui.Scaleform.daapi.view.meta.CustomizationPropertiesSheetMeta import CustomizationPropertiesSheetMeta
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization.constants import CustomizationModes, CustomizationModeSource
from gui.customization.shared import getAvailableRegions, C11nId, getCustomizationTankPartName, EDITABLE_STYLE_IRREMOVABLE_TYPES, getAncestors
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import WarningDialogBuilder
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel as FmtArgs
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.c11n_items import camoIconTemplate
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType, Options, EDITING_STYLE_REASONS
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_outfit.outfit import Area
_logger = logging.getLogger(__name__)
CustomizationCamoSwatchVO = namedtuple('CustomizationCamoSwatchVO', 'paletteIcon selected')
_MAX_PALETTES = 3
_MIN_PROGRESSION_LEVEL = 1
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
_PROGRESSION_LEVEL_ICONS = (RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_I_NORMAL,
 RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_II_NORMAL,
 RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_III_NORMAL,
 RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_IV_NORMAL,
 RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_V_NORMAL)
_PROGRESSION_LEVEL_ICONS_HOVER = (RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_I_HOVER,
 RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_II_HOVER,
 RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_III_HOVER,
 RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_IV_HOVER,
 RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_V_HOVER)
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
        self._isItemAppliedToAll = False
        self._showSwitchers = False
        self._isNarrowSlot = False
        self.__inscriptionController = None
        self.__displayedProgressionLevel = 0
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
        self._isItemAppliedToAll = False
        self.__ctx.events.onCacheResync += self.__onCacheResync
        self.__ctx.events.onItemInstalled += self.__onItemsInstalled
        self.__ctx.events.onItemsRemoved += self.__onItemsRemoved
        self.__ctx.events.onComponentChanged += self.__onComponentChanged
        self.__ctx.events.onItemsBought += self.__onItemsBought
        self.__ctx.events.onItemSold += self.__onItemSold
        self.__ctx.events.onTabChanged += self.__onTabChanged
        self.__ctx.events.onSlotSelected += self.__onSlotSelected
        self.__ctx.events.onEditModeEnabled += self.__onEditModeEnabled
        self.__ctx.events.onUpdateSwitchers += self.__onUpdateSwitchers
        g_currentVehicle.onChanged += self.__onVehicleChanged

    def _dispose(self):
        self.__ctx.events.onItemSold -= self.__onItemSold
        self.__ctx.events.onItemsBought -= self.__onItemsBought
        self.__ctx.events.onComponentChanged -= self.__onComponentChanged
        self.__ctx.events.onItemsRemoved -= self.__onItemsRemoved
        self.__ctx.events.onItemInstalled -= self.__onItemsInstalled
        self.__ctx.events.onCacheResync -= self.__onCacheResync
        self.__ctx.events.onTabChanged -= self.__onTabChanged
        self.__ctx.events.onSlotSelected -= self.__onSlotSelected
        self.__ctx.events.onEditModeEnabled -= self.__onEditModeEnabled
        self.__ctx.events.onUpdateSwitchers -= self.__onUpdateSwitchers
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self._isItemAppliedToAll = False
        self._attachedAnchor = C11nId()
        self.__ctx = None
        self.__inscriptionController = None
        super(CustomizationPropertiesSheet, self)._dispose()
        return

    def locateOnAnchor(self, slotId):
        if slotId != self._attachedAnchor:
            self.__attachToAnchor(slotId)

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
            self.__ctx.mode.removeItem(self.__ctx.mode.selectedSlot)
            return True
        else:
            return False

    def handleLobbyClick(self):
        return self.__inscriptionController.handleLobbyClick() if self.__inscriptionController is not None else False

    def handleBuyWindow(self):
        if self.__inscriptionController is not None:
            purchaseItems = self.__ctx.mode.getPurchaseItems()
            showProhibitedHint = False
            if len(purchaseItems) == 1:
                item = purchaseItems[0].item
                showProhibitedHint = item is not None and item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER
            if showProhibitedHint:
                self.__inscriptionController.finish()
            else:
                self.__inscriptionController.stop()
            return self.__inscriptionController.visible
        else:
            return False

    def show(self):
        if self.__ctx.vehicleAnchorsUpdater is None:
            return
        else:
            self.__ctx.vehicleAnchorsUpdater.attachMenuToAnchor(self._attachedAnchor)
            self._visible = True
            if self.__update():
                self.__ctx.events.onPropertySheetShown(self._attachedAnchor)
                self.__ctx.vehicleAnchorsUpdater.displayMenu(True)
            return

    def hide(self):
        if not self.visible:
            return
        else:
            self._visible = False
            self.as_hideS()
            if self.__inscriptionController is not None:
                self.__inscriptionController.stop()
            self.__ctx.events.onPropertySheetHidden()
            return

    def elementControlsHide(self):
        self.__ctx.vehicleAnchorsUpdater.displayMenu(False)

    def onActionBtnClick(self, actionType, actionData):
        if self._attachedAnchor == C11nId():
            return
        if actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS:
            self._isItemAppliedToAll = not self._isItemAppliedToAll
            self.__applyToOtherAreas(self._isItemAppliedToAll)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS:
            self.__applyToOtherSeasons()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE:
            self.__removeElement()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_RENT_CHECKBOX_CHANGE:
            self.__ctx.mode.changeAutoRent(CLIENT_COMMAND_SOURCES.RENTED_STYLE_RADIAL_MENU)
            self.__update()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_PARTS:
            self.__removeFromAllAreas()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_SCALE_CHANGE:
            if self._attachedAnchor.slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
                self.__ctx.mode.changeCamouflageScale(self._attachedAnchor, actionData)
            elif self._attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                actionData += 1
                self.__ctx.mode.changeProjectionDecalScale(self._attachedAnchor, actionData)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_COLOR_CHANGE:
            self.__ctx.mode.changeCamouflageColor(self._attachedAnchor, actionData)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_CLOSE:
            self.__ctx.mode.unselectSlot()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_HORIZONZONTAL_MIRROR:
            self.__ctx.mode.mirrorDecal(self._attachedAnchor, Options.MIRRORED_HORIZONTALLY)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_VERTICAL_MIRROR:
            self.__ctx.mode.mirrorDecal(self._attachedAnchor, Options.MIRRORED_VERTICALLY)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_EDIT:
            self.__inscriptionController.start(self._attachedAnchor)
            self.__update()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_INFO:
            self.__ctx.events.onShowStyleInfo()
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_GET_BACK:
            item = self._currentItem
            progressionLevel = item.getUsedProgressionLevel(self._currentComponent)
            self.__removeElement()
            self.__ctx.events.onGetItemBackToHand(item, progressionLevel)
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_SWITCH_PROGRESSION_LVL:
            currentProgressionLevel = self._currentItem.getLatestOpenedProgressionLevel(g_currentVehicle.item)
            if actionData == 0:
                self.__displayedProgressionLevel = self.__displayedProgressionLevel % currentProgressionLevel + 1
            elif actionData == 1:
                self.__displayedProgressionLevel -= 1
                self.__displayedProgressionLevel = self.__displayedProgressionLevel % currentProgressionLevel
            progression = self.__displayedProgressionLevel
            if self.__displayedProgressionLevel == currentProgressionLevel:
                progression = 0
            self.__ctx.mode.changeItemProgression(self._attachedAnchor, progression)
            self.as_setDataAndShowS(self.__makeVO())
        elif actionType == CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_EDIT_STYLE:
            self.__ctx.editStyle(self._currentStyle.intCD, source=CustomizationModeSource.PROPERTIES_SHEET)

    def onClose(self):
        self.hide()

    @property
    def _currentSlotData(self):
        if not self.attached or self._attachedAnchor.slotType == GUI_ITEM_TYPE.STYLE:
            return
        outfit = self.__ctx.mode.currentOutfit
        container = outfit.getContainer(self._attachedAnchor.areaId)
        slot = container.slotFor(self._attachedAnchor.slotType)
        if slot is None:
            return
        else:
            return slot.getSlotData(self._attachedAnchor.regionIdx) if self._attachedAnchor.regionIdx != -1 else None

    @property
    def _currentItem(self):
        slotData = self._currentSlotData
        if slotData is None or not slotData.intCD:
            return
        else:
            item = self.service.getItemByCD(slotData.intCD)
            return item

    @property
    def _currentComponent(self):
        slotData = self._currentSlotData
        return None if slotData is None else slotData.component

    @property
    def _currentStyle(self):
        return self.__ctx.mode.modifiedStyle if self._attachedAnchor.slotType == GUI_ITEM_TYPE.STYLE else None

    def __update(self):
        if self._currentItem is None and self._currentStyle is None:
            self.hide()
            return False
        elif self.visible and self.attached:
            self.__updateInscriptionController()
            self.__updateItemAppliedToAllFlag()
            self.__updateProgressionLevel()
            self.as_setDataAndShowS(self.__makeVO())
            return True
        else:
            return False

    def __attachToAnchor(self, anchor):
        if not g_currentVehicle.isPresent():
            return
        else:
            if self.attached:
                if self.__inscriptionController.visible:
                    self.__inscriptionController.stop()
            self._attachedAnchor = anchor
            if self._currentItem is not None or self._currentStyle is not None:
                self.show()
            else:
                self.hide()
            return

    def __applyToOtherAreas(self, installItem):
        if self.__ctx.mode.tabId not in (CustomizationTabs.PAINTS, CustomizationTabs.CAMOUFLAGES):
            return
        if installItem:
            self.__ctx.mode.installItemToAllTankAreas(self.__ctx.season, self._attachedAnchor.slotType, self._currentSlotData)
        else:
            self.__ctx.mode.removeItemFromAllTankAreas(self.__ctx.season, self._attachedAnchor.slotType)
        self.__update()

    def __removeFromAllAreas(self):
        self.__ctx.mode.removeItemFromAllTankAreas(self.__ctx.season, self._attachedAnchor.slotType)
        self.__update()

    def __applyToOtherSeasons(self):
        if not self._isItemAppliedToAll:
            if self.__ctx.mode.tabId == CustomizationTabs.PROJECTION_DECALS:
                lockedSeasons = []
                for season in SeasonType.COMMON_SEASONS:
                    outfit = self.__ctx.mode.getModifiedOutfit(season)
                    if isSlotLocked(outfit, self._attachedAnchor):
                        lockedSeasons.append(season)

                if lockedSeasons:
                    self.__showApplyToOtherSeasonsDialog(lockedSeasons)
                    return
            self.__ctx.mode.installItemToAllSeasons(self._attachedAnchor, self._currentSlotData)
            self._isItemAppliedToAll = True
        else:
            self.__ctx.mode.removeItemFromAllSeasons(self._attachedAnchor)
            self._isItemAppliedToAll = False
        self.__update()

    @async
    def __showApplyToOtherSeasonsDialog(self, lockedSeasons):
        seasonMask = reduce(int.__or__, lockedSeasons, SeasonType.UNDEFINED)
        season = _ms(_SEASONS_REMOVE_TEXT.get(seasonMask, '')).decode('utf-8').upper()
        removed = backport.text(R.strings.vehicle_customization.propertySheet.notify.decal.seasons.removed())
        removed = removed.decode('utf-8').upper()
        message = R.strings.dialogs.customization.applyProjectionDecalToOtherSeasons
        this = backport.text(message.this() if len(lockedSeasons) == 1 else message.these())
        builder = WarningDialogBuilder()
        builder.setMessageArgs(fmtArgs=[FmtArgs(season, 'season', R.styles.AlertTextStyle()), FmtArgs(removed, 'removed', R.styles.AlertTextStyle()), FmtArgs(this, 'this')])
        builder.setMessagesAndButtons(message, focused=DialogButtons.CANCEL)
        subview = self.app.containerManager.getContainer(WindowLayer.SUB_VIEW).getView()
        result = yield await(dialogs.showSimple(builder.build(parent=subview)))
        self.__installProjectionDecalToAllSeasonsDialogCallback(result)

    def __installProjectionDecalToAllSeasonsDialogCallback(self, confirmed):

        def projectionDecalsFilter(item):
            return item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL

        if not confirmed:
            return
        for season in SeasonType.COMMON_SEASONS:
            outfit = self.__ctx.mode.getModifiedOutfit(season)
            if isSlotLocked(outfit, self._attachedAnchor):
                self.__ctx.mode.removeItemsFromSeason(season, projectionDecalsFilter, refresh=False)

        self.__ctx.mode.installItemToAllSeasons(self._attachedAnchor, self._currentSlotData)
        self._isItemAppliedToAll = True

    def __removeElement(self):
        self.__ctx.mode.removeItem(self._attachedAnchor)
        self.__ctx.mode.unselectSlot()

    def __updateInscriptionController(self):
        if self.__inscriptionController is None:
            return
        else:
            self.__inscriptionController.update(self._attachedAnchor)
            return

    def __updateItemAppliedToAllFlag(self):
        if self.__ctx.mode.tabId in (CustomizationTabs.PAINTS, CustomizationTabs.CAMOUFLAGES):
            if self.__isEditableStyle():
                self._isItemAppliedToAll = self.__isItemAppliedToAllSeasons()
            else:
                self._isItemAppliedToAll = self.__isItemAppliedToAllRegions()
        elif self.__ctx.mode.tabId in (CustomizationTabs.MODIFICATIONS,
         CustomizationTabs.EMBLEMS,
         CustomizationTabs.INSCRIPTIONS,
         CustomizationTabs.PROJECTION_DECALS):
            self._isItemAppliedToAll = self.__isItemAppliedToAllSeasons()
        else:
            self._isItemAppliedToAll = False

    def __isItemAppliedToAllSeasons(self):
        slotData = self.__ctx.mode.getSlotDataFromSlot(self._attachedAnchor)
        if not slotData.intCD:
            return False
        for season in SeasonType.COMMON_SEASONS:
            if season == self.__ctx.season:
                continue
            otherSlotData = self.__ctx.mode.getSlotDataFromSlot(self._attachedAnchor, season)
            df = otherSlotData.weakDiff(slotData)
            if not slotData.intCD or df.intCD:
                return False

        return True

    def __isItemAppliedToAllRegions(self):
        for areaId in Area.TANK_PARTS:
            regionsIndexes = getAvailableRegions(areaId, self._attachedAnchor.slotType)
            outfit = self.__ctx.mode.currentOutfit
            multiSlot = outfit.getContainer(areaId).slotFor(self._attachedAnchor.slotType)
            for regionIdx in regionsIndexes:
                slotData = multiSlot.getSlotData(regionIdx)
                df = self._currentSlotData.weakDiff(slotData)
                if not slotData.intCD or df.intCD:
                    return False

        return True

    def __updateProgressionLevel(self):
        if self._currentItem is not None and self._currentItem.isProgressive:
            currentProgressionLevel = self._currentItem.getLatestOpenedProgressionLevel(g_currentVehicle.item)
            if self._currentComponent and self._currentComponent.progressionLevel > 0:
                self.__displayedProgressionLevel = self._currentComponent.progressionLevel
            else:
                self.__displayedProgressionLevel = currentProgressionLevel
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
        slotType = self._attachedAnchor.slotType
        if slotType == GUI_ITEM_TYPE.PAINT:
            renderers = self.__makePaintRenderersVOs()
        elif slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
            renderers = self.__makeCamouflageRenderersVOs()
        elif slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            renderers = self.__makeProjectionDecalRenderersVOs()
        elif slotType in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.PERSONAL_NUMBER):
            renderers = self.__makeDecalRenderersVOs()
        elif slotType == GUI_ITEM_TYPE.MODIFICATION:
            renderers = self.__makeModificationsRenderersVOs()
        elif slotType == GUI_ITEM_TYPE.STYLE:
            renderers = self.__makeStyleRenderersVOs()
        else:
            _logger.error('Cannot get customization properties sheet renderers for slotType: %s', slotType)
            renderers = []
        renderers.append(self.__makeRemoveRendererVO())
        renderers.append(self.__makeCloseRendererVO())
        return renderers

    def __makePaintRenderersVOs(self):
        renderers = []
        if self.__isCustomMode():
            renderers.append(self.__makeSetOnOtherTankPartsRendererVO())
        else:
            renderers.append(self.__makeSetOnOtherSeasonsRendererVO())
        return renderers

    def __makeCamouflageRenderersVOs(self):
        renderers = []
        renderers.append(self.__makeCamoColorRendererVO())
        renderers.append(self.__makeScaleRendererVO())
        if self.__isCustomMode():
            renderers.append(self.__makeSetOnOtherTankPartsRendererVO())
        else:
            renderers.append(self.__makeSetOnOtherSeasonsRendererVO())
        return renderers

    def __makeProjectionDecalRenderersVOs(self):
        renderers = []
        renderers.append(self.__makeMirrorRendererVO())
        renderers.append(self.__makeScaleRendererVO())
        if self._currentItem.isProgressive:
            renderers.append(self.__makeSwitchProgressionLevelRendererVO())
        renderers.append(self.__makeGetBackRendererVO())
        renderers.append(self.__makeSetOnOtherSeasonsRendererVO())
        return renderers

    def __makeDecalRenderersVOs(self):
        renderers = []
        if self._currentItem.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
            renderers.append(self.__makeEditInscriptionRendererVO())
        renderers.append(self.__makeSetOnOtherSeasonsRendererVO())
        return renderers

    def __makeModificationsRenderersVOs(self):
        return [self.__makeSetOnOtherSeasonsRendererVO()]

    def __makeStyleRenderersVOs(self):
        renderers = []
        isRentable = self._currentStyle is not None and self._currentStyle.isRentable
        isEditable = self._currentStyle is not None and self._currentStyle.isEditable
        renderers.append(self.__makeStyleInfoRendererVO())
        if isRentable:
            renderers.append(self.__makeRentSelectorRendererVO())
        if isEditable:
            renderers.append(self.__makeEditStyleRendererVO())
        return renderers

    def __makeSetOnOtherTankPartsRendererVO(self):
        icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_FULL_TANK
        hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_FULL_TANK_HOVER
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_APPLYTOWHOLETANK
        forCurrentItemText = R.strings.vehicle_customization.propertySheet.actionBtn.forCurrentItem.dyn(self._currentItem.itemTypeName)
        forCurrentItemText = backport.text(forCurrentItemText()) if forCurrentItemText.exists() else ''
        disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.applyToWholeTankDisabled(), itemType=forCurrentItemText)
        enabled = True
        if self._isItemAppliedToAll:
            icon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_ICON_DEL_TANK
            hoverIcon = RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_ICON_DEL_TANK_HOVER
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_CANCEL
        else:
            enabled = self.__ctx.mode.isPossibleToInstallToAllTankAreas(self._currentSlotData.intCD, self._attachedAnchor.slotType)
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_FULL_TANK_DISABLE,
         'actionBtnLabel': actionBtnLabel,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'animatedTransition': True,
         'disableTooltip': disableTooltip,
         'enabled': enabled}

    def __makeMirrorRendererVO(self):
        if self._attachedAnchor.slotType not in (GUI_ITEM_TYPE.PROJECTION_DECAL,):
            return {'iconSrc': '',
             'iconHoverSrc': '',
             'iconDisableSrc': '',
             'actionBtnLabel': '',
             'actionType': '',
             'rendererLnk': '',
             'enabled': False}
        horizontalMirror = [{'icon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_MIRROR_02_NORMAL,
          'hoverIcon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_MIRROR_02_HOVER}, {'icon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_MIRROR_01_NORMAL,
          'hoverIcon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_ICON_MIRROR_01_HOVER}]
        verticalMirror = [{'icon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_UP_NORMAL,
          'hoverIcon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_UP_HOVER}, {'icon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_DOWN_NORMAL,
          'hoverIcon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_DOWN_HOVER}]
        comboMirror = [{'icon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_LEFT_UP_NORMAL,
          'hoverIcon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_LEFT_UP_HOVER},
         {'icon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_RIGHT_UP_NORMAL,
          'hoverIcon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_RIGHT_UP_HOVER},
         {'icon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_LEFT_DOWN_NORMAL,
          'hoverIcon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_LEFT_DOWN_HOVER},
         {'icon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_RIGHT_DOWN_NORMAL,
          'hoverIcon': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MIRROR_RIGHT_DOWN_HOVER}]
        slotId = self._attachedAnchor
        slot = g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
        canBeMirroredHorizontally = self._currentItem.canBeMirroredHorizontally
        canBeMirroredVertically = self._currentItem.canBeMirroredVertically and slot.canBeMirroredVertically
        isMirroredHorizontally = self._currentComponent.isMirroredHorizontally()
        isMirroredVertically = self._currentComponent.isMirroredVertically()
        if canBeMirroredHorizontally and canBeMirroredVertically:
            mirrorStates = comboMirror
            currentMirrorState = isMirroredVertically | isMirroredHorizontally
            if currentMirrorState ^ Options.NONE and currentMirrorState ^ Options.COMBO_MIRRORED:
                actionType = CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_HORIZONZONTAL_MIRROR
            else:
                actionType = CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_VERTICAL_MIRROR
        elif canBeMirroredVertically:
            mirrorStates = verticalMirror
            actionType = CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_VERTICAL_MIRROR
            currentMirrorState = bool(isMirroredVertically)
        else:
            mirrorStates = horizontalMirror
            actionType = CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_HORIZONZONTAL_MIRROR
            currentMirrorState = isMirroredHorizontally
        icon = mirrorStates[currentMirrorState]['icon']
        hoverIcon = mirrorStates[currentMirrorState]['hoverIcon']
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_MIRROR
        enabled = canBeMirroredHorizontally or canBeMirroredVertically
        return {'iconSrc': icon,
         'iconHoverSrc': hoverIcon,
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_ICON_MIRROR_01_DISABLED,
         'actionBtnLabel': actionBtnLabel,
         'actionType': actionType,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'disableTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_PROPERTYSHEET_DISABLED_MIRROR,
         'enabled': enabled}

    def __makeGetBackRendererVO(self):
        actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_GETBACK
        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MOVE_NORMAL,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_IDLE_MOVE_HOVER,
         'actionBtnLabel': actionBtnLabel,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_GET_BACK,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'enabled': True}

    def __makeRemoveRendererVO(self):
        slotType = self._attachedAnchor.slotType
        isEditableStyle = self.__isEditableStyle()
        if slotType == GUI_ITEM_TYPE.MODIFICATION:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_MODIFICATION
        elif slotType == GUI_ITEM_TYPE.EMBLEM:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_EMBLEM
        elif slotType == GUI_ITEM_TYPE.INSCRIPTION:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_INSCRIPTION
        elif slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_PROJECTIONDECAL
        elif slotType == GUI_ITEM_TYPE.STYLE:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVESTYLE
        elif slotType == GUI_ITEM_TYPE.PAINT and isEditableStyle:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_PAINT
        elif slotType == GUI_ITEM_TYPE.CAMOUFLAGE and isEditableStyle:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_REMOVE_CAMOUFLAGE
        else:
            actionBtnLabel = VEHICLE_CUSTOMIZATION.getSheetBtnRemoveText(getCustomizationTankPartName(self._attachedAnchor.areaId, self._attachedAnchor.regionIdx))
        disableIcon = backport.image(R.images.gui.maps.icons.customization.property_sheet.disable.icon_remove_disable())
        item = self._currentItem if self._currentItem is not None else self._currentStyle
        forCurrentItemText = R.strings.vehicle_customization.propertySheet.actionBtn.forCurrentItem.dyn(item.itemTypeName)
        forCurrentItemText = backport.text(forCurrentItemText()) if forCurrentItemText.exists() else ''
        disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.removeDisabled(), itemType=forCurrentItemText)
        if isEditableStyle and item.itemTypeID in EDITABLE_STYLE_IRREMOVABLE_TYPES:
            if self.__ctx.mode.getDependenciesData() and item.itemTypeID != GUI_ITEM_TYPE.CAMOUFLAGE:
                enabled = False
            else:
                enabled = not self.__ctx.mode.isBaseItem(self._attachedAnchor)
        else:
            enabled = True
        return {'iconSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_DEL,
         'iconHoverSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_REMOVE_DEL_HOVER,
         'iconDisableSrc': disableIcon,
         'actionBtnLabel': actionBtnLabel,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE,
         'animatedTransition': True,
         'disableTooltip': disableTooltip,
         'enabled': enabled}

    def __makeCloseRendererVO(self):
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

    def __makeRentSelectorRendererVO(self):
        if self.__ctx.mode.isAutoRentEnabled():
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

    def __makeEditStyleRendererVO(self):
        editingReason = self._currentStyle.canBeEditedForVehicle(g_currentVehicle.item.intCD)
        if editingReason.reason == EDITING_STYLE_REASONS.NOT_REACHED_LEVEL:
            disableTooltip = backport.text(R.strings.vehicle_customization.customization.slot.editBtn.disabled.notReachedLevel())
        else:
            disableTooltip = backport.text(R.strings.vehicle_customization.customization.slot.editBtn.disabled())
        return {'iconSrc': backport.image(R.images.gui.maps.icons.customization.property_sheet.idle.edit_style()),
         'iconHoverSrc': backport.image(R.images.gui.maps.icons.customization.property_sheet.idle.edit_style_hover()),
         'iconDisableSrc': backport.image(R.images.gui.maps.icons.customization.property_sheet.disable.edit_style_disable()),
         'actionBtnLabel': backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.edit.style()),
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_EDIT_STYLE,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_BTN_RENDERER_UI,
         'animatedTransition': True,
         'disableTooltip': disableTooltip,
         'enabled': bool(editingReason)}

    def __makeCamoColorRendererVO(self):
        btnsBlockVO = []
        colornum = _DEFAULT_COLORNUM
        for palette in self._currentItem.palettes:
            colornum = max(colornum, sum(((color >> 24) / 255.0 > 0 for color in palette)))

        for idx, palette in enumerate(islice(self._currentItem.palettes, _MAX_PALETTES)):
            texture = _PALETTE_TEXTURE.format(colornum=colornum)
            icon = camoIconTemplate(texture=texture, width=_PALETTE_WIDTH, height=_PALETTE_HEIGHT, colors=palette, background=_PALETTE_BACKGROUND, options=self._currentItem.imageOptions)
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
        notifyString = ''
        needNotify = False
        forCurrentItemText = R.strings.vehicle_customization.propertySheet.actionBtn.forCurrentItem.dyn(self._currentItem.itemTypeName)
        forCurrentItemText = backport.text(forCurrentItemText()) if forCurrentItemText.exists() else ''
        isSuitableForOtherAppliedItems = True
        currentMode = self.__ctx.mode
        if self._isItemAppliedToAll:
            currItemTypeID = self._currentItem.itemTypeID
            if self.__isEditableStyle() and currItemTypeID in EDITABLE_STYLE_IRREMOVABLE_TYPES:
                if currentMode.getDependenciesData() and currItemTypeID == GUI_ITEM_TYPE.PAINT:
                    enabled = False
                else:
                    enabled = not currentMode.isBaseItem(self._attachedAnchor)
            else:
                enabled = True
        else:
            intCD = self._currentItem.intCD
            ancestors = getAncestors(intCD, currentMode.getDependenciesData())
            if ancestors:
                for season in SeasonType.COMMON_SEASONS:
                    if season != currentMode.season:
                        if not self.__isAncestorAppliedForOutfit(season, ancestors):
                            enabled = False
                            isSuitableForOtherAppliedItems = False
                            break
                else:
                    enabled = True

            else:
                enabled = currentMode.isPossibleToInstallItemForAllSeasons(self._attachedAnchor, intCD)
        if self._isItemAppliedToAll:
            icon = R.images.gui.maps.icons.customization.property_sheet.remove.icon_del_all_season()
            iconDisable = R.images.gui.maps.icons.customization.property_sheet.disable.icon_season_del_disable()
            hoverIcon = R.images.gui.maps.icons.customization.property_sheet.remove.icon_season_x_hover()
            actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.remove.seasons())
            disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.removeFromAllMapsDisabled(), itemType=forCurrentItemText)
        else:
            icon = R.images.gui.maps.icons.customization.property_sheet.idle.icon_season()
            iconDisable = R.images.gui.maps.icons.customization.property_sheet.disable.icon_season_disable()
            hoverIcon = R.images.gui.maps.icons.customization.property_sheet.idle.icon_season_hover()
            actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.applyToAllMaps())
            if isSuitableForOtherAppliedItems:
                disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.applyToAllMapsDisabled(), itemType=forCurrentItemText)
            else:
                disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.unsuitableForAppliedDisabled())
        if self._attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            lockedSeasons = []
            for season in SeasonType.COMMON_SEASONS:
                outfit = currentMode.getModifiedOutfit(season)
                if isSlotLocked(outfit, self._attachedAnchor):
                    lockedSeasons.append(season)

            if lockedSeasons:
                needNotify = True
                notifyString = self.__makeProjectionDecalInstallToOtherSeasonsNotifyString(lockedSeasons)
        return {'iconSrc': backport.image(icon),
         'iconHoverSrc': backport.image(hoverIcon),
         'iconDisableSrc': backport.image(iconDisable),
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

    def __makeSwitchProgressionLevelRendererVO(self):
        currentProgressionLevel = self._currentItem.getLatestOpenedProgressionLevel(g_currentVehicle.item)
        actionBtnLabel = _ms(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_SWITCHPROGRESSION, current=self.__displayedProgressionLevel, total=currentProgressionLevel)
        enabled = currentProgressionLevel > _MIN_PROGRESSION_LEVEL
        return {'iconSrc': _PROGRESSION_LEVEL_ICONS[self.__displayedProgressionLevel - 1],
         'iconHoverSrc': _PROGRESSION_LEVEL_ICONS_HOVER[self.__displayedProgressionLevel - 1],
         'iconDisableSrc': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_PROPERTY_SHEET_DISABLE_I_DISABLE,
         'actionBtnLabel': actionBtnLabel,
         'actionType': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_ACTION_SWITCH_PROGRESSION_LVL,
         'rendererLnk': CUSTOMIZATION_ALIASES.CUSTOMIZATION_SHEET_SWITCH_RENDERER_UI,
         'enabled': enabled,
         'disableTooltip': VEHICLE_CUSTOMIZATION.PROPERTYSHEET_ACTIONBTN_SWITCHPROGRESSION_DISABLE_TOOLTIP}

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

    def __isCustomMode(self):
        return self.__ctx.modeId == CustomizationModes.CUSTOM

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            self.hide()
            return
        self.__update()

    def __onComponentChanged(self, slotId, refreshCarousel):
        self.__update()

    def __onItemsInstalled(self, item, slotId, seasonId, component):
        if self._currentItem is not None or self._currentStyle is not None:
            if not self.visible:
                self.show()
            else:
                self.__update()
        return

    def __onItemsRemoved(self, *_, **__):
        if self._currentItem is None and self._currentStyle is None:
            self.hide()
        else:
            self.__update()
        return

    def __onItemsBought(self, *_, **__):
        self.__update()

    def __onItemSold(self, *_, **__):
        self.__update()

    def __onTabChanged(self, tabIndex, itemCD=None):
        self._showSwitchers = tabIndex not in CustomizationTabs.REGIONS
        self._isNarrowSlot = tabIndex == CustomizationTabs.EMBLEMS

    def __onSlotSelected(self, slotId):
        if self.attached and self._attachedAnchor != slotId:
            if self.__inscriptionController is not None:
                self.__inscriptionController.stop()
        return

    def __onUpdateSwitchers(self, left, right):
        self.as_setArrowsStatesS(left, right)

    def __onVehicleChanged(self):
        self.hide()

    def __onEditModeEnabled(self, enabled):
        if not enabled:
            self.__update()

    def __isEditableStyle(self):
        return self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE

    def __isAncestorAppliedForOutfit(self, season, ancestors):
        outfit = self.__ctx.mode.getModifiedOutfit(season)
        for ancestorIntCD in ancestors:
            for itemIntCD in outfit.items():
                if ancestorIntCD == itemIntCD:
                    return True

        return False
