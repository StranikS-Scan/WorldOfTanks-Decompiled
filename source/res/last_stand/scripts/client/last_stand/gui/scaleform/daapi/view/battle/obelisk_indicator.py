# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/obelisk_indicator.py
from __future__ import absolute_import
from LSObeliskInfoComponent import LSObeliskInfoComponent, ObeliskInfoStates
from last_stand.gui.scaleform.daapi.view.meta.ObeliskMeta import ObeliskMeta

class LSObeliskIndicator(ObeliskMeta):

    def _populate(self):
        super(LSObeliskIndicator, self)._populate()
        component = LSObeliskInfoComponent.getInstance()
        if component is not None:
            component.onStateChange += self._onStateChange
            if component.isPresent:
                self.as_setStateS(ObeliskInfoStates.SHOW)
        return

    def _dispose(self):
        component = LSObeliskInfoComponent.getInstance()
        if component is not None:
            component.onStateChange -= self._onStateChange
        super(LSObeliskIndicator, self)._dispose()
        return

    def _onStateChange(self, state):
        self.as_setStateS(state)
