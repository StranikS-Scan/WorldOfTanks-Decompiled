# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/vehicle_preview_event_progression_buying_panel.py
import typing
from adisp import process
from async import await, async
from CurrentVehicle import g_currentPreviewVehicle
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.items_kit_helper import lookupItem, showItemTooltip
from gui.Scaleform.daapi.view.meta.VehiclePreviewEventProgressionBuyingPanelMeta import VehiclePreviewEventProgressionBuyingPanelMeta
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.EVENTPROGRESSION_ALIASES import EVENTPROGRESSION_ALIASES
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.shared.gui_items.processors.event_progression import EventProgressionBuyRewardVehicle
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEventProgressionController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from gui.shared import EVENT_BUS_SCOPE, event_dispatcher

class VehiclePreviewEventProgressionBuyingPanel(VehiclePreviewEventProgressionBuyingPanelMeta):
    __eventProgression = dependency.descriptor(IEventProgressionController)
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

    @async
    def onBuyClick(self):
        vehicle = g_currentPreviewVehicle.item
        ctx = {'vehicle': vehicle,
         'price': self.__eventProgression.getRewardVehiclePrice(g_currentPreviewVehicle.item.intCD)}
        dialog = SFWindow(SFViewLoadParams(EVENTPROGRESSION_ALIASES.EVENT_PROGRESION_BUY_CONFIRM_VIEW_ALIAS), EVENT_BUS_SCOPE.LOBBY, ctx=ctx)
        isOk = yield await(dialogs.showSimple(dialog))
        if isOk:
            self.__getRewards(vehicle)

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

    @process
    def __getRewards(self, vehicle):
        result = yield EventProgressionBuyRewardVehicle(vehicle).request()
        if result and result.success and not self.isDisposed():
            ctx = {'congratulationsViewSettings': {'backBtnLabel': R.strings.store.congratulationAnim.showEpicBtnLabel(),
                                             'backBtnEnabled': True}}
            event_dispatcher.showVehicleBuyDialog(vehicle=vehicle, previousAlias=VIEW_ALIAS.EVENT_PROGRESSION_VEHICLE_PREVIEW, showOnlyCongrats=True, ctx=ctx)
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
