# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehModulesConfiguratorCmpMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehModulesConfiguratorCmpMeta(BaseDAAPIComponent):

    def onClick(self, intCD, columnIdx, moduleIdx):
        self._printOverrideError('onClick')

    def as_setItemsS(self, items):
        return self.flashObject.as_setItems(items) if self._isDAAPIInited() else None

    def as_updateItemsS(self, items):
        return self.flashObject.as_updateItems(items) if self._isDAAPIInited() else None
