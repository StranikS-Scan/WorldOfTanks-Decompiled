# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PrebattleAmmunitionPanelViewMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class PrebattleAmmunitionPanelViewMeta(InjectComponentAdaptor):

    def onViewIsHidden(self):
        self._printOverrideError('onViewIsHidden')

    def as_hideS(self, useAnim):
        return self.flashObject.as_hide(useAnim) if self._isDAAPIInited() else None
