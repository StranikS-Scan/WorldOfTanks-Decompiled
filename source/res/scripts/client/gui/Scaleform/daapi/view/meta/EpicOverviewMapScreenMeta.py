# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicOverviewMapScreenMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicOverviewMapScreenMeta(BaseDAAPIComponent):

    def as_setKeyBindingsS(self, data):
        return self.flashObject.as_setKeyBindings(data) if self._isDAAPIInited() else None

    def as_updateLaneButtonNamesS(self, west, center, east):
        return self.flashObject.as_updateLaneButtonNames(west, center, east) if self._isDAAPIInited() else None
