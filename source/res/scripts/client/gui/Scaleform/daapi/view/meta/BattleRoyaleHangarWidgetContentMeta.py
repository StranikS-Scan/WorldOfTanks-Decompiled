# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleHangarWidgetContentMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class BattleRoyaleHangarWidgetContentMeta(InjectComponentAdaptor):

    def as_onWrapperInitializedS(self):
        return self.flashObject.as_onWrapperInitialized() if self._isDAAPIInited() else None
