# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FittingSelectPopoverMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FittingSelectPopoverMeta(SmartPopOverView):

    def setVehicleModule(self, newId, oldId, isRemove):
        self._printOverrideError('setVehicleModule')

    def showModuleInfo(self, moduleId):
        self._printOverrideError('showModuleInfo')

    def setAutoRearm(self, autoRearm):
        self._printOverrideError('setAutoRearm')

    def buyVehicleModule(self, moduleId):
        self._printOverrideError('buyVehicleModule')

    def setCurrentTab(self, tabIndex):
        self._printOverrideError('setCurrentTab')

    def listOverlayClosed(self):
        self._printOverrideError('listOverlayClosed')

    def as_updateS(self, data):
        """
        :param data: Represented by FittingSelectPopoverVO (AS)
        """
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None
