# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_toolbar_provider.py
import logging
import weakref
from itertools import islice
import typing
from CurrentVehicle import g_currentVehicle
from Event import Event, EventManager
from constants import CLIENT_COMMAND_SOURCES
from gui.customization.constants import CustomizationModeSource, CustomizationModes
from gui.customization.shared import C11nId, EDITABLE_STYLE_IRREMOVABLE_TYPES, getAncestors, getAvailableRegions, getCustomizationTankPartName
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.customization_button_model import ButtonActionType, CustomizationButtonModel
from gui.impl.gen.view_models.views.lobby.customization.customization_sub_button_model import CustomizationSubButtonModel
from gui.impl.gen.view_models.views.lobby.customization.customization_toolbar_model import CustomizationToolbarModel
from gui.impl.lobby.customization.customization_inscription_controller import CustomizationInscriptionController
from gui.impl.lobby.customization.dialogs import getDataForApplyToOtherSeasonsMessage, showApplyToOtherSeasonsDialog
from gui.impl.lobby.customization.settings_constants import APPLY_TO_ALL_SEASONS_ENABLED, CustomizationSettingsSerializable
from gui.impl.lobby.customization.shared import CustomizationTabs, SCALE_SIZE, isSlotLocked
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.c11n_items import camoIconUrl
from helpers import dependency
from helpers.events_handler import EventsHandler
from items.components.c11n_constants import EDITING_STYLE_REASONS, Options, SeasonType
from skeletons.gui.customization import ICustomizationService
from th_async import th_async, th_await
from vehicle_outfit.outfit import Area
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.impl.lobby.customization.context.context import CustomizationContext
    from gui.impl.lobby.customization.customization_main_view import CustomizationMainView
    from gui.shared.gui_items.customization.c11n_items import Style

class CustomizationToolbarProvider(EventsHandler, CustomizationSettingsSerializable):
    __slots__ = ('__mainView', '__ctx', '__eventsManager', '__isShownToolbar', '__attachedAnchor', '__isApplyToAllSeasonsSelected', '__isItemAppliedToAll', '__displayedProgressionLevel', '__inscriptionController', 'onApplyToAllSeasonsSelectedChanged')
    __service = dependency.descriptor(ICustomizationService)
    __MIN_PROGRESSION_LEVEL = 1
    __DEFAULT_COLORNUM = 1
    __PALETTE_TEXTURE = 'gui/maps/vehicles/camouflages/camo_palette_{colornum}.dds'
    __PALETTE_BACKGROUND = 'gui/maps/vehicles/camouflages/camo_palettes_back.dds'
    __PALETTE_WIDTH = 42
    __PALETTE_HEIGHT = 42
    __MAX_PALETTES = 3

    def __init__(self, mainView):
        self.__mainView = weakref.proxy(mainView)
        self.__ctx = self.__service.getCtx()
        self.__eventsManager = EventManager()
        self.__isShownToolbar = False
        self.__attachedAnchor = C11nId()
        self.__isItemAppliedToAll = False
        self.__displayedProgressionLevel = 0
        self.__inscriptionController = None
        self.onApplyToAllSeasonsSelectedChanged = Event(self.__eventsManager)
        return

    def init(self):
        self.__inscriptionController = CustomizationInscriptionController(self.__mainView)
        self._loadSettings()
        self._subscribe()

    def fini(self):
        self._unsubscribe()
        self._dumpSettings()
        self.__eventsManager.clear()
        self.__inscriptionController = None
        return

    @property
    def viewModel(self):
        return self.__mainView.viewModel.toolbarModel

    @property
    def inEditMode(self):
        return self.__inscriptionController is not None and self.__inscriptionController.visible

    @property
    def attachedAnchor(self):
        return self.__attachedAnchor

    @property
    def attached(self):
        return self.__isValidSlot(self.__attachedAnchor)

    @property
    def isApplyToAllSeasonsAvailable(self):
        return self.__ctx.mode.selectedItem is not None and any((self.__ctx.mode.isPossibleToInstallItemForAllSeasons(slotID, self.__ctx.mode.selectedItem.intCD) for slotID in self.__ctx.mode.getAnchorsData()))

    @property
    def isApplyToAllSeasonsSelected(self):
        return self.getSetting(APPLY_TO_ALL_SEASONS_ENABLED, False)

    @property
    def isShownToolbar(self):
        return self.__isShownToolbar

    @property
    def __currentSlotData(self):
        return self.__getSlotData(self.__attachedAnchor)

    @property
    def __currentItem(self):
        slotData = self.__currentSlotData
        if slotData is None or not slotData.intCD:
            return
        else:
            item = self.__service.getItemByCD(slotData.intCD)
            return item

    @property
    def __currentStyle(self):
        isNotEditableStyleMode = self.__attachedAnchor.slotType == GUI_ITEM_TYPE.STYLE and self.__ctx.mode.modeId != CustomizationModes.EDITABLE_STYLE
        return self.__ctx.mode.modifiedStyle if isNotEditableStyleMode else None

    @property
    def __currentComponent(self):
        slotData = self.__currentSlotData
        return None if slotData is None else slotData.component

    def locateOnAnchor(self, slotId):
        if slotId != self.__attachedAnchor:
            self.__attachToAnchor(slotId)

    def locateToCustomizationPreview(self):
        anchor = C11nId()
        self.__attachToAnchor(anchor)

    def show(self):
        self.__isShownToolbar = True
        self.__update()
        self.__ctx.events.onPropertySheetShown(self.__attachedAnchor)

    def hide(self):
        if not self.__isShownToolbar:
            return
        else:
            self.__isShownToolbar = False
            if self.__ctx is not None:
                self.__ctx.events.onPropertySheetHidden()
            if self.__inscriptionController is not None:
                self.__inscriptionController.stop()
            self.__update()
            return

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

    def setIsApplyToAllSeasons(self, isApplyToAllSeasonsSelected):
        self.setSetting(APPLY_TO_ALL_SEASONS_ENABLED, isApplyToAllSeasonsSelected)
        self.onApplyToAllSeasonsSelectedChanged()

    def _getEvents(self):
        return ((self.viewModel.onActionBtnClick, self.__onActionBtnClick),
         (self.__ctx.events.onCacheResync, self.__onCacheResync),
         (self.__ctx.events.onItemInstalled, self.__onItemsInstalled),
         (self.__ctx.events.onItemsRemoved, self.__onItemsRemoved),
         (self.__ctx.events.onComponentChanged, self.__onComponentChanged),
         (self.__ctx.events.onItemsBought, self.__onItemsBought),
         (self.__ctx.events.onItemSold, self.__onItemSold),
         (self.__ctx.events.onEditModeEnabled, self.__onEditModeEnabled),
         (self.__inscriptionController.onEdited, self.__onInscriptionEdited),
         (g_currentVehicle.onChanged, self.__onVehicleChanged))

    def handleLobbyClick(self):
        return self.__inscriptionController.handleLobbyClick() if self.__inscriptionController is not None else False

    def lobbyViewMouseEvent(self, ctx):
        self.__inscriptionController.handleLobbyViewMouseEvent(ctx)

    @staticmethod
    def __isValidSlot(slotID):
        return slotID is not None and slotID.slotType != -1 and slotID.regionIdx != -1 and slotID.areaId != -1

    def __onActionBtnClick(self, args):
        buttonActionType = ButtonActionType(args['actionType'])
        actionData = 0 if 'actionData' not in args else int(args['actionData'])
        if self.__attachedAnchor == C11nId():
            return
        if buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS:
            self.__isItemAppliedToAll = not self.__isItemAppliedToAll
            self.__applyToOtherAreas(self.__isItemAppliedToAll)
        elif buttonActionType in (ButtonActionType.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS, ButtonActionType.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS_ALERT, ButtonActionType.CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_SEASONS):
            self.__changeAppliedToOtherSeasons(self.__attachedAnchor)
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE:
            self.__removeElement()
        elif buttonActionType in (ButtonActionType.CUSTOMIZATION_SHEET_RENT_PROLONG, ButtonActionType.CUSTOMIZATION_SHEET_RENT_NOT_PROLONG):
            self.__ctx.mode.changeAutoRent(CLIENT_COMMAND_SOURCES.RENTED_STYLE_RADIAL_MENU)
            self.__update()
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_PARTS:
            self.__removeFromAllAreas()
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_SCALE_CHANGE:
            if self.__attachedAnchor.slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
                self.__ctx.mode.changeCamouflageScale(self.__attachedAnchor, actionData)
            elif self.__attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                actionData += 1
                self.__ctx.mode.changeProjectionDecalScale(self.__attachedAnchor, actionData)
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_COLOR_CHANGE:
            self.__ctx.mode.changeCamouflageColor(self.__attachedAnchor, actionData)
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_CLOSE:
            self.__ctx.mode.unselectSlot()
        elif buttonActionType in (ButtonActionType.CUSTOMIZATION_SHEET_ACTION_HORIZONZONTAL_MIRROR_LEFT,
         ButtonActionType.CUSTOMIZATION_SHEET_ACTION_HORIZONZONTAL_MIRROR_RIGHT,
         ButtonActionType.CUSTOMIZATION_SHEET_ACTION_MIRROR_LEFT_DOWN,
         ButtonActionType.CUSTOMIZATION_SHEET_ACTION_MIRROR_RIGHT_UP):
            self.__ctx.mode.mirrorDecal(self.__attachedAnchor, Options.MIRRORED_HORIZONTALLY)
        elif buttonActionType in (ButtonActionType.CUSTOMIZATION_SHEET_ACTION_VERTICAL_MIRROR_UP,
         ButtonActionType.CUSTOMIZATION_SHEET_ACTION_VERTICAL_MIRROR_DOWN,
         ButtonActionType.CUSTOMIZATION_SHEET_ACTION_MIRROR_LEFT_UP,
         ButtonActionType.CUSTOMIZATION_SHEET_ACTION_MIRROR_RIGHT_DOWN):
            self.__ctx.mode.mirrorDecal(self.__attachedAnchor, Options.MIRRORED_VERTICALLY)
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_EDIT:
            self.__inscriptionController.start(self.__attachedAnchor)
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_INFO:
            self.__ctx.events.onShowStyleInfo()
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_GET_BACK:
            item = self.__currentItem
            progressionLevel = item.getUsedProgressionLevel(self.__currentComponent)
            if self.isApplyToAllSeasonsSelected:
                self.__ctx.mode.removeItemFromAllSeasons(self.__attachedAnchor)
            else:
                self.__removeElement()
            self.__ctx.events.onGetItemBackToHand(item, progressionLevel)
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_SWITCH_PROGRESSION_LVL:
            currentProgressionLevel = self.__currentItem.getLatestOpenedProgressionLevel(g_currentVehicle.item)
            if actionData == 0:
                self.__displayedProgressionLevel = self.__displayedProgressionLevel % currentProgressionLevel + 1
            elif actionData == 1:
                self.__displayedProgressionLevel -= 1
                self.__displayedProgressionLevel = self.__displayedProgressionLevel % currentProgressionLevel
            progression = self.__displayedProgressionLevel
            if self.__displayedProgressionLevel == currentProgressionLevel:
                progression = 0
            self.__ctx.mode.changeItemProgression(self.__attachedAnchor, progression)
            self.__update()
        elif buttonActionType == ButtonActionType.CUSTOMIZATION_SHEET_ACTION_EDIT_STYLE:
            self.__ctx.editStyle(self.__currentStyle.intCD, source=CustomizationModeSource.PROPERTIES_SHEET)

    def __update(self):
        if self.__currentItem is None and self.__currentStyle is None:
            self.__isShownToolbar = False
        elif self.__isShownToolbar and self.attached:
            self.__updateInscriptionController()
            self.__updateItemAppliedToAllFlag()
            self.__updateProgressionLevel()
            self.__isShownToolbar = True
        else:
            self.__isShownToolbar = False
        self.__fillToolbarModel()
        return

    def __updateInscriptionController(self):
        if self.__inscriptionController is None:
            return
        else:
            self.__inscriptionController.update(self.__attachedAnchor)
            return

    def __fillToolbarModel(self):
        with self.viewModel.transaction() as model:
            model.setIsToolbarPanelEnabled(self.__isShownToolbar)
            if self.__inscriptionController is not None:
                model.setIsInscriptionPanelEnabled(self.__inscriptionController.visible)
            buttonModels = model.getButtonList()
            buttonModels.clear()
            if not self.__isShownToolbar:
                return
            slotType = self.__attachedAnchor.slotType
            if slotType == GUI_ITEM_TYPE.PAINT:
                self.__fillPaintButtons(buttonModels)
            elif slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
                self.__fillCamouflageButtons(buttonModels)
            elif slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                self.__fillProjectionDecalButtons(buttonModels)
            elif slotType in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.PERSONAL_NUMBER):
                self.__fillDecalButtons(buttonModels)
            elif slotType == GUI_ITEM_TYPE.MODIFICATION:
                self.__fillModificationsButtons(buttonModels)
            elif slotType == GUI_ITEM_TYPE.STYLE:
                self.__fillStyleButtons(buttonModels)
            else:
                _logger.error('Cannot get customization properties sheet renderers for slotType: %s', slotType)
            self.__addRemoveButtonData(buttonModels)
            self.__addCloseButtonData(buttonModels)
            buttonModels.invalidate()
        return

    def __fillStyleButtons(self, buttonListModel):
        renderers = []
        isRentable = self.__currentStyle is not None and self.__currentStyle.isRentable
        isEditable = self.__currentStyle is not None and self.__currentStyle.isEditable
        self.__addStyleInfoButtonData(buttonListModel)
        if isRentable:
            self.__addRentSelectorButtonData(buttonListModel)
        if isEditable:
            self.__addEditStyleButton(buttonListModel)
        return renderers

    def __fillModificationsButtons(self, buttonListModel):
        self.__addSetOnOtherSeasonsButtonData(buttonListModel)

    def __fillDecalButtons(self, buttonListModel):
        if self.__currentItem.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
            self.__addEditInscriptionButtonData(buttonListModel)
        self.__addSetOnOtherSeasonsButtonData(buttonListModel)

    def __fillProjectionDecalButtons(self, buttonListModel):
        if self.__currentItem.isProgressive:
            self.__addSwitchProgressionLevelButtonData(buttonListModel)
        self.__addMirrorButtonData(buttonListModel)
        self.__addScaleButtonData(buttonListModel)
        self.__addGetBackButtonData(buttonListModel)
        self.__addSetOnOtherSeasonsButtonData(buttonListModel)

    def __fillPaintButtons(self, buttonListModel):
        if self.__isCustomMode():
            self.__addSetOnOtherTankPartsButtonData(buttonListModel)
        else:
            self.__addSetOnOtherSeasonsButtonData(buttonListModel)

    def __fillCamouflageButtons(self, buttonListModel):
        self.__addCamoColorButtonData(buttonListModel)
        self.__addScaleButtonData(buttonListModel)
        if self.__isCustomMode():
            self.__addSetOnOtherTankPartsButtonData(buttonListModel)
        else:
            self.__addSetOnOtherSeasonsButtonData(buttonListModel)

    def __addCloseButtonData(self, buttonListModel):
        actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_CLOSE
        disableTooltip = ''
        actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.close())
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, True)

    def __addRemoveButtonData(self, buttonListModel):
        slotType = self.__attachedAnchor.slotType
        isEditableStyle = self.__isEditableStyle()
        actionBtn = R.strings.vehicle_customization.propertySheet.actionBtn
        if slotType == GUI_ITEM_TYPE.MODIFICATION:
            actionBtnLabel = backport.text(actionBtn.remove.modification())
        elif slotType == GUI_ITEM_TYPE.EMBLEM:
            actionBtnLabel = backport.text(actionBtn.remove.emblem())
        elif slotType == GUI_ITEM_TYPE.INSCRIPTION:
            actionBtnLabel = backport.text(actionBtn.remove.inscription())
        elif slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            actionBtnLabel = backport.text(actionBtn.remove.projectionDecal())
        elif slotType == GUI_ITEM_TYPE.STYLE:
            actionBtnLabel = backport.text(actionBtn.remove3dStyle() if self.__currentStyle.is3D else actionBtn.remove2dStyle())
        elif slotType == GUI_ITEM_TYPE.PAINT and isEditableStyle:
            actionBtnLabel = backport.text(actionBtn.remove.paint())
        elif slotType == GUI_ITEM_TYPE.CAMOUFLAGE and isEditableStyle:
            actionBtnLabel = backport.text(actionBtn.remove.camouflage())
        else:
            actionBtnLabel = backport.text(actionBtn.remove.dyn(getCustomizationTankPartName(self.__attachedAnchor.areaId, self.__attachedAnchor.regionIdx))())
        item = self.__currentItem if self.__currentItem is not None else self.__currentStyle
        if item is None:
            return
        else:
            forCurrentItemText = actionBtn.forCurrentItem.dyn(item.itemTypeName)
            forCurrentItemText = backport.text(forCurrentItemText()) if forCurrentItemText.exists() else ''
            disableTooltip = backport.text(actionBtn.removeDisabled(), itemType=forCurrentItemText)
            if isEditableStyle and item.itemTypeID in EDITABLE_STYLE_IRREMOVABLE_TYPES:
                if self.__ctx.mode.getDependenciesData() and item.itemTypeID != GUI_ITEM_TYPE.CAMOUFLAGE:
                    enabled = False
                else:
                    enabled = not self.__ctx.mode.isBaseItem(self.__attachedAnchor)
            else:
                enabled = True
            actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE
            self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, enabled)
            return

    def __addEditStyleButton(self, buttonListModel):
        editingReason = self.__currentStyle.canBeEditedForVehicle(g_currentVehicle.item.intCD)
        if editingReason.reason == EDITING_STYLE_REASONS.NOT_REACHED_LEVEL:
            disableTooltip = backport.text(R.strings.vehicle_customization.customization.slot.editBtn.disabled.notReachedLevel())
        else:
            disableTooltip = backport.text(R.strings.vehicle_customization.customization.slot.editBtn.disabled())
        actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_EDIT_STYLE
        actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.edit.style())
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, bool(editingReason))

    def __addRentSelectorButtonData(self, buttonListModel):
        if self.__ctx.mode.isAutoRentEnabled():
            actionBtnLabel = backport.text(R.strings.vehicle_customization.customization.popover.style.notautoProlongationLabel())
            actionType = ButtonActionType.CUSTOMIZATION_SHEET_RENT_NOT_PROLONG
        else:
            actionBtnLabel = backport.text(R.strings.vehicle_customization.customization.popover.style.autoProlongationLabel())
            actionType = ButtonActionType.CUSTOMIZATION_SHEET_RENT_PROLONG
        disableTooltip = ''
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, True)

    def __addStyleInfoButtonData(self, buttonListModel):
        enabled = self.__currentStyle is not None and bool(self.__currentStyle.longDescriptionSpecial)
        actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_INFO
        disableTooltip = backport.text(R.strings.vehicle_customization.customization.propertySheet.disabled.styleInfo())
        actionBtnLabel = backport.text(R.strings.vehicle_customization.customization.popover.style.info())
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, enabled)
        return

    def __addEditInscriptionButtonData(self, buttonListModel):
        actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_EDIT
        disableTooltip = ''
        actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.edit.inscription())
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, True)

    def __addGetBackButtonData(self, buttonListModel):
        actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.getBack())
        actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_GET_BACK
        disableTooltip = backport.text(R.strings.vehicle_customization.customization.propertySheet.disabled.mirror())
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, True)

    def __addSwitchProgressionLevelButtonData(self, buttonListModel):
        currentProgressionLevel = self.__currentItem.getLatestOpenedProgressionLevel(g_currentVehicle.item)
        actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_SWITCH_PROGRESSION_LVL
        actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.switchProgression(), current=self.__displayedProgressionLevel, total=currentProgressionLevel)
        disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.switchProgression.disable.tooltip())
        isEnabled = currentProgressionLevel > self.__MIN_PROGRESSION_LEVEL
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, isEnabled, self.__displayedProgressionLevel)

    def __addMirrorButtonData(self, buttonListModel):
        if self.__attachedAnchor.slotType not in (GUI_ITEM_TYPE.PROJECTION_DECAL,):
            return
        horizontalMirror = [ButtonActionType.CUSTOMIZATION_SHEET_ACTION_HORIZONZONTAL_MIRROR_RIGHT, ButtonActionType.CUSTOMIZATION_SHEET_ACTION_HORIZONZONTAL_MIRROR_LEFT]
        verticalMirror = [ButtonActionType.CUSTOMIZATION_SHEET_ACTION_VERTICAL_MIRROR_UP, ButtonActionType.CUSTOMIZATION_SHEET_ACTION_VERTICAL_MIRROR_DOWN]
        comboMirror = [ButtonActionType.CUSTOMIZATION_SHEET_ACTION_MIRROR_LEFT_UP,
         ButtonActionType.CUSTOMIZATION_SHEET_ACTION_MIRROR_RIGHT_UP,
         ButtonActionType.CUSTOMIZATION_SHEET_ACTION_MIRROR_LEFT_DOWN,
         ButtonActionType.CUSTOMIZATION_SHEET_ACTION_MIRROR_RIGHT_DOWN]
        slotId = self.__attachedAnchor
        slot = g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
        canBeMirroredHorizontally = self.__currentItem.canBeMirroredHorizontally
        canBeMirroredVertically = self.__currentItem.canBeMirroredVertically and slot.canBeMirroredVertically
        isMirroredHorizontally = self.__currentComponent.isMirroredHorizontally()
        isMirroredVertically = self.__currentComponent.isMirroredVertically()
        if canBeMirroredHorizontally and canBeMirroredVertically:
            mirrorStates = comboMirror
            currentMirrorState = isMirroredVertically | isMirroredHorizontally
        elif canBeMirroredVertically:
            mirrorStates = verticalMirror
            currentMirrorState = bool(isMirroredVertically)
        else:
            mirrorStates = horizontalMirror
            currentMirrorState = isMirroredHorizontally
        actionType = mirrorStates[currentMirrorState]
        actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.mirror())
        disableTooltip = backport.text(R.strings.vehicle_customization.customization.propertySheet.disabled.mirror())
        isEnabled = canBeMirroredHorizontally or canBeMirroredVertically
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, isEnabled)

    def __addScaleButtonData(self, buttonListModel):
        buttonModel = CustomizationButtonModel()
        buttonModel.setActionType(ButtonActionType.CUSTOMIZATION_SHEET_ACTION_SCALE_CHANGE)
        buttonModel.setDisableTooltip('')
        buttonModel.setActionBtnLabel('')
        isEnabled = self.__fillScaleSubButtons(buttonModel.getSubButtons())
        buttonModel.setProgressionLevel(0)
        buttonModel.setIsEnabled(isEnabled)
        buttonListModel.addViewModel(buttonModel)

    def __fillScaleSubButtons(self, subButtons):
        if self.__attachedAnchor.slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
            selected = self.__currentComponent.patternSize
        elif self.__attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            selected = self.__currentComponent.scaleFactorId - 1
        else:
            return False
        for idx, icon in enumerate(SCALE_SIZE):
            subButtonModel = CustomizationSubButtonModel()
            subButtonModel.setIcon(icon)
            subButtonModel.setIsSelected(selected == idx)
            subButtonModel.setActionData(idx)
            subButtons.addViewModel(subButtonModel)

        subButtons.invalidate()
        return True

    def __addCamoColorButtonData(self, buttonListModel):
        buttonModel = CustomizationButtonModel()
        buttonModel.setActionType(ButtonActionType.CUSTOMIZATION_SHEET_ACTION_COLOR_CHANGE)
        subButtons = buttonModel.getSubButtons()
        self.__fillCamoColorSubButtons(subButtons)
        isEnabled = len(subButtons) == self.__MAX_PALETTES
        disableTooltip = '' if isEnabled else backport.text(R.strings.vehicle_customization.customization.propertySheet.disabled.color())
        buttonModel.setDisableTooltip(disableTooltip)
        buttonModel.setActionBtnLabel('')
        buttonModel.setProgressionLevel(0)
        buttonModel.setIsEnabled(isEnabled)
        buttonListModel.addViewModel(buttonModel)

    def __fillCamoColorSubButtons(self, subButtons):
        colorNum = self.__DEFAULT_COLORNUM
        currentItem = self.__currentItem
        for palette in currentItem.palettes:
            colorNum = max(colorNum, sum(((color >> 24) / 255.0 > 0 for color in palette)))

        for idx, palette in enumerate(islice(currentItem.palettes, self.__MAX_PALETTES)):
            texture = self.__PALETTE_TEXTURE.format(colornum=colorNum)
            icon = camoIconUrl(texture=texture, width=self.__PALETTE_WIDTH, height=self.__PALETTE_HEIGHT, colors=palette, background=self.__PALETTE_BACKGROUND, options=currentItem.imageOptions)
            subButtonModel = CustomizationSubButtonModel()
            subButtonModel.setPaletteIcon(icon)
            subButtonModel.setIsSelected(idx == self.__currentComponent.palette)
            subButtonModel.setActionData(idx)
            subButtons.addViewModel(subButtonModel)

        subButtons.invalidate()

    def __addSetOnOtherTankPartsButtonData(self, buttonListModel):
        actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.applyToWholeTank())
        forCurrentItemText = R.strings.vehicle_customization.propertySheet.actionBtn.forCurrentItem.dyn(self.__currentItem.itemTypeName)
        forCurrentItemText = backport.text(forCurrentItemText()) if forCurrentItemText.exists() else ''
        disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.applyToWholeTankDisabled(), itemType=forCurrentItemText)
        enabled = True
        if self.__isItemAppliedToAll:
            actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.cancel())
            actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_PARTS
        else:
            actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS
            enabled = self.__ctx.mode.isPossibleToInstallToAllTankAreas(self.__currentSlotData.intCD, self.__attachedAnchor.slotType)
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, enabled)

    def __addSetOnOtherSeasonsButtonData(self, buttonListModel):
        forCurrentItemText = R.strings.vehicle_customization.propertySheet.actionBtn.forCurrentItem.dyn(self.__currentItem.itemTypeName)
        forCurrentItemText = backport.text(forCurrentItemText()) if forCurrentItemText.exists() else ''
        isSuitableForOtherAppliedItems = True
        currentMode = self.__ctx.mode
        if self.__isItemAppliedToAll:
            currItemTypeID = self.__currentItem.itemTypeID
            if self.__isEditableStyle() and currItemTypeID in EDITABLE_STYLE_IRREMOVABLE_TYPES:
                if currentMode.getDependenciesData() and currItemTypeID == GUI_ITEM_TYPE.PAINT:
                    enabled = False
                else:
                    enabled = not currentMode.isBaseItem(self.__attachedAnchor)
            else:
                enabled = True
        else:
            intCD = self.__currentItem.intCD
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
                enabled = currentMode.isPossibleToInstallItemForAllSeasons(self.__attachedAnchor, intCD)
        if self.__isItemAppliedToAll:
            actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_SEASONS
            actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.remove.seasons())
            disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.removeFromAllMapsDisabled(), itemType=forCurrentItemText)
        else:
            actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS
            actionBtnLabel = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.applyToAllMaps())
            if isSuitableForOtherAppliedItems:
                disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.applyToAllMapsDisabled(), itemType=forCurrentItemText)
            else:
                disableTooltip = backport.text(R.strings.vehicle_customization.propertySheet.actionBtn.unsuitableForAppliedDisabled())
            lockedSeasons = self.__getLockeSeasonsForApply(self.__attachedAnchor)
            if self.__attachedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL and lockedSeasons:
                actionType = ButtonActionType.CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS_ALERT
                seasons, removed, these, _ = getDataForApplyToOtherSeasonsMessage(lockedSeasons)
                disableTooltip = backport.text(R.strings.dialogs.customization.applyToOtherSeasons.alert_message(), season=seasons, removed=removed, this=these)
        self.__fillSimpleCustomizationButtonModel(buttonListModel, actionType, disableTooltip, actionBtnLabel, enabled)

    def __fillSimpleCustomizationButtonModel(self, buttonListModel, actionType, disableTooltip, actionBtnLabel, isEnabled, progressionLevel=0):
        buttonModel = CustomizationButtonModel()
        buttonModel.setActionType(actionType)
        buttonModel.setIsEnabled(isEnabled)
        disableTooltip = '' if isEnabled else disableTooltip
        buttonModel.setDisableTooltip(disableTooltip)
        buttonModel.setProgressionLevel(progressionLevel)
        buttonModel.setActionBtnLabel(actionBtnLabel)
        buttonListModel.addViewModel(buttonModel)

    def __isCustomMode(self):
        return self.__ctx.modeId == CustomizationModes.CUSTOM

    def __attachToAnchor(self, anchor):
        if not g_currentVehicle.isPresent():
            return
        else:
            isInscriptionControllerWasVisible = self.__inscriptionController.visible
            if self.attached:
                if self.__inscriptionController.visible:
                    self.__inscriptionController.stop()
            self.__attachedAnchor = anchor
            if self.__currentItem is not None or self.__currentStyle is not None:
                self.show()
            else:
                self.hide()
                if self.__ctx is not None and isInscriptionControllerWasVisible:
                    self.__ctx.events.onPropertySheetHidden()
            return

    def __applyToOtherAreas(self, installItem):
        if self.__ctx.tabId not in (CustomizationTabs.PAINTS, CustomizationTabs.CAMOUFLAGES):
            return
        if installItem:
            self.__ctx.mode.installItemToAllTankAreas(self.__ctx.season, self.__attachedAnchor.slotType, self.__currentSlotData)
        else:
            self.__ctx.mode.removeItemFromAllTankAreas(self.__ctx.season, self.__attachedAnchor.slotType)
        self.__update()

    def __updateItemAppliedToAllFlag(self):
        if self.__ctx.tabId in (CustomizationTabs.PAINTS, CustomizationTabs.CAMOUFLAGES):
            if self.__isEditableStyle():
                self.__isItemAppliedToAll = self.__isItemAppliedToAllSeasons()
            else:
                self.__isItemAppliedToAll = self.__isItemAppliedToAllRegions()
        elif self.__ctx.tabId in (CustomizationTabs.MODIFICATIONS,
         CustomizationTabs.EMBLEMS,
         CustomizationTabs.INSCRIPTIONS,
         CustomizationTabs.PROJECTION_DECALS):
            self.__isItemAppliedToAll = self.__isItemAppliedToAllSeasons()
        else:
            self.__isItemAppliedToAll = False

    def __isItemAppliedToAllSeasons(self):
        slotData = self.__ctx.mode.getSlotDataFromSlot(self.__attachedAnchor)
        if not slotData.intCD:
            return False
        for season in SeasonType.COMMON_SEASONS:
            if season == self.__ctx.season:
                continue
            otherSlotData = self.__ctx.mode.getSlotDataFromSlot(self.__attachedAnchor, season)
            df = otherSlotData.weakDiff(slotData)
            if not slotData.intCD or df.intCD:
                return False

        return True

    def __isItemAppliedToAllRegions(self):
        for areaId in Area.TANK_PARTS:
            regionsIndexes = getAvailableRegions(areaId, self.__attachedAnchor.slotType)
            outfit = self.__ctx.mode.currentOutfit
            multiSlot = outfit.getContainer(areaId).slotFor(self.__attachedAnchor.slotType)
            for regionIdx in regionsIndexes:
                slotData = multiSlot.getSlotData(regionIdx)
                df = self.__currentSlotData.weakDiff(slotData)
                if not slotData.intCD or df.intCD:
                    return False

        return True

    def __isEditableStyle(self):
        return self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE

    def __changeAppliedToOtherSeasons(self, slotID):
        if not self.__isItemAppliedToAll:
            self.__applyToOtherSeasons(slotID)
        else:
            self.__removeFromOtherSeasons(slotID)

    def __getLockeSeasonsForApply(self, slotID):
        lockedSeasons = []
        for season in SeasonType.COMMON_SEASONS:
            outfit = self.__ctx.mode.getModifiedOutfit(season)
            if isSlotLocked(outfit, slotID):
                lockedSeasons.append(season)

        return lockedSeasons

    def __applyToOtherSeasons(self, slotID, silent=False):
        if self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS:
            lockedSeasons = self.__getLockeSeasonsForApply(slotID)
            if lockedSeasons:
                self.__showApplyToOtherSeasonsDialog(slotID, lockedSeasons)
                return
        self.__ctx.mode.installItemToAllSeasons(slotID, self.__getSlotData(slotID))
        self.__isItemAppliedToAll = True
        if not silent:
            self.__update()

    def __removeFromOtherSeasons(self, slotID, silent=False):
        self.__ctx.mode.removeItemFromAllSeasons(slotID, silent)
        self.__isItemAppliedToAll = False
        self.__update()

    @th_async
    def __showApplyToOtherSeasonsDialog(self, slotID, lockedSeasons):
        confirmed = yield th_await(showApplyToOtherSeasonsDialog(lockedSeasons))
        if not confirmed:
            self.__ctx.mode.removeItem(slotID, self.__ctx.season)
            return

        def isProjectionDecal(item):
            return item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL

        for season in SeasonType.COMMON_SEASONS:
            outfit = self.__ctx.mode.getModifiedOutfit(season)
            if isSlotLocked(outfit, slotID):
                self.__ctx.mode.removeItemsFromSeason(season, isProjectionDecal, refresh=False)

        self.__ctx.mode.installItemToAllSeasons(slotID, self.__getSlotData(slotID))
        self.__isItemAppliedToAll = True
        self.__update()

    def __getSlotData(self, slotID):
        if not self.__isValidSlot(slotID) or slotID.slotType == GUI_ITEM_TYPE.STYLE:
            return
        outfit = self.__ctx.mode.currentOutfit
        container = outfit.getContainer(slotID.areaId)
        slot = container.slotFor(slotID.slotType)
        if slot is None:
            return
        else:
            return slot.getSlotData(slotID.regionIdx) if slotID.regionIdx != -1 else None

    def __removeElement(self):
        self.__ctx.mode.removeItem(self.__attachedAnchor)
        self.__ctx.mode.unselectSlot()

    def __removeFromAllAreas(self):
        self.__ctx.mode.removeItemFromAllTankAreas(self.__ctx.season, self.__attachedAnchor.slotType)
        self.__update()

    def __updateProgressionLevel(self):
        if self.__currentItem is not None and self.__currentItem.isProgressive:
            currentProgressionLevel = self.__currentItem.getLatestOpenedProgressionLevel(g_currentVehicle.item)
            if self.__currentComponent and self.__currentComponent.progressionLevel > 0:
                self.__displayedProgressionLevel = self.__currentComponent.progressionLevel
            else:
                self.__displayedProgressionLevel = currentProgressionLevel
        return

    def __isAncestorAppliedForOutfit(self, season, ancestors):
        outfit = self.__ctx.mode.getModifiedOutfit(season)
        for ancestorIntCD in ancestors:
            for itemIntCD in outfit.items():
                if ancestorIntCD == itemIntCD:
                    return True

        return False

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            self.hide()
            return
        self.__update()

    def __onItemsInstalled(self, _, slotId=C11nId(), *args, **kwargs):
        if self.isApplyToAllSeasonsAvailable and self.__isValidSlot(slotId):
            if self.isApplyToAllSeasonsSelected:
                self.__applyToOtherSeasons(slotId)
        if self.__currentItem is not None or self.__currentStyle is not None:
            if not self.__isShownToolbar:
                self.show()
            else:
                self.__update()
        return

    def __onItemsRemoved(self, slotId=C11nId(), *args, **kwargs):
        if self.isApplyToAllSeasonsAvailable:
            if self.isApplyToAllSeasonsSelected and self.__isValidSlot(slotId):
                self.__removeFromOtherSeasons(slotId, silent=True)
        if self.__currentItem is None and self.__currentStyle is None:
            self.__ctx.mode.unselectSlot()
            self.hide()
        else:
            self.__update()
        return

    def __onInscriptionEdited(self, slotId):
        if self.isApplyToAllSeasonsSelected and self.__isValidSlot(slotId):
            self.__applyToOtherSeasons(slotId, silent=True)

    def __onComponentChanged(self, slotId, refreshCarousel):
        self.__update()

    def __onItemsBought(self, *args, **kwargs):
        self.__update()

    def __onItemSold(self, *args, **kwargs):
        self.__update()

    def __onEditModeEnabled(self, enabled, slotId):
        if not enabled:
            self.__update()

    def __onVehicleChanged(self):
        self.hide()
