# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WTAbilityWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class WTAbilityWidgetMeta(BaseDAAPIComponent):

    def as_addMissileWidgetS(self):
        return self.flashObject.as_addMissileWidget() if self._isDAAPIInited() else None
