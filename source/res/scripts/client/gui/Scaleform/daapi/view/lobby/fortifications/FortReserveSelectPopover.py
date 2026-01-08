# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortReserveSelectPopover.py
import logging
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.meta.FittingSelectPopoverMeta import FittingSelectPopoverMeta
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.unit.listener import IUnitListener
from gui.prb_control.items.stronghold_items import ARTILLERY_STRIKE, INSPIRATION, RESERVE_ITEMS, REQUISITION_TYPE
from gui.shared.events import CSReserveSelectEvent
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import params_helper, formatters
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
RESERVE_PARAMS_LIST = {ARTILLERY_STRIKE: ('maxDamage', 'areaRadius'),
 INSPIRATION: ('crewRolesFactor', 'commonAreaRadius', 'inactivationDelay')}

class FortReserveSelectPopover(FittingSelectPopoverMeta, IUnitListener):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(FortReserveSelectPopover, self).__init__(ctx)
        data = ctx.get('data')
        self._slotType = data.slotType
        self._slotIndex = data.slotIndex
        self._selectedIndex = -1

    def setVehicleModule(self, newId, oldId, isRemove):
        settings = {'newId': newId,
         'oldId': oldId,
         'isRemove': isRemove}
        self.fireEvent(CSReserveSelectEvent(CSReserveSelectEvent.RESERVE_SELECTED, settings))
        self.destroy()

    def setCurrentTab(self, tabIndex):
        pass

    def _populate(self):
        super(FortReserveSelectPopover, self)._populate()
        title = self.__getReserveGroup()
        rendererName = FITTING_TYPES.RESERVE_FITTING_ITEM_RENDERER
        rendererDataClass = FITTING_TYPES.MODULE_FITTING_RENDERER_DATA_CLASS_NAME
        width = FITTING_TYPES.RESERVE_POPOVER_WIDTH
        self.as_updateS({'title': text_styles.highTitle(title),
         'rendererName': rendererName,
         'rendererDataClass': rendererDataClass,
         'availableDevices': self.__buildList(),
         'selectedIndex': self._selectedIndex,
         'preferredLayout': 0,
         'width': width})

    def __buildModuleData(self, selectedIdxs, reserve, count):
        isSelected = False
        for selectReserve in selectedIdxs:
            if selectReserve and selectReserve.getId() == reserve.getId():
                isSelected = True
                count -= 1
                break

        showExtendedParams = reserve.getType() in RESERVE_PARAMS_LIST
        moduleData = vo_converters.makeReserveModuleData(reserve.getId(), reserve.getType(), reserve.getLevel(), str(count), isSelected, showExtendedParams, self.__buildReserveParams(reserve))
        return moduleData

    def __getReserveGroup(self):
        entity = self.prbEntity
        if entity is None:
            return
        else:
            slots = self.__getReserveOrder()
            groupType = slots[self._slotIndex]
            return vo_converters.getReserveGroupTitle(groupType)

    def __getReserveOrder(self):
        slots = []
        reserve = self.prbEntity.getStrongholdSettings().getReserve()
        reserveOrder = self.prbEntity.getStrongholdSettings().getReserveOrder()
        reserves = set(reserve.getAvailableReserves().keys())
        availableGroups = {group for group, items in RESERVE_ITEMS.items() if reserves.intersection(set(items))}
        index = 0
        for groupType in reserveOrder:
            if groupType not in availableGroups:
                continue
            slots.append(groupType)
            index += 1

        return slots

    def __updateReserve(self, groupType, reserveData, slotIndex):
        current = None
        group = reserveData.getUniqueReservesByGroupType(groupType)
        selectedReserves = reserveData.getSelectedReserves()
        for reserve in group:
            if reserve in selectedReserves:
                current = reserve
                break

        unitPermissions = self.prbEntity.getPermissions()
        havePermissions = unitPermissions.canChangeConsumables()
        slotType = None
        level = 0
        reserveId = 0
        if current:
            slotType = current.getType()
            level = current.getLevel()
            reserveId = current.getId()
        isRequisition = groupType == REQUISITION_TYPE
        disabledByRequisition = isRequisition and not self.prbEntity.isFirstBattle()
        empty = len(group) == 0
        isInBattle = self.prbEntity.getFlags().isInArena()
        enabled = havePermissions and not empty and not isInBattle and not disabledByRequisition
        tooltip, tooltipType = vo_converters.makeReserveSlotTooltipVO(current, groupType, empty, havePermissions, isInBattle, disabledByRequisition)
        vo = vo_converters.makeReserveSlotVO(slotType, groupType, reserveId, level, slotIndex, tooltip, tooltipType)
        return (vo, enabled)

    def __buildList(self):
        entity = self.prbEntity
        if entity is None:
            return
        else:
            selectedIdxs = entity.getStrongholdSettings().getReserve().getSelectedReserves()
            slots = self.__getReserveOrder()
            groupType = slots[self._slotIndex]
            modulesList = []
            reserves = entity.getStrongholdSettings().getReserve()
            group = reserves.getUniqueReservesByGroupType(groupType)
            for i, reserve in enumerate(group):
                count = reserves.getReserveCount(reserve.getType(), reserve.getLevel())
                moduleData = self.__buildModuleData(selectedIdxs, reserve, count)
                if moduleData.get('isSelected', None):
                    self._selectedIndex = i
                modulesList.append(moduleData)

            return modulesList

    def __buildReserveParams(self, reserve):
        if not reserve.isUsingInBattle():
            return [{'paramValue': '+{}%'.format(reserve.getBonusPercent()),
              'paramName': reserve.getDescription()}]
        else:
            paramsData = []
            item = self.__itemsCache.items.getItemByCD(int(reserve.intCD))
            if item is None:
                _logger.warning('There is not a reserve with intCD=%s', reserve.intCD)
                return paramsData
            paramsFilter = RESERVE_PARAMS_LIST.get(reserve.getType())
            if paramsFilter is None:
                _logger.warning('RESERVE_PARAMS_LIST does not know a reserve with type=%s', reserve.getType())
                return paramsData
            params = params_helper.getParameters(item)
            paramsResult = formatters.getFormattedParamsList(item.descriptor, params)
            for paramName, paramValue in paramsResult:
                if paramName in paramsFilter:
                    paramsStrR = R.strings.menu.moduleInfo.params.short.dyn(paramName)
                    if not paramsStrR.isValid():
                        paramsStrR = R.strings.menu.moduleInfo.params.dyn(paramName)
                    paramsData.append({'paramValue': paramValue,
                     'paramName': text_styles.concatStylesWithNBSP(text_styles.main(backport.text(paramsStrR())), text_styles.standard(formatters.measureUnitsForParameter(paramName)))})

            return paramsData
