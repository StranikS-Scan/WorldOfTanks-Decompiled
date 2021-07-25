# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PerksPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PerksPanelMeta(BaseDAAPIComponent):

    def onMinimizedChanged(self, isMinimized):
        self._printOverrideError('onMinimizedChanged')

    def as_initS(self, items):
        return self.flashObject.as_init(items) if self._isDAAPIInited() else None

    def as_updatePerkS(self, perkId, state, stacks, isUltimate, duration, lifeTime):
        return self.flashObject.as_updatePerk(perkId, state, stacks, isUltimate, duration, lifeTime) if self._isDAAPIInited() else None

    def as_clearPanelS(self):
        return self.flashObject.as_clearPanel() if self._isDAAPIInited() else None
