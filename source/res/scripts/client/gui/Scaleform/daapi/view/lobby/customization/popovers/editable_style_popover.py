# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/popovers/editable_style_popover.py
import typing
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.customization.popovers import C11nPopoverItemData, orderKey
from gui.Scaleform.daapi.view.lobby.customization.shared import ITEM_TYPE_TO_SLOT_TYPE, fitOutfit, getCurrentVehicleAvailableRegionsMap, isStyleEditedForCurrentVehicle
from gui.Scaleform.daapi.view.meta.CustomizationEditedKitPopoverMeta import CustomizationEditedKitPopoverMeta
from gui.customization.constants import CustomizationModes
from gui.customization.shared import SEASONS_ORDER, SEASON_TYPE_TO_NAME, C11nId, EDITABLE_STYLE_IRREMOVABLE_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, getItemPricesVO, icons
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.components.c11n_components import getItemSlotType
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService

class EditableStylePopover(CustomizationEditedKitPopoverMeta):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(EditableStylePopover, self).__init__(ctx)
        self.__ctx = None
        self.__style = None
        return

    def onWindowClose(self):
        self.destroy()

    def remove(self, intCD, slotIds, season):
        self.__ctx.mode.removeFromSlots(slotIds, season)

    def setToDefault(self):
        self.__ctx.mode.clearStyle()

    def removeAll(self):
        if self.__style is not None:
            self.__ctx.changeMode(CustomizationModes.STYLED)
            self.__ctx.mode.removeStyle(self.__style.intCD)
        return

    def _populate(self):
        super(EditableStylePopover, self)._populate()
        self.__ctx = self.__service.getCtx()
        self.__ctx.events.onCacheResync += self.__update
        self.__ctx.events.onSeasonChanged += self.__update
        self.__ctx.events.onItemInstalled += self.__update
        self.__ctx.events.onItemsRemoved += self.__update
        self.__ctx.events.onChangesCanceled += self.__update
        self.__update()

    def _dispose(self):
        if self.__ctx.events is not None:
            self.__ctx.events.onChangesCanceled -= self.__update
            self.__ctx.events.onItemsRemoved -= self.__update
            self.__ctx.events.onItemInstalled -= self.__update
            self.__ctx.events.onSeasonChanged -= self.__update
            self.__ctx.events.onCacheResync -= self.__update
        self.__style = None
        self.__ctx = None
        super(EditableStylePopover, self)._dispose()
        return

    def __setHeader(self):
        if self.__style is None:
            header = backport.text(R.strings.vehicle_customization.customization.kitPopover.title.items())
        else:
            header = R.strings.tooltips.vehiclePreview.boxTooltip.style.header
            header = backport.text(header(), value=self.__style.userName)
        self.as_setHeaderS(text_styles.highTitle(header))
        img = icons.makeImageTag(backport.image(R.images.gui.maps.icons.customization.edited_small()))
        helpMessage = backport.text(R.strings.vehicle_customization.popover.editableStyle.editedItems())
        self.as_setHelpMessageS(img + text_styles.main(helpMessage))
        return

    def __setClearMessage(self):
        if self.__style is None:
            clearMessage = R.strings.vehicle_customization.customization.itemsPopover.clear.message
            clearMessage = text_styles.main(backport.text(clearMessage()))
        else:
            clearMessage = ''
        self.as_showClearMessageS(clearMessage)
        return

    def __update(self, *_):
        outfit = self.__ctx.mode.currentOutfit
        self.__style = self.__service.getItemByID(GUI_ITEM_TYPE.STYLE, outfit.id) if outfit.id else None
        if self.__style is not None and not self.__style.isEditable:
            self.destroy()
        itemsList = self.__buildList()
        self.as_setItemsS({'items': itemsList})
        self.__setHeader()
        self.__setClearMessage()
        self.__updateClearStyleButton()
        return

    def __updateClearStyleButton(self):
        if self.__style is not None:
            modifiedOutfits = self.__ctx.mode.getModifiedOutfits()
            enabled = isStyleEditedForCurrentVehicle(modifiedOutfits, self.__style)
        else:
            enabled = False
        self.as_setDefaultButtonEnabledS(enabled)
        return

    def __buildList(self):
        data = []
        if self.__style is None:
            return data
        else:
            vehicleDescriptor = g_currentVehicle.item.descriptor
            purchaseItems = self.__ctx.mode.getPurchaseItems()
            seasonPurchaseItems = {season:[] for season in SeasonType.COMMON_SEASONS}
            for pItem in purchaseItems:
                if pItem.group not in SeasonType.COMMON_SEASONS:
                    continue
                seasonPurchaseItems[pItem.group].append(pItem)

            availableRegionsMap = getCurrentVehicleAvailableRegionsMap()
            for season in SEASONS_ORDER:
                seasonGroupVO = self.__getSeasonGroupVO(season)
                data.append(seasonGroupVO)
                itemsData = self.__getSeasonItemsData(season, seasonPurchaseItems[season], availableRegionsMap, vehicleDescriptor)
                data.extend(itemsData)

            return data

    def __getSeasonItemsData(self, season, purchaseItems, availableRegionsMap, vehicleDescriptor):
        itemData = {}
        for pItem in purchaseItems:
            item = pItem.item
            if item.isHiddenInUI():
                continue
            sType = getItemSlotType(item.descriptor)
            key = (pItem.item.intCD, pItem.isFromInventory)
            if key not in itemData:
                isBase = not pItem.isEdited
                if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
                    isRemovable = False
                elif sType in self.__style.changeableSlotTypes:
                    if isBase:
                        isRemovable = False
                    elif item.itemTypeID in EDITABLE_STYLE_IRREMOVABLE_TYPES:
                        if bool(self.__style.getDependenciesIntCDs()) and item.itemTypeID != GUI_ITEM_TYPE.CAMOUFLAGE:
                            isRemovable = False
                        else:
                            isRemovable = True
                    else:
                        isRemovable = True
                else:
                    isRemovable = False
                itemData[key] = C11nPopoverItemData(item=item, season=season, isBase=isBase, isRemovable=isRemovable, isRemoved=False, isFromInventory=pItem.isFromInventory)
            slotId = C11nId(pItem.areaID, pItem.slotType, pItem.regionIdx)
            itemData[key].slotsIds.append(slotId._asdict())

        baseOutfit = self.__style.getOutfit(season, vehicleCD=vehicleDescriptor.makeCompactDescr())
        fitOutfit(baseOutfit, availableRegionsMap)
        nationalEmblemItem = self.__service.getItemByID(GUI_ITEM_TYPE.EMBLEM, vehicleDescriptor.type.defaultPlayerEmblemID)
        showStyle = True
        nationalEmblemDetected = False
        otherDetected = False
        for intCD, _, regionIdx, container, _ in baseOutfit.itemsFull():
            item = self.__service.getItemByCD(intCD)
            if item.isHiddenInUI():
                continue
            else:
                showStyle = False
            if not nationalEmblemDetected and intCD == nationalEmblemItem.intCD:
                nationalEmblemDetected = True
            elif not otherDetected and intCD != nationalEmblemItem.intCD:
                otherDetected = True
            key = (intCD, True)
            if key not in itemData:
                itemData[key] = C11nPopoverItemData(item=item, season=season, isBase=True, isRemoved=True, isFromInventory=True)
            if itemData[key].isRemoved:
                areaId = container.getAreaID()
                slotType = ITEM_TYPE_TO_SLOT_TYPE[item.itemTypeID]
                slotId = C11nId(areaId, slotType, regionIdx)
                itemData[key].slotsIds.append(slotId._asdict())

        if nationalEmblemDetected and not otherDetected:
            showStyle = True
            key = (nationalEmblemItem.intCD, True)
            itemData.pop(key)
        if showStyle:
            key = (self.__style.intCD, True)
            itemData[key] = C11nPopoverItemData(item=self.__style, season=season, isBase=True, isRemoved=False, isFromInventory=True)
        data = [ self.__makeItemDataVO(itemData) for itemData in sorted(itemData.values(), key=orderKey) ]
        return data

    def __makeItemDataVO(self, itemData):
        item = itemData.item
        progressionLevel = item.getLatestOpenedProgressionLevel(g_currentVehicle.item)
        icon = item.icon if progressionLevel == -1 else item.iconByProgressionLevel(progressionLevel)
        name = text_styles.main(item.userName)
        if itemData.isRemoved or not itemData.isRemovable:
            countLabel = ''
            price = None
        elif itemData.isFromInventory:
            countLabel = text_styles.main('{} '.format(len(itemData.slotsIds)))
            price = None
        else:
            countLabel = text_styles.main('{} x '.format(len(itemData.slotsIds)))
            price = getItemPricesVO(item.buyPrices.itemPrice)[0]
        disabledLabel = backport.text(R.strings.vehicle_customization.popover.style.removed())
        disabledLabel = text_styles.bonusPreviewText(disabledLabel)
        isApplied = itemData.isBase
        progressionLevel = 0
        if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            progressionLevel = self.__ctx.mode.currentOutfit.progressionLevel
        itemDataVO = {'id': item.intCD,
         'icon': icon,
         'userName': name,
         'numItems': countLabel,
         'isHistoric': item.isHistorical(),
         'price': price,
         'isApplied': isApplied,
         'isWide': item.isWide(),
         'itemsList': itemData.slotsIds,
         'isDim': item.isDim(),
         'isEdited': not itemData.isBase,
         'isDisabled': itemData.isRemoved,
         'disabledLabel': disabledLabel,
         'isRemovable': itemData.isRemovable,
         'seasonType': itemData.season,
         'progressionLevel': progressionLevel}
        return itemDataVO

    @staticmethod
    def __getSeasonGroupVO(season):
        seasonName = SEASON_TYPE_TO_NAME[season]
        seasonTitle = makeHtmlString('html_templates:lobby/customization/StylePopoverSeasonName', seasonName, ctx={'align': 'CENTER'})
        seasonGroupVO = {'isTitle': True,
         'titleLabel': seasonTitle}
        return seasonGroupVO
