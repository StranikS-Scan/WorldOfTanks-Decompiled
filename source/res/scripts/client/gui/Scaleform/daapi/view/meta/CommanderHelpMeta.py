# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CommanderHelpMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CommanderHelpMeta(BaseDAAPIComponent):

    def onOrderButtonClicked(self, keyCode):
        self._printOverrideError('onOrderButtonClicked')

    def as_setOrderItemsS(self, orderItems):
        return self.flashObject.as_setOrderItems(orderItems) if self._isDAAPIInited() else None

    def as_updateOrderStateS(self, idx, isActive, isPressed, isDisabled):
        return self.flashObject.as_updateOrderState(idx, isActive, isPressed, isDisabled) if self._isDAAPIInited() else None
