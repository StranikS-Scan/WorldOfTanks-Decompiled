# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/event_progression_buying_panels.py
import typing
from adisp import process
from async import async, await
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
from gui.impl.lobby.common.congrats.congrats_ctx import EventProgressionStyleCongratsCtx
from gui.shared.gui_items.processors.event_progression import getEventProgressionRewardRequester
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEventProgressionController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from gui.shared import EVENT_BUS_SCOPE, event_dispatcher

class _VehiclePreviewEventProgressionBuyingPanel(VehiclePreviewEventProgressionBuyingPanelMeta):
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, _=None):
        super(_VehiclePreviewEventProgressionBuyingPanel, self).__init__()
        self.__items = []

    def setData(self, panelDataVO, **kwargs):
        self.__items = kwargs.get('itemsPack', [])
        self.as_setDataS(panelDataVO)

    @async
    def onBuyClick(self):
        item = self._getItem()
        dialog = SFWindow(SFViewLoadParams(EVENTPROGRESSION_ALIASES.EVENT_PROGRESION_BUY_CONFIRM_VIEW_ALIAS), EVENT_BUS_SCOPE.LOBBY, ctx={'item': item,
         'price': self._getPrice(item)})
        isOk = yield await(dialogs.showSimple(dialog))
        if isOk:
            self.__getRewards(item)

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

    def _getItem(self):
        raise NotImplementedError

    def _getPrice(self, item):
        raise NotImplementedError

    def _showCongrats(self, item):
        raise NotImplementedError

    @process
    def __getRewards(self, item):
        result = yield getEventProgressionRewardRequester(item).request()
        if result:
            if result.success:
                self._showCongrats(item)
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class VehiclePreviewEventProgressionStyleBuyingPanel(_VehiclePreviewEventProgressionBuyingPanel):
    __eventProgression = dependency.descriptor(IEventProgressionController)

    def __init__(self, _=None):
        super(VehiclePreviewEventProgressionStyleBuyingPanel, self).__init__()
        self.__style = None
        return

    def setData(self, panelDataVO, **kwargs):
        self.__style = kwargs.get('style')
        super(VehiclePreviewEventProgressionStyleBuyingPanel, self).setData(panelDataVO, **kwargs)

    def _getItem(self):
        return self.__style

    def _getPrice(self, item):
        return self.__eventProgression.getRewardStylePrice(item.id)

    def _showCongrats(self, item):
        event_dispatcher.showCongrats(EventProgressionStyleCongratsCtx(item))


class VehiclePreviewEventProgressionVehicleBuyingPanel(_VehiclePreviewEventProgressionBuyingPanel):
    __eventProgression = dependency.descriptor(IEventProgressionController)

    def setData(self, panelDataVO, **kwargs):
        super(VehiclePreviewEventProgressionVehicleBuyingPanel, self).setData(panelDataVO, **kwargs)
        self.as_setSetItemsDataS(kwargs.get('packedItemsVO', {}))

    def _getItem(self):
        return g_currentPreviewVehicle.item

    def _getPrice(self, item):
        return self.__eventProgression.getRewardVehiclePrice(item.intCD)

    def _showCongrats(self, item):
        event_dispatcher.showVehicleBuyDialog(vehicle=item, previousAlias=VIEW_ALIAS.EVENT_PROGRESSION_VEHICLE_PREVIEW, showOnlyCongrats=True, ctx={'congratulationsViewSettings': {'backBtnLabel': R.strings.store.congratulationAnim.backToEpicLabel(),
                                         'backBtnEnabled': True}})
