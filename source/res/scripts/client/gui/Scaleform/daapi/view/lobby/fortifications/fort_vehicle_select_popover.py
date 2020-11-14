# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_vehicle_select_popover.py
from gui import makeHtmlString
from gui.Scaleform import MENU
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.meta.FortVehicleSelectPopoverMeta import FortVehicleSelectPopoverMeta
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.prb_control.entities.base.unit.listener import IUnitListener
from gui.shared.events import CSVehicleSelectEvent, StrongholdEvent
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, getSmallIconPath, Vehicle, getTypeSmallIconPath
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString
from skeletons.gui.shared import IItemsCache
_IGNORED_VEHICLE_STATES = (Vehicle.VEHICLE_STATE.UNDAMAGED, Vehicle.VEHICLE_STATE.IN_PREBATTLE, Vehicle.GROUP_STATES)

def convertState(vState):
    if vState in _IGNORED_VEHICLE_STATES:
        return ''
    return makeHtmlString('html_templates:lobby', 'inPremiumIgrOnly') if vState == Vehicle.VEHICLE_STATE.IN_PREMIUM_IGR_ONLY else makeString(MENU.tankcarousel_vehiclestates(vState))


def getVehicleCriteria(levelsRange, inHangar=False):
    req = REQ_CRITERIA.VEHICLE.LEVELS(levelsRange) | ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    if inHangar:
        req |= REQ_CRITERIA.INVENTORY
    return req


class FortVehicleSelectPopover(FortVehicleSelectPopoverMeta, VehicleSelectorBase, IUnitListener):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(FortVehicleSelectPopover, self).__init__(ctx)
        self._classFilters = None
        data = ctx.get('data', None)
        self._showMainBtn = data.showMainBtn
        self._slotIndex = data.slotIndex
        self._levelsRange = data.levelsRange
        self._selectedVehicles = data.selectedVehicles
        return

    def setVehicleSelected(self, dbID, autoClose):
        super(FortVehicleSelectPopover, self).setVehicleSelected(dbID, autoClose)
        if not autoClose:
            self.updateAddButtonLabel()

    def updateAddButtonLabel(self):
        selectedCount = len(self._vehDP.getSelected())
        buttonState = {'btnEnabled': selectedCount > 0}
        if self._isMultiSelect:
            buttonState['btnLabel'] = makeString(FORTIFICATIONS.FORTVEHPOPOVER_BTNSAVE, count=selectedCount)
        else:
            buttonState['btnLabel'] = makeString(CYBERSPORT.WINDOW_ROSTERSLOTSETTINGS_VEHICLETAB_SUBMITBTN)
        self.as_setAddButtonStateS(buttonState)

    def applyFilters(self, nation, vehicleType, level, isMain, hangarOnly):
        self._updateFilter(nation, vehicleType, isMain, level, hangarOnly)
        self.updateData()

    def onFilterChange(self, index, value):
        self._classFilters[index] = value
        self.updateData()

    def initFilters(self):
        self._classFilters = [ False for _ in VEHICLE_TYPES_ORDER ]
        filters = self._initFilter()
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        return filters

    def updateData(self):
        vehicleCriteria = getVehicleCriteria(levelsRange=self._levelsRange, inHangar=not self._isMultiSelect)
        vehicles = self._updateData(self.itemsCache.items.getVehicles(vehicleCriteria), compatiblePredicate=lambda vo: vo['inHangar'])
        self._vehDP.buildList(vehicles)
        self._updateSortField()

    def addButtonClicked(self):
        vehicles = self._vehDP.getSelected()
        if not self._isMultiSelect:
            self.fireEvent(CSVehicleSelectEvent(CSVehicleSelectEvent.VEHICLE_SELECTED, list(vehicles)))
        else:
            self.fireEvent(StrongholdEvent(StrongholdEvent.STRONGHOLD_VEHICLES_SELECTED, {'items': list(vehicles),
             'slotIndex': self._slotIndex}))
        self.onWindowClose()

    def _populate(self):
        super(FortVehicleSelectPopover, self)._populate()
        self.__initControls()
        self._initDP()
        self.updateData()
        self.updateAddButtonLabel()

    def _getHeader(self):
        return FORTIFICATIONS.STRONGHOLDPOPOVER_COMMANDERHEADER if self._isMultiSelect else FORTIFICATIONS.STRONGHOLDPOPOVER_HEADER

    def _parseFilters(self):
        nations, _, _ = super(FortVehicleSelectPopover, self)._parseFilters()
        classes = [ VEHICLE_TYPES_ORDER[i] for i, v in enumerate(self._classFilters) if v ]
        if not classes:
            classes = list(VEHICLE_TYPES_ORDER)
        return (nations, None, classes)

    def _initFilter(self, nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False):
        filtersData = super(FortVehicleSelectPopover, self)._initFilter(nation, vehicleType, isMain, level, compatibleOnly)
        filtersData['togglesDP'] = self.__createFilterToggles()
        filtersData['nationTooltip'] = makeTooltip(MENU.NATIONS_TITLE, TOOLTIPS.VEHICLESELECTOR_FILTER_NATION)
        if self._showMainBtn:
            entry = 'favorite'
            filtersData['mainBtn'] = {'value': getButtonsAssetPath(entry),
             'tooltip': makeTooltip('#tank_carousel_filter:tooltip/{}/header'.format(entry), makeString('#tank_carousel_filter:tooltip/{}/body'.format(entry))),
             'selected': False}
        return filtersData

    def _dispose(self):
        super(FortVehicleSelectPopover, self)._dispose()
        self._classFilters = None
        return

    def _makeVehicleVOAction(self, vehicle):
        if self._selectedVehicles:
            checkSelectedFunc = self._isSelected
        else:
            checkSelectedFunc = lambda vo: False
        vState, _ = vehicle.getState()
        return {'dbID': vehicle.intCD,
         'level': vehicle.level,
         'shortUserName': vehicle.shortUserName,
         'smallIconPath': getSmallIconPath(vehicle.name),
         'nationID': vehicle.nationID,
         'type': vehicle.type,
         'typeIcon': getTypeSmallIconPath(vehicle.type, vehicle.isPremium),
         'selected': checkSelectedFunc(vehicle),
         'inHangar': False,
         'isMultiSelect': self._isMultiSelect,
         'isReadyToFight': vehicle.isReadyToFight,
         'enabled': vehicle.isReadyToFight,
         'tooltip': makeTooltip('#tooltips:vehicleStatus/%s/header' % vState, '#tooltips:vehicleStatus/body'),
         'state': convertState(vState)}

    def _isSelected(self, entry):
        return entry.intCD in self._selectedVehicles

    def __initControls(self):
        common = {'btnHeight': 34,
         'enabled': True}
        nameWidth = 200 if self._isMultiSelect else 245
        headers = [packHeaderColumnData('nations', 43, icon=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_NATION, **common),
         packHeaderColumnData('type', 33, icon=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TYPE, **common),
         packHeaderColumnData('level', 33, icon=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_LEVEL, btnHeight=34, enabled=False),
         packHeaderColumnData('name', nameWidth, label=VEH_COMPARE.ADDVEHPOPOVER_VEHICLENAME, tooltip=VEH_COMPARE.ADDVEHPOPOVER_TOOLTIPS_TITLE, direction='ascending', **common)]
        if self._isMultiSelect:
            headers.insert(0, packHeaderColumnData('check', 45, icon=RES_ICONS.MAPS_ICONS_BUTTONS_ICON_TABLE_COMPARISON_CHECKMARK, **common))
        self.as_setInitDataS({'tableHeaders': headers,
         'filters': self.initFilters(),
         'header': text_styles.highTitle(makeString(self._getHeader())),
         'btnCancel': VEH_COMPARE.ADDVEHPOPOVER_BTNCANCEL,
         'isMultiSelect': self._isMultiSelect})

    def __getAssetPath(self, assetType, extension='.png'):
        return ''.join(['../maps/icons/filters/tanks/', assetType, extension])

    def __createFilterToggles(self):
        filterToggles = []
        for entry in VEHICLE_TYPES_ORDER:
            filterToggles.append({'value': self.__getAssetPath(entry),
             'tooltip': makeTooltip('#menu:carousel_tank_filter/{}'.format(entry), '#tank_carousel_filter:tooltip/vehicleTypes/body'),
             'selected': False})

        return filterToggles
