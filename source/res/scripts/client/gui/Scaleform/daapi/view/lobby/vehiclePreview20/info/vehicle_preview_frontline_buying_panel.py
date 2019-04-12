# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_frontline_buying_panel.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import lookupItem, showItemTooltip
from gui.Scaleform.daapi.view.meta.VehiclePreviewFrontlineBuyingPanelMeta import VehiclePreviewFrontlineBuyingPanelMeta
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from gui.shared import event_dispatcher

class VehiclePreviewFrontlineBuyingPanel(VehiclePreviewFrontlineBuyingPanelMeta):
    _itemsCache = dependency.descriptor(IItemsCache)
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, ctx=None):
        super(VehiclePreviewFrontlineBuyingPanel, self).__init__()
        self.__items = []

    def setData(self, itemsPack, panelDataVO, packedItemsVO):
        self.__items = itemsPack
        self.as_setDataS(panelDataVO)
        self.as_setSetItemsDataS(packedItemsVO)

    def onBuyClick(self):
        event_dispatcher.showFrontlineBuyConfirmView(ctx={'vehicle': g_currentPreviewVehicle.item})

    def showTooltip(self, intCD, itemType):
        toolTipMgr = self._appLoader.getApp().getToolTipMgr()
        try:
            try:
                itemId = int(intCD)
            except ValueError:
                itemId = None

            rawItem = [ item for item in self.__items if item.id == itemId and item.type == itemType ][0]
            item = lookupItem(rawItem, self._itemsCache, self._goodiesCache)
            showItemTooltip(toolTipMgr, rawItem, item)
        except IndexError:
            return

        return
