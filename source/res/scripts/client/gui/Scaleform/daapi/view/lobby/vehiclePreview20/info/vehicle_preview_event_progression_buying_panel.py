# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_event_progression_buying_panel.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import lookupItem, showItemTooltip
from gui.Scaleform.daapi.view.meta.VehiclePreviewEventProgressionBuyingPanelMeta import VehiclePreviewEventProgressionBuyingPanelMeta
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEventProgressionController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from gui.shared import event_dispatcher

class VehiclePreviewEventProgressionBuyingPanel(VehiclePreviewEventProgressionBuyingPanelMeta):
    __eventProgressionController = dependency.descriptor(IEventProgressionController)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, ctx=None):
        super(VehiclePreviewEventProgressionBuyingPanel, self).__init__()
        self.__items = []

    def setData(self, itemsPack, panelDataVO, packedItemsVO):
        self.__items = itemsPack
        self.as_setDataS(panelDataVO)
        self.as_setSetItemsDataS(packedItemsVO)

    def onBuyClick(self):
        event_dispatcher.showEventProgressionBuyConfirmView(ctx={'vehicle': g_currentPreviewVehicle.item,
         'price': self.__eventProgressionController.getRewardVehiclePrice(g_currentPreviewVehicle.item.intCD)})

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
