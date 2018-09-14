# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/RosterSlotSettingsWindow.py
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.daapi.view.lobby.cyberSport.VehicleSelectorBase import VehicleSelectorBase
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.meta.RosterSlotSettingsWindowMeta import RosterSlotSettingsWindowMeta
from gui.shared.ItemsCache import g_itemsCache, REQ_CRITERIA
from gui.shared.events import CSRosterSlotSettingsWindow

class RosterSlotSettingsWindow(RosterSlotSettingsWindowMeta, VehicleSelectorBase):

    def __init__(self, ctx = None):
        super(RosterSlotSettingsWindow, self).__init__()
        raise 'section' in ctx or AssertionError('Section is required to show selector popup')
        self.__section = ctx.get('section')
        self.__levelsRange = ctx.get('levelsRange', (1, 10))
        self.__vehicleTypes = ctx.get('vehicleTypes', None)
        self.currentSlot = self.__makeInitialSlotData(ctx.get('settings'))
        return

    def _getLevelsRange(self):
        return [0] + self.__levelsRange

    def _populate(self):
        super(RosterSlotSettingsWindow, self)._populate()
        self.as_setDefaultDataS(self.currentSlot)
        self.slotSettings = None
        return

    def updateSlots(self, slots):
        self.as_setDefaultDataS(slots)

    def onFiltersUpdate(self, nation, vehicleType, isMain, level, compatibleOnly):
        self._updateFilter(nation, vehicleType, isMain, level, compatibleOnly)
        self.updateData()

    def updateData(self):
        result = self._updateData(g_itemsCache.items.getVehicles(~REQ_CRITERIA.SECRET), self.__levelsRange, self.__vehicleTypes, isVehicleRoster=True)
        self.as_setListDataS(result)

    def getFilterData(self):
        filters = AccountSettings.getFilter(self.__section)
        filters['isMain'] = False
        result = self._initFilter(**filters)
        return result

    def submitButtonHandler(self, value):
        self.currentSlot = self.__makeCurrentSlotData(value)
        self.fireEvent(CSRosterSlotSettingsWindow(CSRosterSlotSettingsWindow.APPLY_SLOT_SETTINGS, self.currentSlot))
        self.onWindowClose()

    def __makeInitialSlotData(self, slotSettings):
        if slotSettings[2] is None:
            levels = list(self.__levelsRange)
            slotSettings[2] = {'nationIDRange': [],
             'vTypeRange': [],
             'vLevelRange': levels[::len(levels) - 1]}
            return slotSettings
        else:
            return self.__makeCurrentSlotData(slotSettings)

    def __makeCurrentSlotData(self, value):
        currentSlot = [value[0], value[1]]
        data = value[2]
        if isinstance(data, long):
            currentSlot.append(makeVehicleVO(g_itemsCache.items.getItemByCD(int(data)), self.__levelsRange, self.__vehicleTypes))
        elif data is not None:
            if len(data.nationIDRange) == 0 and len(data.vTypeRange) == 0 and len(data.vLevelRange) == 0:
                currentSlot.append(None)
            else:
                currentSlot.append({'nationIDRange': data.nationIDRange,
                 'vTypeRange': data.vTypeRange,
                 'vLevelRange': data.vLevelRange})
        else:
            currentSlot.append(None)
        return currentSlot

    def cancelButtonHandler(self):
        self.onWindowClose()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        currentFilters = self.getFilters()
        if currentFilters:
            filters = {'nation': currentFilters['nation'],
             'vehicleType': currentFilters['vehicleType'],
             'isMain': currentFilters['isMain'],
             'level': currentFilters['level'],
             'compatibleOnly': currentFilters['compatibleOnly']}
            AccountSettings.setFilter(self.__section, filters)
        super(RosterSlotSettingsWindow, self)._dispose()
        self.currentSlot = None
        self.slotSettings = None
        return
