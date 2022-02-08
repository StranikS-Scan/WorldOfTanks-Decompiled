# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/bottom_panel_offer_gift.py
import typing
from gui.Scaleform.daapi.view.lobby.vehicle_preview.items_kit_helper import lookupItem, showItemTooltip
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelOfferGiftMeta import VehiclePreviewBottomPanelOfferGiftMeta
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache

class VehiclePreviewBottomPanelOfferGift(VehiclePreviewBottomPanelOfferGiftMeta):
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, ctx=None):
        super(VehiclePreviewBottomPanelOfferGift, self).__init__()
        self.__items = []
        self.__confirmCallback = None
        return

    def setData(self, itemsPack, panelDataVO, packedItemsVO, confirmCallback):
        self.__items = itemsPack
        self.__confirmCallback = confirmCallback
        self.as_setDataS(panelDataVO)
        self.as_setSetItemsDataS(packedItemsVO)

    def onBuyClick(self):
        self.__confirmCallback()

    def showTooltip(self, intCD, itemType):
        toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
        try:
            try:
                itemId = int(intCD)
            except ValueError:
                itemId = None

            rawItem = [ item for item in self.__items if item.id == itemId and item.type == itemType ][0]
            item = lookupItem(rawItem, self.__itemsCache, self.__goodiesCache)
            showItemTooltip(toolTipMgr, rawItem, item)
        except IndexError:
            return

        return
