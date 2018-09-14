# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RosterSlotSettingsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class RosterSlotSettingsWindowMeta(AbstractWindowView):

    def onFiltersUpdate(self, nation, vehicleType, isMain, level, compatibleOnly):
        self._printOverrideError('onFiltersUpdate')

    def getFilterData(self):
        self._printOverrideError('getFilterData')

    def submitButtonHandler(self, value):
        self._printOverrideError('submitButtonHandler')

    def cancelButtonHandler(self):
        self._printOverrideError('cancelButtonHandler')

    def as_setDefaultDataS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setDefaultData(value)

    def as_setListDataS(self, listData):
        if self._isDAAPIInited():
            return self.flashObject.as_setListData(listData)
