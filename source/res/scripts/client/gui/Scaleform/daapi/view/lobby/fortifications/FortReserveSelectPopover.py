# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortReserveSelectPopover.py
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.meta.FittingSelectPopoverMeta import FittingSelectPopoverMeta
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.prb_control.entities.base.unit.listener import IUnitListener
from gui.shared.events import CSReserveSelectEvent
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

        bonusPersent = '+%d%%' % reserve.getBonusPercent()
        moduleData = vo_converters.makeReserveModuleData(reserve.getId(), reserve.getType(), reserve.getLevel(), str(count), isSelected, bonusPersent, reserve.getDescription())
        return moduleData

    def __getReserveGroup(self):
        entity = self.prbEntity
        if entity is None:
            return
        else:
            order = entity.getStrongholdSettings().getReserveOrder()
            groupType = order[self._slotIndex]
            return vo_converters.getReserveGroupTitle(groupType)

    def __buildList(self):
        entity = self.prbEntity
        if entity is None:
            return
        else:
            selectedIdxs = entity.getStrongholdSettings().getReserve().getSelectedReserves()
            order = entity.getStrongholdSettings().getReserveOrder()
            groupType = order[self._slotIndex]
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
