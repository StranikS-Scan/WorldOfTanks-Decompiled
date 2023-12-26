# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/ny_select_vehicle_for_discount_popover.py
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleBasicVO
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.meta.NYSelectVehiclePopoverMeta import NYSelectVehiclePopoverMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.new_year.popovers.ny_select_vehicle_popover import NySelectVehiclePopoverDataProvider
from gui.impl.new_year.new_year_helper import formatRomanNumber
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from new_year.ny_processor import ApplyVehicleDiscountProcessor
from new_year.variadic_discount import VariadicDiscount
from skeletons.gui.shared import IItemsCache
from gui.shared.utils import decorators
from skeletons.new_year import INewYearController

class NYSelectVehicleForDiscountPopover(VehicleSelectorBase, NYSelectVehiclePopoverMeta):
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, ctx=None):
        VehicleSelectorBase.__init__(self)
        NYSelectVehiclePopoverMeta.__init__(self)
        data = ctx.get('data')
        discountID = data.get('variadicID')
        self.__parentWindow = data.get('parentWindow')
        self.__variadicDiscount = VariadicDiscount(discountID)
        self.__vehiclesByDiscount = self.__variadicDiscount.getVehiclesByDiscount()
        self._levelsRange = [self.__variadicDiscount.getTankLevel()]
        self._compatibleOnlyLabel = backport.text(R.strings.ny.applyDiscountWindow.compatibleCheckBox.label())

    def applyFilters(self, nation, vehicleType, level):
        self._updateFilter(nation, vehicleType, False, level)
        self.__updateData()

    def onSelectVehicle(self, vehicleCD):
        self.__onSelectVehicle(vehicleCD)
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(NYSelectVehicleForDiscountPopover, self)._populate()
        self.__vehicleDP = NySelectVehiclePopoverDataProvider()
        self.__vehicleDP.setFlashObject(self.as_getDPS())
        self.__itemsCache.onSyncCompleted += self.__onResync
        self.__initControls()
        self.__updateData()

    def _dispose(self):
        self.__itemsCache.onSyncCompleted -= self.__onResync
        self.__vehicleDP.fini()
        self.__vehicleDP = None
        super(NYSelectVehicleForDiscountPopover, self)._dispose()
        return

    def _makeVehicleVOAction(self, vehicle):
        return makeVehicleBasicVO(vehicle)

    def __onResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.INVENTORY_RESYNC or GUI_ITEM_TYPE.VEHICLE in diff:
            self.__vehicleDP.clear()
            self.__updateData()

    def __initControls(self):
        headers = [packHeaderColumnData('nations', 49, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_NATION, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, enabled=True), packHeaderColumnData('type', 45, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHTYPE, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, enabled=True), packHeaderColumnData('name', 148, 40, label=DIALOGS.TRADEINPOPOVER_SORTING_VEHNAME_HEADER, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHNAME, enabled=True, verticalTextAlign='center')]
        levelStr = formatRomanNumber(self.__variadicDiscount.getTankLevel())
        discountStr = str(self.__variadicDiscount.getDiscountValue())
        title = backport.text(R.strings.ny.applyDiscountWindow.title(), level=levelStr)
        description = backport.text(R.strings.ny.applyDiscountWindow.infoText(), level=levelStr, discount=discountStr)
        self.as_setInitDataS({'title': title,
         'description': description,
         'tableHeaders': headers,
         'filters': self.__initFilters()})

    def __initFilters(self):
        filters = self._initFilter(nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        return filters

    def __updateData(self):
        allVehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__vehiclesByDiscount.keys()) | ~REQ_CRITERIA.INVENTORY)
        vehicles = self._updateData(allVehicles, compatiblePredicate=lambda vo: vo['isUnlocked'])
        self.__vehicleDP.buildList(vehicles)

    @decorators.adisp_process('newYear/applyVehicleDiscount')
    def __onSelectVehicle(self, vehicleCD):
        vehicle = self.__itemsCache.items.getItemByCD(int(vehicleCD))
        goodiesID = self.__vehiclesByDiscount[vehicle.intCD]
        discountID = self.__variadicDiscount.getID()
        discountValue = self.__variadicDiscount.getDiscountValue()
        confirmKwargs = {'parent': self.__parentWindow,
         'vehicle': vehicle,
         'discountValue': discountValue,
         'goodiesID': goodiesID,
         'discountID': discountID}
        result = yield ApplyVehicleDiscountProcessor(**confirmKwargs).request()
        if result is None:
            return
        else:
            if result.success:
                SystemMessages.pushMessage(backport.text(R.strings.system_messages.newYear.applyVehicleDiscount.success(), discount=discountValue, vehName=vehicle.userName), priority=NotificationPriorityLevel.MEDIUM, type=result.sysMsgType)
            elif result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType, priority=result.msgPriority)
            return
