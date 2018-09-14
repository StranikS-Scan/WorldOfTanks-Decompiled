# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortReserveSelectPopover.py
import BigWorld
import itertools
from gui.shared.events import CSReserveSelectEvent
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.meta.FittingSelectPopoverMeta import FittingSelectPopoverMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.entities.base.unit.listener import IUnitListener
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared.formatters import text_styles

class FortReserveSelectPopover(FittingSelectPopoverMeta, IUnitListener):

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

    def __getStrongholdData(self):
        entity = self.prbEntity
        if entity is None:
            return
        else:
            data = entity.getStrongholdData()
            return data

    def __buildModuleData(self, selectedIdxs, reserve, count):
        isSelected = next(itertools.ifilter(lambda id: reserve.getId() == id, selectedIdxs), None) is not None
        if isSelected:
            count -= 1
        bonusPersent = '+%d%%' % reserve.getBonusPercent()
        moduleData = vo_converters.makeReserveModuleData(reserve.getId(), reserve.getType(), reserve.getLevel(), str(count), isSelected, bonusPersent, reserve.getDescription())
        return moduleData

    def __getReserveGroup(self):
        data = self.__getStrongholdData()
        order = data.getReserveOrder()
        groupType = order[self._slotIndex]
        return vo_converters.getReserveGroupTitle(groupType)

    def __buildList(self):
        data = self.__getStrongholdData()
        if data is None:
            return
        else:
            selectedIdxs = data.getSelectedReservesIdx()
            order = data.getReserveOrder()
            groupType = order[self._slotIndex]
            modulesList = []
            group = data.getUniqueReservesByGroupType(groupType)
            for i, reserve in enumerate(group):
                count = data.getReserveCount(reserve.getType(), reserve.getLevel())
                moduleData = self.__buildModuleData(selectedIdxs, reserve, count)
                if moduleData.get('isSelected', None):
                    self._selectedIndex = i
                modulesList.append(moduleData)

            return modulesList
