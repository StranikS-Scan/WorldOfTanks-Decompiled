# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortOrderPopover.py
from adisp import process
from constants import CLAN_MEMBER_FLAGS
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications.ConfirmOrderDialogMeta import BuyOrderDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortOrderPopoverMeta import FortOrderPopoverMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications.context import OrderCtx
from helpers import i18n

class FortOrderPopover(View, FortOrderPopoverMeta, SmartPopOverView, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(FortOrderPopover, self).__init__()
        self._setKeyPoint(ctx.get('inXcoordinate'), ctx.get('inYcoordinate'))
        self._orderID = str(ctx.get('data'))

    def _getTitle(self):
        orderTitle = ''
        if self._orderID:
            orderTitle = i18n.makeString(FORTIFICATIONS.orders_orderpopover_ordertype(self._orderID))
        return orderTitle

    def _getLevelStr(self, level):
        formatedLvl = fort_formatters.getTextLevel(level)
        return i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_LEVELSLBL, orderLevel=formatedLvl)

    def _getFormattedTimeStr(self, time):
        return fort_text.getTimeDurationStr(time)

    def _getFormattedLeftTime(self, order):
        if order.inCooldown and not order.isPermanent:
            secondsLeft = order.getUsageLeftTime()
            return self._getFormattedTimeStr(secondsLeft)
        return ''

    def _getBuildingStr(self, order):
        buildingID = self.UI_BUILDINGS_BIND[order.buildingID]
        building = i18n.makeString(FORTIFICATIONS.buildings_buildingname(buildingID))
        hasBuilding = order.hasBuilding
        if not hasBuilding:
            return fort_text.getText(fort_text.ERROR_TEXT, building)
        return building

    def _getCountStr(self, order):
        count = order.count
        total = ' / %d' % order.maxCount
        countColor = fort_text.NEUTRAL_TEXT if count != 0 else fort_text.STANDARD_TEXT
        return fort_text.concatStyles(((countColor, count), (fort_text.STANDARD_TEXT, total)))

    def _canGiveOrder(self):
        return self.fortCtrl.getPermissions().canActivateOrder()

    def _canCreateOrder(self, order):
        isEnoughMoney = False
        if order.hasBuilding:
            building = self.fortCtrl.getFort().getBuilding(order.buildingID)
            defRes = building.storage
            isEnoughMoney = bool(defRes >= order.productionCost)
        return self.fortCtrl.getPermissions().canAddOrder() and order.hasBuilding and isEnoughMoney and not order.inProgress

    def _prepareAndSetData(self):
        orderID = self.UI_ORDERS_BIND.index(self._orderID)
        order = self.fortCtrl.getFort().getOrder(orderID)
        data = {'title': self._getTitle(),
         'levelStr': self._getLevelStr(order.level),
         'description': order.description,
         'effectTimeStr': self._getEffectTimeStr(order),
         'leftTimeStr': self._getFormattedLeftTime(order),
         'productionTime': self._getFormattedTimeStr(order.productionTotalTime),
         'buildingStr': self._getBuildingStr(order),
         'productionCost': fort_formatters.getDefRes(order.productionCost, True),
         'producedAmount': self._getCountStr(order),
         'orderID': self._orderID,
         'canUseOrder': self._canGiveOrder(),
         'canCreateOrder': self._canCreateOrder(order),
         'inCooldown': order.inCooldown,
         'effectTime': order.effectTime,
         'leftTime': order.getUsageLeftTime(),
         'useBtnTooltip': self._getUseBtnTooltip(order),
         'hasBuilding': order.hasBuilding,
         'isPermanent': order.isPermanent}
        isBtnDisabled, _ = self.fortCtrl.getLimits().canActivateOrder(orderID)
        self.as_setInitDataS(data)
        self.as_disableOrderS(isBtnDisabled)

    def _getEffectTimeStr(self, order):
        if not order.isPermanent:
            return self._getFormattedTimeStr(order.effectTime)
        else:
            return i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_INDEFENSIVE)

    def _populate(self):
        super(FortOrderPopover, self)._populate()
        self.startFortListening()
        self._prepareAndSetData()

    def _dispose(self):
        self.stopFortListening()
        super(FortOrderPopover, self)._dispose()

    def _getUseBtnTooltip(self, order):
        hasBuilding = order.hasBuilding
        buildingID = self.UI_BUILDINGS_BIND[order.buildingID]
        buildingStr = i18n.makeString(FORTIFICATIONS.buildings_buildingname(buildingID))
        if order.isPermanent:
            return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOTAVAILABLE)
        if not hasBuilding:
            return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOBUILDING, building=buildingStr)
        if self.fortCtrl.getFort().hasActivatedOrders():
            return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_WASUSED)
        if order.count < 1:
            return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOORDERS)
        return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_DESCRIPTION)

    def onWindowClose(self):
        self.destroy()

    def requestForCreateOrder(self):
        DialogsInterface.showDialog(BuyOrderDialogMeta(self._orderID), None)
        self.onWindowClose()
        return

    def _updateData(self):
        self._prepareAndSetData()

    def requestForUseOrder(self):
        self.__requestToUse()

    @process
    def __requestToUse(self):
        orderTypeID = self.UI_ORDERS_BIND.index(self._orderID)
        result = yield self.fortProvider.sendRequest(OrderCtx(orderTypeID, isAdd=False, waitingID='fort/order/activate'))
        if result:
            if self.app.soundManager is not None:
                self.app.soundManager.playEffectSound('activate_' + self._orderID)
        return

    def getLeftTime(self):
        order = self.fortCtrl.getFort().getOrder(self.UI_ORDERS_BIND.index(self._orderID))
        return order.getUsageLeftTime()

    def getLeftTimeStr(self):
        order = self.fortCtrl.getFort().getOrder(self.UI_ORDERS_BIND.index(self._orderID))
        return self._getFormattedLeftTime(order)

    def getLeftTimeTooltip(self):
        order = self.fortCtrl.getFort().getOrder(self.UI_ORDERS_BIND.index(self._orderID))
        if order.inCooldown and not order.isPermanent:
            leftTimeStr = fort_text.getTimeDurationStr(order.getUsageLeftTime())
            return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_PROGRESSBAR_TIMELEFT, timeLeft=leftTimeStr)
        return ''

    def onUpdated(self):
        self._updateData()
