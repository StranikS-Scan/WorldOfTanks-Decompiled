# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_select_vehicle_popover.py
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleBasicVO
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.meta.NYSelectVehiclePopoverMeta import NYSelectVehiclePopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.requesters.ItemsRequester import RESEARCH_CRITERIA
from helpers import dependency
from new_year.vehicle_branch import SetVehicleBranchProcessor
from new_year.vehicle_branch_helpers import getAvailableVehicleRange
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
_INACCESSIBLE_FOR_TRADE_STATES = (Vehicle.VEHICLE_STATE.DAMAGED,
 Vehicle.VEHICLE_STATE.EXPLODED,
 Vehicle.VEHICLE_STATE.DESTROYED,
 Vehicle.VEHICLE_STATE.BATTLE,
 Vehicle.VEHICLE_STATE.IN_PREBATTLE,
 Vehicle.VEHICLE_STATE.LOCKED,
 Vehicle.VEHICLE_STATE.DISABLED)

class NySelectVehiclePopover(VehicleSelectorBase, NYSelectVehiclePopoverMeta):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, ctx=None):
        VehicleSelectorBase.__init__(self)
        NYSelectVehiclePopoverMeta.__init__(self)
        data = ctx['data']
        slotID = int(data.get('slotID'))
        self.__slot = self._nyController.getVehicleBranch().getVehicleSlots()[slotID]
        self._levelsRange = getAvailableVehicleRange()

    def initFilters(self):
        filters = self._initFilter(nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        return filters

    def applyFilters(self, nation, vehicleType, level):
        self._updateFilter(nation, vehicleType, False, level)
        self.__updateData()

    def onWindowClose(self):
        self.destroy()

    def onSelectVehicle(self, vehicleCD):
        vehicle = self._itemsCache.items.getItemByCD(int(vehicleCD))
        if vehicle is not None and vehicle.isInInventory:
            self.__setVehicleSlot(vehicle.invID)
        return

    def _populate(self):
        super(NySelectVehiclePopover, self)._populate()
        self.__vehicleDP = NySelectVehiclePopoverDataProvider()
        self.__vehicleDP.setFlashObject(self.as_getDPS())
        self._itemsCache.onSyncCompleted += self.__onResync
        self.__initControls()
        self.__updateData()

    def _dispose(self):
        self._itemsCache.onSyncCompleted -= self.__onResync
        self.__vehicleDP.fini()
        self.__vehicleDP = None
        super(NySelectVehiclePopover, self)._dispose()
        return

    def _makeVehicleVOAction(self, vehicle):
        return makeVehicleBasicVO(vehicle)

    def __initControls(self):
        headers = [packHeaderColumnData('nationID', 40, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_NATION, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, enabled=True),
         packHeaderColumnData('typeIndex', 40, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHTYPE, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, enabled=True),
         packHeaderColumnData('level', 40, 40, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHLVL, icon=RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_ALL, enabled=True),
         packHeaderColumnData('shortUserName', 152, 40, label=DIALOGS.TRADEINPOPOVER_SORTING_VEHNAME_HEADER, tooltip=DIALOGS.TRADEINPOPOVER_SORTING_VEHNAME, enabled=True, verticalTextAlign='center', showSeparator=False)]
        if not self._nyController.isPostEvent():
            description = ''
            cooldown = self.__slot.getDefaultSlotCooldown()
            if cooldown > 0:
                timeLeft = backport.getTillTimeStringByRClass(cooldown, R.strings.menu.Time.timeValueShort)
                description = backport.text(R.strings.ny.vehiclesView.selectVehiclePopover.description(), time=text_styles.stats(timeLeft))
        else:
            description = backport.text(R.strings.ny.vehiclesView.selectVehiclePopover.postEvent.description())
        self.as_setInitDataS({'title': backport.text(R.strings.ny.vehiclesView.selectVehiclePopover.header(), level=self.__slot.getLevelStr()),
         'description': description,
         'defaultSortField': 'level',
         'defaultSortDirection': 'descending',
         'tableHeaders': headers,
         'filters': self.initFilters()})

    def __onResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC or GUI_ITEM_TYPE.VEHICLE in diff:
            self.__vehicleDP.clear()
            self.__updateData()

    def __updateData(self):
        allVehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(self._levelsRange) | ~REQ_CRITERIA.VEHICLE.IS_IN_BATTLE | ~REQ_CRITERIA.VEHICLE.IS_IN_UNIT | ~REQ_CRITERIA.VEHICLE.RENT | RESEARCH_CRITERIA.VEHICLE_TO_UNLOCK ^ (REQ_CRITERIA.VEHICLE.PREMIUM | REQ_CRITERIA.VEHICLE.SPECIAL))
        for slot in self._nyController.getVehicleBranch().getVehicleSlots():
            vehicle = slot.getVehicle()
            if vehicle is not None and vehicle.intCD in allVehicles:
                del allVehicles[vehicle.intCD]

        vehicles = self._updateData(allVehicles, compatiblePredicate=lambda vo: vo['inHangar'])
        self.__vehicleDP.buildList(vehicles)
        return

    @decorators.process('newYear/setVehicleBranch')
    def __setVehicleSlot(self, invID):
        self.onWindowClose()
        result = yield SetVehicleBranchProcessor(invID, self.__slot.getSlotID()).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.TANKS_SET)


class NySelectVehiclePopoverDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(NySelectVehiclePopoverDataProvider, self).__init__()
        self.__list = []
        self.__mapping = {}
        self.__selectedID = None
        return

    @property
    def collection(self):
        return self.__list

    def emptyItem(self):
        return None

    def clear(self):
        self.__list = []
        self.__mapping.clear()
        self.__selectedID = None
        return

    def fini(self):
        self.clear()
        self.destroy()

    def getSelectedIdx(self):
        return self.__mapping[self.__selectedID] if self.__selectedID in self.__mapping else -1

    def setSelectedID(self, selId):
        self.__selectedID = selId

    def buildList(self, vehicleVOs):
        self.__list = vehicleVOs
        self.refresh()

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def pySortOn(self, fields, order):
        super(NySelectVehiclePopoverDataProvider, self).pySortOn(fields, order)
        self.__rebuildMapping()
        self.refresh()

    def __rebuildMapping(self):
        self.__mapping = {item['intCD']:idx for idx, item in enumerate(self.sortedCollection)}
