# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleVehicleConfiguratorMeta.py
from gui.Scaleform.framework.entities.View import View

class BattleVehicleConfiguratorMeta(View):

    def onModuleMouseOver(self, intCD):
        self._printOverrideError('onModuleMouseOver')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setVisibleS(self, isVisible):
        return self.flashObject.as_setVisible(isVisible) if self._isDAAPIInited() else None

    def as_updateModuleInfoPanelS(self, data):
        return self.flashObject.as_updateModuleInfoPanel(data) if self._isDAAPIInited() else None

    def as_updateChoiceInfoPanelS(self, data):
        return self.flashObject.as_updateChoiceInfoPanel(data) if self._isDAAPIInited() else None
