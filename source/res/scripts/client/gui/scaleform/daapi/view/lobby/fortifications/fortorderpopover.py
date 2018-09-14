# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortOrderPopover.py
import constants
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.fortifications.ConfirmOrderDialogMeta import BuyOrderDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortOrderPopoverMeta import FortOrderPopoverMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events
from gui.server_events import g_eventsCache, events_dispatcher as quests_events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, time_formatters
from gui.shared.fortifications.context import OrderCtx
from gui.shared.utils.functions import makeTooltip
from helpers import i18n

class FortOrderPopover(FortOrderPopoverMeta, FortViewHelper):

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

    def _getFormattedLeftTime(self, order):
        if order.inCooldown:
            if not order.isPermanent:
                secondsLeft = order.getUsageLeftTime()
                return time_formatters.getTimeDurationStr(secondsLeft)
            else:
                nextBattle = i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_NEXTBATTLE)
                return text_styles.success(nextBattle)
        return ''

    def _getBuildingStr(self, order):
        buildingID = self.getBuildingUIDbyID(order.buildingID)
        building = i18n.makeString(FORTIFICATIONS.buildings_buildingname(buildingID))
        hasBuilding = order.hasBuilding
        if not hasBuilding:
            return text_styles.error(building)
        return building

    def _getCountStr(self, order):
        count = order.count
        if count > 0:
            result = text_styles.neutral(count)
        else:
            result = text_styles.standard(count)
        return result

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
        orderID = self.getOrderIDbyUID(self._orderID)
        order = self.fortCtrl.getFort().getOrder(orderID)
        building = self.fortCtrl.getFort().getBuilding(order.buildingID)
        canActivateOrder, _ = self.fortCtrl.getLimits().canActivateOrder(orderID)
        isBtnDisabled = not canActivateOrder or self._isProductionInPause(building)
        showAlertIcon, alertIconTooltip = self._showOrderAlertIcon(order)
        data = {'title': self._getTitle(),
         'levelStr': self._getLevelStr(order.level),
         'description': self._getOrderDescription(order),
         'effectTimeStr': self._getEffectTimeStr(order),
         'leftTimeStr': '' if order.isConsumable else self._getFormattedLeftTime(order),
         'productionTime': time_formatters.getTimeDurationStr(order.productionTotalTime),
         'buildingStr': self._getBuildingStr(order),
         'productionCost': fort_formatters.getDefRes(order.productionCost, True),
         'producedAmount': self._getCountStr(order),
         'icon': order.bigIcon,
         'canUseOrder': False if order.isConsumable else self._canGiveOrder(),
         'canCreateOrder': self._canCreateOrder(order),
         'inCooldown': False if order.isConsumable else order.inCooldown,
         'effectTime': order.effectTime,
         'leftTime': order.getUsageLeftTime(),
         'useBtnTooltip': self._getUseBtnTooltip(order, building, isBtnDisabled),
         'hasBuilding': order.hasBuilding,
         'isPermanent': order.isPermanent,
         'questID': self._getQuestID(order),
         'showLinkBtn': self._showLinkBtn(order),
         'showAlertIcon': showAlertIcon,
         'alertIconTooltip': alertIconTooltip,
         'showDetailsBtn': order.isConsumable}
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
                award = i18n.makeString(FORTIFICATIONS.ORDERS_SPECIALMISSION_AWARD) + ' '
                serverData = self.__getFortQuestBonusesStr()
                serverData += '\n' + i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_SPECIALMISSION_SHORTDESCR)
                return ''.join((text_styles.neutral(award), text_styles.main(serverData)))
            else:
                return text_styles.main(i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_SPECIALMISSION_DESCRIPTION))
        else:
            return order.description

    def _getEffectTimeStr(self, order):
        if order.isPermanent:
            return i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_INDEFENSIVE)
        elif order.isConsumable:
            return i18n.makeString('#fortifications:Orders/orderPopover/battleConsumable')
        else:
            return time_formatters.getTimeDurationStr(order.effectTime)

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
        buildingID = self.getBuildingUIDbyID(order.buildingID)
        buildingStr = i18n.makeString(FORTIFICATIONS.buildings_buildingname(buildingID))
        body = None
        note = None
        if not isDisabled:
            header = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_HEADER
            body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_DESCRIPTION
        else:
            header = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_CANTUSE_HEADER
            fort = self.fortCtrl.getFort()
            if not order.isSupported:
                body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOTAVAILABLE
            elif not hasBuilding:
                body = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOBUILDING, building=buildingStr)
            elif order.inCooldown:
                body = TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_WASUSED
            elif not order.isCompatible and fort.hasActivatedContinualOrders():
                body = TOOLTIPS.FORTIFICATION_ORDERSPANEL_CANTUSEORDER
            elif order.isPermanent and not fort.isDefenceHourEnabled():
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
        orderTypeID = self.getOrderIDbyUID(self._orderID)
        result = yield self.fortProvider.sendRequest(OrderCtx(orderTypeID, isAdd=False, waitingID='fort/order/activate'))
        if result:
            g_fortSoundController.playActivateOrder(self._orderID)

    def getLeftTime(self):
        order = self.fortCtrl.getFort().getOrder(self.getOrderIDbyUID(self._orderID))
        return order.getUsageLeftTime()

    def getLeftTimeStr(self):
        order = self.fortCtrl.getFort().getOrder(self.getOrderIDbyUID(self._orderID))
        return self._getFormattedLeftTime(order)

    def getLeftTimeTooltip(self):
        order = self.fortCtrl.getFort().getOrder(self.getOrderIDbyUID(self._orderID))
        if order.inCooldown:
            if order.isPermanent:
                return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_PERMANENTORDER_INFO)
            else:
                leftTimeStr = time_formatters.getTimeDurationStr(order.getUsageLeftTime())
                return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_PROGRESSBAR_TIMELEFT, timeLeft=leftTimeStr)
        return ''

    def onUpdated(self, isFullUpdate):
        self._updateData()

    def onEventsSyncCompleted(self):
        self._prepareAndSetData()

    def openQuest(self, questID):
        return quests_events.showEventsWindow(questID, constants.EVENT_TYPE.FORT_QUEST)

    def openOrderDetailsWindow(self):
        orderID = self.getOrderIDbyUID(self._orderID)
        order = self.fortCtrl.getFort().getOrder(orderID)
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, ctx={'orderID': orderID,
         'orderLevel': order.level}), scope=EVENT_BUS_SCOPE.LOBBY)

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
                formattedValue = b.format()
                if b.isShowInGUI() and formattedValue:
                    result.append(formattedValue)

        return ', '.join(result)
