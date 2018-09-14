# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortOrdersPanelComponent.py
import itertools
import operator
from ClientFortifiedRegion import ORDER_UPDATE_REASON
from gui.shared.formatters import time_formatters
from helpers import i18n
from constants import CLAN_MEMBER_FLAGS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.SlotsPanelMeta import SlotsPanelMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.utils.functions import makeTooltip

class FortOrdersPanelComponent(SlotsPanelMeta, FortViewHelper):
    SLOTS_PROPS = {'slotsCount': -1,
     'groupCount': -1,
     'slotWidth': 50,
     'paddings': 64,
     'groupPadding': 18,
     'ySlotPosition': 5,
     'offsetSlot': -7,
     'useOnlyLeftBtn': True}

    def _populate(self):
        super(FortOrdersPanelComponent, self)._populate()
        self.startFortListening()
        self._buildList()

    def _dispose(self):
        self.stopFortListening()
        super(FortOrdersPanelComponent, self)._dispose()

    def _buildList(self):
        result = filter(None, map(self._buildData, self.BUILDINGS))
        totalDifferentTypes = tuple(itertools.groupby(result, key=operator.itemgetter('type')))
        propsData = dict(self.SLOTS_PROPS)
        if result:
            propsData['slotsCount'] = len(result)
        if totalDifferentTypes:
            propsData['groupCount'] = len(totalDifferentTypes) + 1
        self.as_setPanelPropsS(propsData)
        self.as_setSlotsS(result)
        return

    def _buildData(self, buildingID, isRecharged = False):
        orderID = self.fortCtrl.getFort().getBuildingOrder(buildingID)
        if orderID is None:
            return
        else:
            orderUID = self.getOrderUIDbyID(orderID)
            if orderUID == self.FORT_UNKNOWN:
                return
            builidngUID = self.getBuildingUIDbyID(buildingID)
            order = self.fortCtrl.getFort().getOrder(orderID)
            return {'fortOrderTypeID': order.orderID,
             'group': order.group,
             'type': order.type,
             'enabled': order.hasBuilding,
             'id': orderUID,
             'icon': order.icon,
             'count': order.count,
             'level': order.level,
             'inProgress': order.inProgress,
             'buildingStr': i18n.makeString(FORTIFICATIONS.buildings_buildingname(builidngUID)),
             'inCooldown': order.inCooldown,
             'cooldownPercent': order.getCooldownAsPercent(),
             'leftTime': order.getUsageLeftTime(),
             'isPermanent': order.isPermanent,
             'isRecharged': isRecharged,
             'isDischarging': True}

    def getSlotTooltipBody(self, orderID):
        header = i18n.makeString(FORTIFICATIONS.orders_orderpopover_ordertype(orderID))
        note = None
        fort = self.fortCtrl.getFort()
        order = fort.getOrder(self.getOrderIDbyUID(orderID))
        buildingDescr = fort.getBuilding(order.buildingID)
        if order.hasBuilding:
            description = ''
            ordersListStr = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_CLANPERMISSIONS)
            if order.inCooldown:
                description = self._getCooldownInfo(order)
            elif order.count > 0:
                if self._isProductionInPause(buildingDescr):
                    description = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERSPANEL_CANTUSEORDER)
                    description += '\n' + i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPROCESS_INFO)
                elif not order.isPermanent and not order.isCompatible and fort.hasActivatedContinualOrders():
                    description = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERSPANEL_CANTUSEORDER)
                else:
                    description = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_ORDERISREADY)
                if not self._canGiveOrder():
                    description += '\n' + ordersListStr
            else:
                if not order.inProgress:
                    description = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_CREATEORDER)
                if not self._canGiveOrder():
                    description = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_USEORDERBTN_NOORDERS)
                    description += '\n' + ordersListStr
            if order.inProgress:
                if self._isProductionInPause(buildingDescr):
                    pauseText = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPROCESS_INPAUSE)
                    if len(description) > 0:
                        description += '\n' + pauseText
                    else:
                        description = pauseText
                    description += '\n' + i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPROCESS_INFO)
                else:
                    description = self._getProgressInfo(description, order)
        else:
            buildingStr = i18n.makeString(FORTIFICATIONS.buildings_buildingname(self.getBuildingUIDbyID(order.buildingID)))
            description = i18n.makeString(FORTIFICATIONS.ORDERS_ORDERPOPOVER_ORDERNOTREADY, building=buildingStr)
        return makeTooltip(header, description, note)

    def _canGiveOrder(self):
        return g_clanCache.clanRole in (CLAN_MEMBER_FLAGS.LEADER, CLAN_MEMBER_FLAGS.VICE_LEADER)

    def _getRolesStr(self):
        leader = i18n.makeString(FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_LEADER)
        vice_leader = i18n.makeString(FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_VICE_LEADER)
        return leader + ', ' + vice_leader

    def _getProgressInfo(self, description, order):
        createdTime = order.getProductionLeftTime()
        createdTimeStr = time_formatters.getTimeDurationStr(createdTime)
        productionCountStr = ''
        if order.productionCount > 1:
            productionCountStr = ' (x%d)' % order.productionCount
        text = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_INPROGRESS_TEXT, count=productionCountStr)
        text += '\n' + i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_INPROGRESS_TIMELEFT, timeLeft=createdTimeStr)
        if len(description) > 0:
            description += '\n' + text
        else:
            description = text
        return description

    def _getCooldownInfo(self, order):
        if not order.isPermanent:
            leftTime = order.getUsageLeftTime()
            leftTimeStr = time_formatters.getTimeDurationStr(leftTime)
            return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_PROGRESSBAR_TIMELEFT, timeLeft=leftTimeStr)
        else:
            return i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPOPOVER_INDEFENSIVE)

    def onOrderChanged(self, orderTypeID, reason):
        g_fortSoundController.playReadyOrder()
        buildingTypeID, _, _, _ = self.fortCtrl.getFort().getOrderData(orderTypeID)
        self.as_updateSlotS(self._buildData(buildingTypeID, reason == ORDER_UPDATE_REASON.ADDED))

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        data = self._buildData(buildingTypeID)
        if data is not None:
            self.as_updateSlotS(data)
        return

    def onConsumablesChanged(self, unitMgrID):
        self._buildList()
