# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortOrderPopover.py
import constants
from adisp import process
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.fortifications.ConfirmOrderDialogMeta import BuyOrderDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortOrderPopoverMeta import FortOrderPopoverMeta
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events, g_eventsCache
from gui.shared.fortifications.context import OrderCtx
from gui.shared.utils.functions import makeTooltip
from helpers import i18n

class FortOrderPopover(View, FortOrderPopoverMeta, SmartPopOverView, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(FortOrderPopover, self).__init__()
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
        return self.app.utilsManager.textManager.getTimeDurationStr(time)

    def _getFormattedLeftTime(self, order):
        if order.inCooldown:
            if not order.isPermanent:
                secondsLeft = order.getUsageLeftTime()
                return self._getFormattedTimeStr(secondsLeft)
            else:
                nextBattle = i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_NEXTBATTLE)
                return self.app.utilsManager.textManager.getText(TextType.SUCCESS_TEXT, nextBattle)
        return ''

    def _getBuildingStr(self, order):
        buildingID = self.UI_BUILDINGS_BIND[order.buildingID]
        building = i18n.makeString(FORTIFICATIONS.buildings_buildingname(buildingID))
        hasBuilding = order.hasBuilding
        if not hasBuilding:
            return self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, building)
        return building

    def _getCountStr(self, order):
        count = order.count
        total = ' / %d' % order.maxCount
        countColor = TextType.NEUTRAL_TEXT if count != 0 else TextType.STANDARD_TEXT
        return self.app.utilsManager.textManager.concatStyles(((countColor, count), (TextType.STANDARD_TEXT, total)))

    def _canGiveOrder(self):
        return self.fortCtrl.getPermissions().canActivateOrder()

    def _canCreateOrder(self, order):
        isEnoughMoney = False
        building = self.fortCtrl.getFort().getBuilding(order.buildingID)
        if order.hasBuilding:
            defRes = building.storage
            isEnoughMoney = bool(defRes >= order.productionCost)
        return self.fortCtrl.getPermissions().canAddOrder() and order.hasBuilding and isEnoughMoney and not order.inProgress and not self._isProductionInPause(building)

    def _prepareAndSetData(self):
        orderID = self.UI_ORDERS_BIND.index(self._orderID)
        order = self.fortCtrl.getFort().getOrder(orderID)
        building = self.fortCtrl.getFort().getBuilding(order.buildingID)
        canActivateOrder, _ = self.fortCtrl.getLimits().canActivateOrder(orderID)
        isBtnDisabled = not canActivateOrder or self._isProductionInPause(building)
        data = {'title': self._getTitle(),
         'levelStr': self._getLevelStr(order.level),
         'description': self._getOrderDescription(order),
         'effectTimeStr': self._getEffectTimeStr(order),
         'leftTimeStr': self._getFormattedLeftTime(order),
         'productionTime': self._getFormattedTimeStr(order.productionTotalTime),
         'buildingStr': self._getBuildingStr(order),
         'productionCost': fort_formatters.getDefRes(order.productionCost, True),
         'producedAmount': self._getCountStr(order),
         'icon': order.bigIcon,
         'canUseOrder': self._canGiveOrder(),
         'canCreateOrder': self._canCreateOrder(order),
         'inCooldown': order.inCooldown,
         'effectTime': order.effectTime,
         'leftTime': order.getUsageLeftTime(),
         'useBtnTooltip': self._getUseBtnTooltip(order, building, isBtnDisabled),
         'hasBuilding': order.hasBuilding,
         'isPermanent': order.isPermanent,
         'questID': self._getQuestID(order),
         'showLinkBtn': self._showLinkBtn(order),
         'showAlertIcon': self._showOrderAlertIcon(order)}
        self.as_setInitDataS(data)
        self.as_disableOrderS(isBtnDisabled)

    @classmethod
    def _showLinkBtn(cls, order):
        return order.isSpecialMission and order.inCooldown and cls.__getFortQuest() is not None

    @classmethod
    def _getQuestID(cls, order):
        if order.isSpecialMission and order.inCooldown:
            fortQuest = cls.__getFortQuest()
            if fortQuest is not None:
                return fortQuest.getID()
        return

    def _getOrderDescription(self, order):
        if order.isSpecialMission:
            if order.inCooldown:
                textsStyle = (TextType.NEUTRAL_TEXT, TextType.MAIN_TEXT)
                award = i18n.makeString(FORTIFICATIONS.ORDERS_SPECIALMISSION_AWARD) + ' '
                serverData = self.__getFortQuestBonusesStr()
                serverData += '\n' + i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_SPECIALMISSION_SHORTDESCR)
                return self.app.utilsManager.textManager.concatStyles(((textsStyle[0], award), (textsStyle[1], serverData)))
            else:
                return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_SPECIALMISSION_DESCRIPTION))
        else:
            return order.description

    def _getEffectTimeStr(self, order):
        if not order.isPermanent:
            return self._getFormattedTimeStr(order.effectTime)
        else:
            return i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_INDEFENSIVE)

    def _populate(self):
        super(FortOrderPopover, self)._populate()
        self.startFortListening()
        g_eventsCache.onSyncCompleted += self.onEventsSyncCompleted
        self._prepareAndSetData()

    def _dispose(self):
        g_eventsCache.onSyncCompleted -= self.onEventsSyncCompleted
        self.stopFortListening()
        super(FortOrderPopover, self)._dispose()

    def _getUseBtnTooltip(self, order, buildingDescr, isDisabled):
        hasBuilding = order.hasBuilding
        buildingID = self.UI_BUILDINGS_BIND[order.buildingID]
        buildingStr = i18n.makeString(FORTIFICATIONS.buildings_buildingname(buildingID))
        body = None
        note = None
        if not isDisabled:
            header = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_HEADER
            body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_DESCRIPTION
        else:
            header = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_CANTUSE_HEADER
            if not order.isSupported:
                body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOTAVAILABLE
            elif not hasBuilding:
                body = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOBUILDING, building=buildingStr)
            elif not order.isPermanent and self.fortCtrl.getFort().hasActivatedContinualOrders():
                body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_WASUSED
            elif order.isPermanent and order.inCooldown:
                body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_WASUSED
            elif order.isPermanent and not self.fortCtrl.getFort().isDefenceHourEnabled():
                body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_DEFENCEHOURDISABLED
            elif order.count < 1:
                body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOORDERS
            elif self._isBuildingDamaged(buildingDescr) or self._isBaseBuildingDamaged() or self._isFortFrozen():
                body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_CANTUSE_BODY
        return makeTooltip(header, body, note)

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
            g_fortSoundController.playActivateOrder(self._orderID)

    def getLeftTime(self):
        order = self.fortCtrl.getFort().getOrder(self.UI_ORDERS_BIND.index(self._orderID))
        return order.getUsageLeftTime()

    def getLeftTimeStr(self):
        order = self.fortCtrl.getFort().getOrder(self.UI_ORDERS_BIND.index(self._orderID))
        return self._getFormattedLeftTime(order)

    def getLeftTimeTooltip(self):
        order = self.fortCtrl.getFort().getOrder(self.UI_ORDERS_BIND.index(self._orderID))
        if order.inCooldown:
            if order.isPermanent:
                return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_PERMANENTORDER_INFO)
            else:
                leftTimeStr = self.app.utilsManager.textManager.getTimeDurationStr(order.getUsageLeftTime())
                return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_PROGRESSBAR_TIMELEFT, timeLeft=leftTimeStr)
        return ''

    def onUpdated(self, isFullUpdate):
        self._updateData()

    def onEventsSyncCompleted(self):
        self._prepareAndSetData()

    def openQuest(self, questID):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_EVENTS_WINDOW, {'eventID': questID}))

    @classmethod
    def __getFortQuest(cls):
        fortQuests = g_eventsCache.getQuests(lambda q: q.getType() == constants.EVENT_TYPE.FORT_QUEST)
        if len(fortQuests):
            return fortQuests.values()[0]
        else:
            return None

    @classmethod
    def __getFortQuestBonusesStr(cls):
        result = []
        quest = cls.__getFortQuest()
        if quest is not None:
            for b in quest.getBonuses():
                if b.isShowInGUI():
                    result.append(b.format())

        return ', '.join(result)
