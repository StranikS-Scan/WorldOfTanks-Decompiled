# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/event_progression_style_buying_panel.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.meta.VehiclePreviewEventProgressionBuyingPanelMeta import VehiclePreviewEventProgressionBuyingPanelMeta
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEventProgressionController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from gui.shared import event_dispatcher

class VehiclePreviewEventProgressionStyleBuyingPanel(VehiclePreviewEventProgressionBuyingPanelMeta):
    __eventProgression = dependency.descriptor(IEventProgressionController)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, ctx=None):
        super(VehiclePreviewEventProgressionStyleBuyingPanel, self).__init__()
        self.__style = None
        return

    def setData(self, style, panelDataVO):
        self.__style = style
        self.as_setDataS(panelDataVO)

    def onBuyClick(self):
        event_dispatcher.showEventProgressionBuyConfirmView(ctx={'vehicle': g_currentPreviewVehicle.item,
         'reward': self.__style,
         'price': self.__eventProgression.getRewardStylePrice(self.__style.id)})
