# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/tooltips/shop_vehicle_tooltip.py
import time
from gui.impl.gen import R
from gui.impl import backport
from frameworks.wulf import ViewSettings
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency, time_utils
from skeletons.gui.server_events import IEventsCache
from gui.impl.gen.view_models.views.lobby.halloween.tooltips.shop_vehicle_tooltip_model import ShopVehicleTooltipModel
from gui.impl.pub import ViewImpl
from skeletons.gui.shared import IItemsCache

class ShopVehicleTooltip(ViewImpl):
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__id',)

    def __init__(self, tankId):
        settings = ViewSettings(R.views.lobby.halloween.tooltips.ShopVehicleTooltip())
        settings.model = ShopVehicleTooltipModel()
        self.__id = tankId
        super(ShopVehicleTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ShopVehicleTooltip, self).getViewModel()

    def _onLoading(self):
        super(ShopVehicleTooltip, self)._onLoading()
        self.__fillModel()

    def __fillModel(self):
        vehicle = self._itemsCache.items.getItemByCD(int(self.__id))
        with self.viewModel.transaction() as vm:
            vm.setVehicleName(vehicle.userName)
            vm.setVehicleIcon(replaceHyphenToUnderscore(vehicle.name.replace(':', '-')))
            tm = time.gmtime(self._eventsCache.getEventFinishTime() + time_utils.ONE_MINUTE)
            vm.setFooter(backport.text(R.strings.event.shopVehicleTooltip.footer(), year=tm.tm_year, month=tm.tm_mon, day=tm.tm_mday))
