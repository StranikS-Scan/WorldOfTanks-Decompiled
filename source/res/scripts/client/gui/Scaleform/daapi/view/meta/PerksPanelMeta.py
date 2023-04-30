# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PerksPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PerksPanelMeta(BaseDAAPIComponent):

    def as_setPerksS(self, items):
        return self.flashObject.as_setPerks(items) if self._isDAAPIInited() else None

    def as_updatePerkS(self, perkName, state, duration, lifeTime):
        return self.flashObject.as_updatePerk(perkName, state, duration, lifeTime) if self._isDAAPIInited() else None

    def as_clearPanelS(self):
        return self.flashObject.as_clearPanel() if self._isDAAPIInited() else None
