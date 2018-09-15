# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYDecorationsPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class NYDecorationsPopoverMeta(SmartPopOverView):

    def onSlotClick(self, toyId, index):
        self._printOverrideError('onSlotClick')

    def goToTasks(self):
        self._printOverrideError('goToTasks')

    def onHideNew(self, toyId, index):
        self._printOverrideError('onHideNew')

    def onResetFilterClick(self):
        self._printOverrideError('onResetFilterClick')

    def onFilterChange(self, level, nation):
        self._printOverrideError('onFilterChange')

    def as_initFilterS(self, settingsData):
        """
        :param settingsData: Represented by Array (AS)
        """
        return self.flashObject.as_initFilter(settingsData) if self._isDAAPIInited() else None

    def as_setDataS(self, data, isInit):
        """
        :param data: Represented by NYDecorationsPopoverVO (AS)
        """
        return self.flashObject.as_setData(data, isInit) if self._isDAAPIInited() else None

    def as_setupS(self, arrowDirection):
        return self.flashObject.as_setup(arrowDirection) if self._isDAAPIInited() else None

    def as_breakToyS(self, index):
        return self.flashObject.as_breakToy(index) if self._isDAAPIInited() else None

    def as_breakToyFailS(self):
        return self.flashObject.as_breakToyFail() if self._isDAAPIInited() else None

    def as_breakToyStartS(self):
        return self.flashObject.as_breakToyStart() if self._isDAAPIInited() else None
