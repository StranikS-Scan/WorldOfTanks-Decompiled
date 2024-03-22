# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleTypeSelectorMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class BattleTypeSelectorMeta(InjectComponentAdaptor):

    def startFirstShowAnimation(self):
        self._printOverrideError('startFirstShowAnimation')

    def startIdleAnimation(self):
        self._printOverrideError('startIdleAnimation')

    def setIsVisibleS(self, value):
        return self.flashObject.setIsVisible(value) if self._isDAAPIInited() else None
