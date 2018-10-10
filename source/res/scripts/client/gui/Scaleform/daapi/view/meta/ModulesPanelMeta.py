# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ModulesPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ModulesPanelMeta(BaseDAAPIComponent):

    def showModuleInfo(self, moduleId):
        self._printOverrideError('showModuleInfo')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setVehicleHasTurretS(self, hasTurret):
        return self.flashObject.as_setVehicleHasTurret(hasTurret) if self._isDAAPIInited() else None

    def as_setModulesEnabledS(self, value):
        return self.flashObject.as_setModulesEnabled(value) if self._isDAAPIInited() else None
