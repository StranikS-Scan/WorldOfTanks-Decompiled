# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePreviewBrowseTabMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehiclePreviewBrowseTabMeta(BaseDAAPIComponent):

    def setActiveState(self, isActive):
        self._printOverrideError('setActiveState')

    def as_setDataS(self, historicReferenceTxt, showTooltip, bonuses):
        return self.flashObject.as_setData(historicReferenceTxt, showTooltip, bonuses) if self._isDAAPIInited() else None
