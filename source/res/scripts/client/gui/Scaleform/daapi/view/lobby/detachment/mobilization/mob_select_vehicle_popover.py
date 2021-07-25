# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/detachment/mobilization/mob_select_vehicle_popover.py
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.meta.MobilizationVehicleSelectPopoverMeta import MobilizationVehicleSelectPopoverMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.impl import backport
from gui.impl.auxiliary.detachmnet_convert_helper import isBarracksNotEmpty
from gui.impl.gen import R
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getSmallIconPath, getTypeSmallIconPath
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from nations import INDICES, ALL_NATIONS_INDEX
from skeletons.gui.shared import IItemsCache

def _makeVehicleCmpVO(vehicle):
    return {'dbID': vehicle.intCD,
     'level': vehicle.level,
     'shortUserName': vehicle.shortUserName,
     'smallIconPath': getSmallIconPath(vehicle.name),
     'nationID': vehicle.nationID,
     'type': vehicle.type,
     'typeIcon': getTypeSmallIconPath(vehicle.type, vehicle.isPremium),
     'selected': False,
     'inHangar': vehicle.isInInventory}


defaultFilters = {'nation': -1,
 'vehicleType': 'none',
 'isMain': False,
 'level': -1,
 'compatibleOnly': True}

class MobilizationSelectVehiclePopover(MobilizationVehicleSelectPopoverMeta, VehicleSelectorBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(MobilizationSelectVehiclePopover, self).__init__(ctx)
        self._searchStr = ''
        self._totalVehicles = 0

    def onResetButtonClick(self):
        self.applyFilters(defaultFilters['nation'], defaultFilters['vehicleType'], defaultFilters['level'], defaultFilters['isMain'], defaultFilters['compatibleOnly'])
        self._initControls()

    def onSearchInputChange(self, inputText):
        self._searchStr = inputText
        self.updateData()

    def applyFilters(self, nation, vehicleType, level, isMain, hangarOnly):
        self._updateFilter(nation, vehicleType, isMain, level, hangarOnly)
        self.updateData()

    def updateData(self):
        criteria = self._getBaseCriteria()
        if not self._totalVehicles:
            self._totalVehicles = len(self.itemsCache.items.getVehicles(criteria))
        criteria |= REQ_CRITERIA.VEHICLE.NAME_VEHICLE(self._searchStr)
        allVehicles = self.itemsCache.items.getVehicles(criteria)
        vehicles = self._updateData(allVehicles, compatiblePredicate=lambda vo: vo['inHangar'])
        self._vehDP.buildList(vehicles)
        self._updateSortField()
        self.as_updateFilterStatusS({'current': len(vehicles),
         'total': self._totalVehicles})

    def setVehicleSelected(self, dbID, autoClose):
        self.fireEvent(events.DetachmentViewEvent(events.DetachmentViewEvent.VEHICLE_SELECTED, ctx={'vehicleId': dbID}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.onWindowClose()

    def addButtonClicked(self):
        pass

    def _populate(self):
        super(MobilizationSelectVehiclePopover, self)._populate()
        self._initControls()
        self._initDP()
        self.updateData()

    def _getBaseCriteria(self):
        criteria = REQ_CRITERIA.EMPTY
        criteria |= REQ_CRITERIA.VEHICLE.ACTIVE_OR_MAIN_IN_NATION_GROUP ^ REQ_CRITERIA.VEHICLE.INACTIVE_IN_NATION_GROUP
        criteria |= ~REQ_CRITERIA.VEHICLE.EXPIRED_IGR_RENT
        criteria |= ~REQ_CRITERIA.VEHICLE.DISABLED_IN_PREM_IGR
        criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        criteria |= REQ_CRITERIA.INVENTORY ^ ~REQ_CRITERIA.VEHICLE.SECRET
        criteria ^= REQ_CRITERIA.VEHICLE.INACTIVE_IN_NATION_GROUP
        availableNations = [ nationID for nationID in INDICES.itervalues() if isBarracksNotEmpty(nationID) ]
        criteria |= REQ_CRITERIA.INVENTORY ^ ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        criteria |= ~REQ_CRITERIA.VEHICLE.HAS_DETACHMENT ^ ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        criteria |= REQ_CRITERIA.NATIONS(availableNations) ^ REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        return criteria

    def _makeVehicleVOAction(self, vehicle):
        return _makeVehicleCmpVO(vehicle)

    def _initControls(self):
        common = {'btnHeight': 34,
         'enabled': True}
        headers = [packHeaderColumnData('nations', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_NATION, **common),
         packHeaderColumnData('type', 45, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TYPE, **common),
         packHeaderColumnData('level', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_LEVEL, **common),
         packHeaderColumnData('name', 140, label=VEH_COMPARE.ADDVEHPOPOVER_VEHICLENAME, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TITLE, direction='ascending', **common),
         packHeaderColumnData('hangar', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_ICON_TABLE_COMPARISON_INHANGAR, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_INHANGAR, **common)]
        self.as_setInitDataS({'tableHeaders': headers,
         'filters': self.__initFilters(),
         'header': text_styles.highTitle(backport.text(R.strings.detachment.mobilizationPopover.header()))})

    def __initFilters(self):
        filters = self._initFilter(nation=defaultFilters['nation'], vehicleType=defaultFilters['vehicleType'], isMain=defaultFilters['isMain'], level=defaultFilters['level'], compatibleOnly=defaultFilters['compatibleOnly'])
        availableNations = [ nationID for nationID in INDICES.itervalues() if isBarracksNotEmpty(nationID, excludeLockedCrew=False) ]
        availableNations.append(ALL_NATIONS_INDEX)
        filters['nationDP'] = [ nation for nation in filters['nationDP'] if nation['data'] in availableNations ]
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        filters.update({'compatibleOnlyLabel': VEH_COMPARE.ADDVEHPOPOVER_SHOWONLYMYVAHICLES})
        return filters
