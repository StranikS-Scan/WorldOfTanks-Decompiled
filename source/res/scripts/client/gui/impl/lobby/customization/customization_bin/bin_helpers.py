# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_bin/bin_helpers.py
import logging
from collections import namedtuple
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import InfoItemBase
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.customization.processors.cart import ItemsType
from gui.customization.processors.cart import SeparateItemsProcessor, StyleItemsProcessor, EditableStyleItemsProcessor
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.cart_slot_model import CartSlotModel
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.graphics import isRendererPipelineDeferred
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
_logger = logging.getLogger(__name__)
SelectItemData = namedtuple('SelectItemData', ('season', 'quantity', 'purchaseIndices', 'idx', 'intCD', 'dependents', 'dependentOn', 'component'))

class CartExchangeCreditsInfoItem(InfoItemBase):

    @property
    def itemTypeName(self):
        pass

    @property
    def userName(self):
        pass

    @property
    def itemTypeID(self):
        return GUI_ITEM_TYPE.CUSTOMIZATION

    def getExtraIconInfo(self):
        return None

    def getGUIEmblemID(self):
        pass


class _BaseUIDataPacker(object):

    def __call__(self, desc):
        model = CartSlotModel()
        model.setQuantity(desc.quantity)
        model.setIntCD(desc.intCD)
        model.setItemID(desc.identificator)
        return model


class _ItemUIDataPacker(_BaseUIDataPacker):
    __service = dependency.descriptor(ICustomizationService)

    def __call__(self, desc):
        model = super(_ItemUIDataPacker, self).__call__(desc)
        ctx = self.__service.getCtx()
        item = desc.item
        component = desc.component
        rentalInfoText = ''
        if item.isRentable:
            if ctx.mode.getItemInventoryCount(item) <= 0:
                rentalInfoText = backport.text(R.strings.vehicle_customization.carousel.rentalBattles(), battlesNum=item.rentCount)
                model.setQuantity(0)
            else:
                model.setQuantity(item.rentCount)
        model.setIsWide(item.isWide())
        model.setIsDim(item.isDim())
        model.setCustomizationDisplayType(item.customizationDisplayType())
        model.setIsMainType(item.markedAsFavorite)
        model.setIsWithSerialNumber(item.itemTypeID == GUI_ITEM_TYPE.STYLE and item.isWithSerialNumber)
        model.setIsRental(item.isRentable)
        model.setAutoRentEnabled(ctx.mode.isAutoRentEnabled())
        model.setRentalInfoText(rentalInfoText)
        BuyPriceModelBuilder.fillPriceModelByItemPrice(model.buyPrice, item.getBuyPrice())
        if item.itemTypeID in (GUI_ITEM_TYPE.MODIFICATION, GUI_ITEM_TYPE.STYLE) and item.userName is not None:
            model.setExtraName(item.userName)
        if item.isProgressive and component:
            progressionLevel = component.progressionLevel
            if progressionLevel == 0:
                progressionLevel = item.getLatestOpenedProgressionLevel(g_currentVehicle.item)
            model.setIcon(item.iconUrlByProgressionLevel(progressionLevel))
            model.setProgressionLevel(progressionLevel)
        elif item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and component:
            model.setIcon(item.numberIconUrl(component.number))
        elif item.itemTypeID == GUI_ITEM_TYPE.STYLE and item.isProgressive:
            currentProgression = item.getLatestOpenedProgressionLevel(g_currentVehicle.item)
            model.setTypeId(item.itemTypeID)
            model.setProgressionLevel(desc.progressionLevel)
            model.setIsProgressionRewindEnabled(item.isProgressionRewindEnabled)
            model.setIcon(item.iconUrl)
            BuyPriceModelBuilder.fillPriceModelByItemPrice(model.buyPrice, item.getUpgradePrice(currentProgression, desc.progressionLevel))
        elif item.itemTypeID == GUI_ITEM_TYPE.STYLE and item.isQuestsProgression:
            model.setTypeId(item.itemTypeID)
            model.setIcon(item.iconUrl)
            model.setProgressionLevel(0)
        else:
            model.setIcon(item.iconUrl)
        canShow = item.itemTypeID == GUI_ITEM_TYPE.MODIFICATION or item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL and item.isProgressive
        model.setShowAlert(canShow and not isRendererPipelineDeferred())
        isSpecial = item.isVehicleBound and (item.buyCount > 0 or item.inventoryCount > 0) and not item.isProgressionAutoBound or item.isLimited and item.buyCount > 0
        model.setIsSpecial(isSpecial)
        return model


class _StubUIDataPacker(_BaseUIDataPacker):

    def __call__(self, desc):
        model = super(_StubUIDataPacker, self).__call__(desc)
        model.setIsFromStorage(False)
        model.setTooltip(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM)
        return model


class _SeparateUIDataPacker(_ItemUIDataPacker):

    def __call__(self, desc):
        model = super(_SeparateUIDataPacker, self).__call__(desc)
        model.setIsSelected(desc.selected)
        model.setTooltip(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE)
        model.setIsFromStorage(desc.isFromInventory)
        return model


class _StyleUIDataPacker(_ItemUIDataPacker):

    def __call__(self, desc):
        model = super(_StyleUIDataPacker, self).__call__(desc)
        model.setTooltip(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON)
        model.setIsFromStorage(desc.item.isInInventory)
        return model


class _EditableStyleItemUIDataPacker(_SeparateUIDataPacker):

    def __call__(self, desc):
        model = super(_EditableStyleItemUIDataPacker, self).__call__(desc)
        model.setIsEdited(desc.isEdited)
        model.setTooltip(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_ICON if desc.locked else TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_PURCHASE)
        return model


def getProcessorsMap():
    return {ItemsType.DEFAULT: SeparateItemsProcessor(_SeparateUIDataPacker(), _StubUIDataPacker()),
     ItemsType.STYLE: StyleItemsProcessor(_StyleUIDataPacker(), _StubUIDataPacker()),
     ItemsType.EDITABLE_STYLE: EditableStyleItemsProcessor(_EditableStyleItemUIDataPacker(), _StubUIDataPacker())}
