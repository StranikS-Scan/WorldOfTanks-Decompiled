# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AmmunitionPanelInjectMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class AmmunitionPanelInjectMeta(InjectComponentAdaptor):

    def onHangarSwitchAnimComplete(self, isComplete):
        self._printOverrideError('onHangarSwitchAnimComplete')

    def as_setPanelSizeS(self, panelWidth, panelHeight, offsetY):
        return self.flashObject.as_setPanelSize(panelWidth, panelHeight, offsetY) if self._isDAAPIInited() else None

    def as_setHelpLayoutS(self, helpLayoutData):
        return self.flashObject.as_setHelpLayout(helpLayoutData) if self._isDAAPIInited() else None

    def as_clearHelpLayoutS(self):
        return self.flashObject.as_clearHelpLayout() if self._isDAAPIInited() else None
