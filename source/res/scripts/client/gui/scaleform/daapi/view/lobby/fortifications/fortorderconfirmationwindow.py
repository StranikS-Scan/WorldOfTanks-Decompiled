# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortOrderConfirmationWindow.py
import BigWorld
from gui.Scaleform.framework import AppRef
from gui.shared.SoundEffectsId import SoundEffectsId
from helpers import time_utils
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortOrderConfirmationWindowMeta import FortOrderConfirmationWindowMeta
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.fortifications.context import OrderCtx
from helpers import i18n

class FortOrderConfirmationWindow(View, FortOrderConfirmationWindowMeta, AbstractWindowView, FortViewHelper, AppRef):

    def __init__(self, meta, handler):
        super(FortOrderConfirmationWindow, self).__init__()
        self.meta = meta
        self.handler = handler
        self._orderID = meta.getOrderID()

    def _populate(self):
        super(FortOrderConfirmationWindow, self)._populate()
        self._prepareAndSendData()
        self.startFortListening()
        self.as_setSettingsS({'title': self.meta.getTitle(),
         'submitBtnLabel': self.meta.getSubmitButtonLabel(),
         'cancelBtnLabel': self.meta.getCancelButtonLabel()})

    def _dispose(self):
        self.stopFortListening()
        if self.meta is not None:
            self.meta.destroy()
            self.meta = None
        self.handler = self._data = None
        super(FortOrderConfirmationWindow, self)._dispose()
        return

    def _prepareAndSendData(self):
        resultData = {}
        if self._orderID:
            orderTitle = i18n.makeString(FORTIFICATIONS.orders_orderpopover_ordertype(self._orderID))
            order = self.fortCtrl.getFort().getOrder(self.UI_ORDERS_BIND.index(self._orderID))
            building = self.fortCtrl.getFort().getBuilding(order.buildingID)
            defRes = building.storage
            maxPurchase = int(defRes / order.productionCost)
            resultData = {'orderIcon': order.icon,
             'name': orderTitle,
             'description': order.description,
             'productionTime': order.productionTotalTime,
             'productionCost': order.productionCost,
             'level': order.level,
             'defaultValue': -1,
             'maxAvailableCount': min(order.maxCount - order.count, maxPurchase)}
        self.as_setDataS(resultData)

    def onWindowClose(self):
        self.destroy()

    def submit(self, count):
        self.__requestToCreate(count)

    @process
    def __requestToCreate(self, count):
        orderTypeID = self.UI_ORDERS_BIND.index(self._orderID)
        count = int(count)
        result = yield self.fortProvider.sendRequest(OrderCtx(orderTypeID, count, waitingID='fort/order/add'))
        if result:
            order = self.fortCtrl.getFort().getOrder(orderTypeID)
            if self.app.soundManager is not None:
                self.app.soundManager.playEffectSound(SoundEffectsId.FORT_ORDER_INPROGRESS)
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_ADDORDER, count=BigWorld.wg_getIntegralFormat(count), time=order.getProductionLeftTimeStr(), type=SystemMessages.SM_TYPE.Warning)
            self.destroy()
        return

    def getTimeStr(self, time):
        return time_utils.getTillTimeString(time, FORTIFICATIONS.TIME_TIMEVALUE)

    def onUpdated(self):
        self._prepareAndSendData()

    def onBuildingRemoved(self, buildingTypeID):
        order = self.fortCtrl.getFort().getOrder(self.UI_ORDERS_BIND.index(self._orderID))
        if order.buildingID == buildingTypeID:
            self.destroy()
