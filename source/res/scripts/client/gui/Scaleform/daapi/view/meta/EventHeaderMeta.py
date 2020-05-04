# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventHeaderMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventHeaderMeta(BaseDAAPIComponent):

    def menuItemClick(self, alias):
        self._printOverrideError('menuItemClick')

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

    def as_setCoinsS(self, value):
        return self.flashObject.as_setCoins(value) if self._isDAAPIInited() else None

    def as_setScreenS(self, alias):
        return self.flashObject.as_setScreen(alias) if self._isDAAPIInited() else None

    def as_setHangarMenuDataS(self, data):
        return self.flashObject.as_setHangarMenuData(data) if self._isDAAPIInited() else None

    def as_setButtonCounterS(self, btnAlias, value):
        return self.flashObject.as_setButtonCounter(btnAlias, value) if self._isDAAPIInited() else None

    def as_removeButtonCounterS(self, btnAlias):
        return self.flashObject.as_removeButtonCounter(btnAlias) if self._isDAAPIInited() else None
