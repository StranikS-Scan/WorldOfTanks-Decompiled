# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/OrdersPanelMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class OrdersPanelMeta(DAAPIModule):

    def getOrderTooltipBody(self, orderID):
        self._printOverrideError('getOrderTooltipBody')

    def as_setPanelPropsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setPanelProps(data)

    def as_setOrdersS(self, orders):
        if self._isDAAPIInited():
            return self.flashObject.as_setOrders(orders)

    def as_updateOrderS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateOrder(data)
